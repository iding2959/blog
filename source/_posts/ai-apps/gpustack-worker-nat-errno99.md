---
title: GPUStack 模型启动报 Errno 99：NAT 后面 worker 的地址绑定陷阱
date: 2026-07-23 10:00:00
description: GPUStack worker 注册正常但运行模型报 OSError Errno 99 Cannot assign requested address：分析 vLLM --host 的来源，用 --advertise-address + pfSense DNAT 解决 NAT 后面 worker 的地址问题，并给出多 worker 的端口段规划与转发规则。
keywords: GPUStack, vLLM, Errno 99, NAT, pfSense, worker 地址
categories: AI 应用
tags:
  - GPUStack
  - vLLM
  - Docker
  - PVE
  - LLM
---

## 概述

GPUStack 里加了一台位于防火墙 NAT 后面的 worker，注册一切正常，但部署模型必挂 `OSError: [Errno 99] Cannot assign requested address`。本文记录从报错到根因（vLLM 的 `--host` 绑了防火墙地址）、再到正确配置（`--worker-ip` + `--advertise-address`）的完整过程，最后附上多 worker 场景的端口段规划方法。

## 现象

GPUStack 集群里新加了一台 worker，在 Web 控制台看一切正常：worker 在线、`READY`、GPU 也识别到了。但一部署模型就挂，日志最后一行是：

```text
(APIServer pid=1)   File "/usr/local/lib/python3.12/dist-packages/vllm/entrypoints/openai/api_server.py", line 525, in create_server_socket
(APIServer pid=1)     sock.bind(addr)
(APIServer pid=1) OSError: [Errno 99] Cannot assign requested address
```

往前翻，vLLM 的启动命令是 GPUStack 自动拼的：

```text
vllm serve /mnt/models/HY/Hy-MT2-7B-FP8 --max-model-len 8192 \
  --host 192.168.0.158 --port 40040 --served-model-name hy-mt2-7b-fp8
```

`Cannot assign requested address` 最典型的含义就是：**要绑定的 IP 不在本机的网卡上**。而这里的 `192.168.0.158` 确实不在 worker 机器上——它是防火墙（pfSense）的地址。

## 环境拓扑

```text
GPUStack master  192.168.0.242  (gpustack-server 容器, v2.2.3)
      │
      │  192.168.0.0/24
      │
pfSense (VM)     WAN 192.168.0.158 ─┐
                 LAN 192.168.1.1    │
      │                             │
      └── worker VM 192.168.1.202 ──┘   默认网关 192.168.1.1
            gpustack-worker 容器（network_mode: host）
            L40 GPU（PCI 直通）
```

worker 在一台 PVE 上，处在 pfSense 后的 `192.168.1.0/24` 内网。master 在 `192.168.0.0/24`，两边通过 pfSense 互通。

## 根因：`--host` 来自 worker 自己上报的地址

GPUStack 给 vLLM 拼命令行时，绑定地址用的不是用户配置，而是 worker 记录里的 `ip` 字段。翻源码（v2.2.3）：

```python
# gpustack/worker/backends/vllm.py
arguments, ("--host", self._worker.ip), ("--port", str(port))
```

而 worker 的注册参数是：

```text
--server-url=http://192.168.0.242/ --worker-ip=192.168.0.158 --proxy-mode=direct
```

也就是说：当初部署 worker 时，`--worker-ip` 填了 pfSense 的 WAN 地址（大概是想让 master 从这个地址访问 worker）。结果 GPUStack 认为"worker 的 IP 就是 0.158"，于是：

1. vLLM 被要求绑 `192.168.0.158:40040`；
2. worker 容器是 `network_mode: host`，直接继承宿主机网络栈；
3. 宿主机只有 `192.168.1.202`，没有 `0.158`；
4. `bind()` 失败 → `Errno 99`。

数据库里也能印证：

```sql
select id,name,ip,advertise_address,state from workers;
--  4 | gpustack-worker-202 | 192.168.0.158 | 192.168.0.158 | READY
```

**注册成功 ≠ 能跑模型**：心跳是 worker 主动出站上报的，走 NAT 出去完全没问题；但模型容器要绑死一个本机地址，这个地址一旦填错就必然失败。

## 定位过程

### 1. 看 worker 容器怎么起的

```bash
docker inspect gpustack-worker-202 --format '{{.HostConfig.NetworkMode}} {{.Config.Cmd}}'
# host [--server-url=http://192.168.0.242/ --worker-ip=192.168.0.158 --proxy-mode=direct]
```

`host` 网络确认了"容器里没有独立网卡，绑定就是绑定宿主机网卡"。

### 2. 看 worker 上实际有哪些地址

```bash
ip -4 addr show | grep "inet "
# inet 192.168.1.202/24 brd 192.168.1.255 scope global enp6s18
# inet 172.17.0.1/16 ...（docker bridge）
```

只有 `192.168.1.202`，没有 `192.168.0.158`。

### 3. 看实例记录

```sql
select id,name,worker_ip,port,state from model_instances;
-- 52 | hy-mt2-7b-fp8-2p02n | 192.168.0.158 | 40040 | STARTING
```

实例的 `worker_ip` 是调度时从 worker 记录复制过来的（`scheduler.py` 里 `model_instance.worker_ip = candidate.worker.ip`），所以**光改 worker 还不够，旧实例不会自动更新**。

## 第一次尝试：给 master 加静态路由（可行但不必要）

master 的默认网关是 `192.168.0.1`，并不认识 `192.168.1.0/24`。当时为了先跑通，在 master 上临时加了一条：

```bash
ip route add 192.168.1.0/24 via 192.168.0.158
```

然后让 worker 用真实地址注册：

```bash
--worker-ip=192.168.1.202
```

再删掉旧实例让 controller 重建，模型确实起来了：vLLM 绑 `192.168.1.202:40019`，master 通过路由直连 `1.202:40019` 一切正常。

但这条路由只是"能跑"，并没有回答一个问题：**防火墙那边是不是本来就有更好的办法？**

## 最终方案：pfSense DNAT + `--advertise-address`

登录 pfSense 把配置导出（`Diagnostics → Backup & Restore` 下载 `config.xml`），发现里面早就有一堆到 worker 的端口转发：

| WAN 端口（192.168.0.158） | 内部目标 | 用途 |
| --- | --- | --- |
| 10150 | 192.168.1.202:10150 | worker API（`healthz`） |
| 10151 | 192.168.1.202:10151 | worker 指标 |
| 30000-60000 | 192.168.1.202:30000 | **整段 1:1 映射**，覆盖 GPUStack 动态分配的实例端口 |
| 20020 | 192.168.1.202:22 | SSH |
| 18443 / 15000 / 15021 / 15090 / 9876 … | 同名端口 | 其他服务 |

也就是说，管理员原本的设计就是"master 走 `192.168.0.158:<端口>` 访问 worker"。问题只在于 worker 把**外部地址**当成了**绑定地址**。

GPUStack 正好为这种场景提供了两个独立参数：

| 参数 | 含义 | 本例取值 |
| --- | --- | --- |
| `--worker-ip` | 本机地址，给容器/推理引擎绑定用 | `192.168.1.202` |
| `--advertise-address` | 对外广播地址，给 server 访问用 | `192.168.0.158` |

最终 `docker-compose` 配置（省略无关项）：

```yaml
services:
  gpustack-worker:
    image: gpustack/gpustack:v2.2.3
    container_name: gpustack-worker-202
    environment:
      GPUSTACK_TOKEN: <集群 Token>
    command:
      - --server-url=http://192.168.0.242/
      - --worker-ip=192.168.1.202        # 绑定用，必须是本机地址
      - --advertise-address=192.168.0.158 # 对外用，pfSense 把 worker 的端口 DNAT 到这里
      - --proxy-mode=direct
    restart: unless-stopped
    privileged: true
    network_mode: host
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - gpustack-data:/var/lib/gpustack
      - /mnt/models:/mnt/models
    runtime: nvidia
```

改完 `docker compose up -d` 重建 worker，数据库里的记录变成：

```sql
select id,name,ip,advertise_address,state from workers;
--  4 | gpustack-worker-202 | 192.168.1.202 | 192.168.0.158 | READY
```

### 实例必须重建

这是容易漏的一步：实例的 `worker_advertise_address` 是**调度那一刻**从 worker 复制过来的：

```python
model_instance.worker_ip = candidate.worker.ip
model_instance.worker_advertise_address = candidate.worker.advertise_address
```

已有的实例不会跟着 worker 记录自动更新，所以要在控制台把实例删掉，让 controller 按 `replicas` 重新拉起。新实例拿到 `worker_advertise_address=192.168.0.158` 后，master 访问它就会走 pfSense 的转发，不再需要任何路由。

## 验证

模型起来后，先从 master 直接访问 pfSense 的转发地址（端口以实例实际分配为准）：

```bash
curl -s http://192.168.0.158:40050/v1/models | jq '.data[].id'
# "hy-mt2-7b-fp8"
```

再通过 GPUStack 的 OpenAI 兼容接口发一次请求（需要带 API Key，或复用登录后的会话 Cookie）：

```bash
curl -s http://192.168.0.242/v1-openai/chat/completions \
  -H 'Authorization: Bearer <API_KEY>' \
  -H 'Content-Type: application/json' \
  -d '{"model":"hy-mt2-7b-fp8","messages":[{"role":"user","content":"你好"}],"max_tokens":40}'
```

确认实例状态：

```bash
curl -s -H "Cookie: gpustack_session=$TOKEN" \
  http://192.168.0.242/v2/model-instances | jq '.items[] | {name,state,port,workerIp}'
```

返回正常、实例状态 `RUNNING` 后，master 上的静态路由和 systemd unit 一并撤掉。

## 延伸：多 worker 时怎么规划端口段

上面是一台 worker 的场景，pfSense 把 `30000-60000` 整段转给一台机器就够用。一旦同一台 pfSense 后面接多台 worker，**同一个 WAN IP 的同一个端口只能指向一台机器**，就必须把端口段拆开分配。这一节适用于 WAN 只有单个 IP 的情况；如果 WAN 能再加地址，也可以走后面的 VIP 方案。

### 端口相关参数

| 参数 | 默认值 | 作用 |
| --- | --- | --- |
| `--worker-port` | `10150` | worker API（master 健康检查、代理入口） |
| `--worker-metrics-port` | `10151` | 指标端口（Prometheus 抓取） |
| `--service-port-range` | `40000-40063`（64 个） | 模型实例端口，worker 在段内随机挑空闲端口，绑在 `worker_ip` 上 |
| `--ray-port-range` | `41000-41999` | 分布式 vLLM（Ray）使用 |

端口由每个 worker 自己分配，在段内**随机**取（等价于 `get_free_port(port_range, host=worker_ip)`），既不顺序递增，也不跨 worker 协调——所以两个 worker 用同一段时，外部根本没法判断某个端口属于谁。

### 按 worker 拆段

| worker | `--worker-port` | `--worker-metrics-port` | `--service-port-range` | pfSense 转发 |
| --- | --- | --- | --- | --- |
| worker-A (192.168.1.202) | 10150 | 10151 | 40000-40063 | 10150/10151/40000-40063 → 1.202 同号 |
| worker-B (192.168.1.205) | 10160 | 10161 | 40064-40127 | 10160/10161/40064-40127 → 1.205 同号 |
| worker-C (192.168.1.206) | 10170 | 10171 | 40128-40191 | 10170/10171/40128-40191 → 1.206 同号 |

worker-B 的 compose 片段：

```yaml
command:
  - --server-url=http://192.168.0.242/
  - --worker-ip=192.168.1.205
  - --advertise-address=192.168.0.158   # 同一个 WAN IP，靠端口区分
  - --worker-port=10160
  - --worker-metrics-port=10161
  - --service-port-range=40064-40127
```

几条硬约束：

1. **段不能重叠**：pfSense 的范围转发是"外部段 → 内部同号段"，重叠时只会命中其中一条。
2. **避开 Ray 段**（默认 `41000-41999`）：服务段放在 `40000-40999` 最稳妥，1000 个端口约等于 15 个 worker（每台 64 个）。
3. **段的长度 = 该 worker 的并发实例上限**：默认 64 个，不够就放大（例如 `40064-40227`）。
4. **`worker-port` 也要错开**：否则 `192.168.0.158:10150` 只能指向一台机器，其余 worker 的健康检查过不去。

### 怎么确认每台 worker 用的段

```bash
# 看启动参数
docker inspect gpustack-worker-202 --format '{{.Config.Cmd}}'

# 或看 worker 启动日志的 config dump（显式设置了才会打印 service_port_range）

# 看 worker 记录（$TOKEN 是登录后的会话 Cookie）
curl -s -H "Cookie: gpustack_session=$TOKEN" \
  http://192.168.0.242/v2/workers/4 | jq '{name,port,metricsPort}'
# {"name":"gpustack-worker-202","port":10150,"metricsPort":null}
```

实例实际端口在 `GET /v2/model-instances` 的 `port` 字段里，可以用来验证转发是否生效。

### 另一种做法：每个 worker 一个 WAN VIP

> 前提：WAN 上还能再加 IP。上游只给了一个地址时，只能用上面的拆段方案。

worker 多到端口段不够分、或不想改默认段时，可以在 pfSense 上给每个 worker 配一个 Virtual IP（例如 `192.168.0.160/161/162`），每个 VIP 都转发 `10150`、`10151`、`40000-40063`，worker 的 `--advertise-address` 填各自的 VIP。代价是每台多占一个地址、规则数量翻倍。

### 漏配转发的典型症状

实例在 GPUStack 里是 `RUNNING`（容器起来了，worker 本地 `curl` 也通），但 master 侧请求超时或 500——因为 `advertise_address` 指向的端口没有转发到该 worker。看到"实例正常但接口不通"，先去 pfSense 核对端口段。

## 踩坑清单

1. **`Errno 99` 先查地址归属**：`ip addr` 看目标 IP 是否在本机，没有就是绑定地址填错了。
2. **worker 在 NAT/防火墙后面时，绑定地址和对外地址要分开**：`--worker-ip` 填本机网卡地址，`--advertise-address` 填外部可达地址。
3. **实例不会自动跟随 worker 的地址变化**：`worker_advertise_address` 在调度时复制，改完 worker 要重建实例。
4. **动态端口要预留映射段**：GPUStack 的实例端口默认在 `40000-40063` 内随机分配，pfSense 里那条 `30000-60000` 的整段转发就是为它准备的（多 worker 时要按段收窄，见上一节）；如果只映射单个端口，第二次部署换个端口就又不通了。
5. **加路由之前先看防火墙配置**：能通过 DNAT 解决的，不要在主机上堆静态路由；路由方案还依赖 master 每次都记得加，换机器、重装系统就丢失。
6. **`network_mode: host` 会放大地址错误**：容器不是桥接，没有自己的 IP，worker 上报什么地址，容器就会去绑什么地址。

## 小结

这类问题的迷惑点在于"注册正常"——worker 的心跳是出站连接，NAT 环境下永远能通；但推理引擎的监听端口要求**绑在本机地址**上，两者用的是同一个 `worker.ip` 字段，一旦把外部地址填进去，注册和推理就会一个成功、一个失败。把"绑定地址"和"广播地址"拆开，再配合防火墙的端口转发，才是 NAT 后面 worker 的正确打开方式。
