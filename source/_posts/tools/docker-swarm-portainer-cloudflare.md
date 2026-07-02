---
title: Docker Swarm 最佳实践：从零构建安全高效的 Portainer 与全内网穿透架构
date: 2026-05-02 13:16:00
description: 在 Docker Swarm 集群中告别宿主机端口暴露和容器间通信延迟高的困扰。本文以 Portainer + Cloudflare Tunnel 为例，手把手教你构建基于自定义 Overlay 网络的全内网穿透架构，实现零端口暴露与极速服务互通。
keywords: Docker Swarm, Portainer, Cloudflare Tunnel, Overlay网络, 内网穿透, 容器安全
categories:
  - 工具
tags:
  - Docker
  - Docker Swarm
  - Cloudflare
  - DevOps
  - 容器编排
---

## 引言

在利用 Docker Swarm 部署微服务时，很多初学者常常会遇到集群网络错综复杂、容器间通信延迟高、以及宿主机端口暴露过多的安全隐患。

本文将以 **Portainer（集群可视化面板）** 的安装为例，带大家构建一个符合生产标准的 Docker Swarm 网络架构。我们将通过引入自定义 Overlay 全局网络，让 Portainer、Cloudflare Tunnel 穿透服务以及你的业务容器（如 Gitea、Redis、Postgres）全内网极速互通，并彻底收紧宿主机端口。

## 一、核心架构设计

在传统的单机 `docker-compose` 中，我们习惯于使用 `network_mode: "host"` 或通过宿主机 IP + 端口进行容器间转发。但在 Docker Swarm 集群模式下，这种做法不仅性能损耗大，还会带来宿主机 IP 变动导致穿透断开的风险。

标准的 Swarm 架构应当建立清晰的网络隔离边界：

- **`portainer_agent_network`（管理专属私道）**：专供 Portainer Server 与各节点 Agent 进行高特权集群管理通信，与业务完全隔离。

- **`iding-net`（业务/穿透专用专线）**：我们手动创建的全局 Overlay 网络。Cloudflare Tunnel 和你的所有业务容器（Portainer、Gitea 等）都插在这根网线上，通过服务名（Service Name）直接在内存中高速交换数据。

## 二、基础准备：创建全局 Overlay 网络

在开始部署任何服务之前，我们需要先在 Swarm 管理节点（Manager）上，手动创建一个支持容器直接挂载的全局覆盖网络：

```bash
sudo docker network create --driver=overlay --attachable iding-net
```

- `--driver=overlay`：允许跨多台服务器节点进行容器间通信。
- `--attachable`：允许独立的常规容器或不同 Stack 的服务自由加入该网络。

## 三、在 Swarm 中安装与部署 Portainer

Portainer 在 Swarm 中通常以 Stack 形式部署，包含一个处于 Manager 节点的 Server，和分布在每个节点的 Agent。

### 1. 编写配置文件 `portanier.yml`

创建并编辑 `portanier.yml`，我们将 Portainer 引入双网卡设计：一根线连 `agent_network` 用于集群管理，一根线连 `iding-net` 用于内网穿透。

```yaml
version: '3.8'

services:
  agent:
    image: portainer/agent:lts
    environment:
      # 汇报当前节点上的常规容器状态
      - AGENT_CLUSTER_ADDR=tasks.agent
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /var/lib/docker/volumes:/var/lib/docker/volumes
    networks:
      - agent_network
    deploy:
      mode: global # 确保集群中每台机器都自动运行一个 Agent
      restart_policy:
        condition: on-failure

  portainer:
    image: portainer/portainer-ce:lts
    command: -H tcp://tasks.agent:9001 --tlsskipverify
    environment:
      - TZ=Asia/Shanghai

    # ⚠️ 提示：当外网穿透测试成功后，下面这三行 ports 映射可以直接删掉/注释掉
    ports:
      - "9443:9443"
      - "9000:9000"
      - "8000:8000"

    volumes:
      - portainer_data:/data

    networks:
      - agent_network  # 保持原样，用于管理集群
      - iding-net      # ➕ 关键：加入穿透网络，让穿透容器能找到它

    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role == manager # 强绑定在管理节点

networks:
  agent_network:
    driver: overlay
    attachable: true

  # ========================================================
  # 引入我们提前手动创建好的外部全局网络
  # ========================================================
  iding-net:
    external: true

volumes:
  portainer_data:
```

### 2. 使用 Stack 部署上线

在终端执行以下命令将 Portainer 部署到集群中，Stack 名称指定为 `portainer`：

```bash
sudo docker stack deploy -c portanier.yml portainer
```

## 四、实现 Cloudflare Tunnel 极速内网穿透

当 Portainer 接入 `iding-net` 后，你的 `cloudflare-tunnel` 容器也应当同步加入该网络。

### 1. 优化后的 cloudflared 部署配置

放弃传统的 `network_mode: "host"`，改为全内网标准互通：

```yaml
version: '3.8'

services:
  cloudflare-tunnel:
    image: cloudflare/cloudflared:latest
    deploy:
      restart_policy:
        condition: on-failure
    entrypoint: ["cloudflared", "tunnel"]
    command:
      - "run"
      - "--token"
      - "YOUR_CLOUDFLARE_TUNNEL_TOKEN" # 填入你的真实 Token

    environment:
      - TUNNEL_METRICS=0.0.0.0:2000
      - TCP_KEEPALIVE=30s
      - NO_AUTOUPDATE=true

    networks:
      - iding-net # 接入统一的穿透网络

networks:
  iding-net:
    external: true
```

### 2. Cloudflare Zero Trust 后台配置

由于 `cloudflared` 和 `portainer` 都在同一个 `iding-net` 网络中，在 Cloudflare 网页后台配置 Public Hostnames 时，内网 URL 填写的逻辑将变得极其优雅和安全：

- **Portainer 穿透**：`http://portainer_portainer:9000`（格式为：`http://Stack名_服务名:内部端口`）
- **Gitea 穿透**：`http://gitea_gitea:3000`
- **Redis 内部调用**：在 Gitea 或其他业务配置中，直接填写 `redis_redis:6379`

## 五、全内网架构的终极优势

相比于传统的宿主机 IP 映射转发，这种"全内网"设计带来了质的飞跃：

### 速度大幅提升（延迟降低 30% ~ 50%）

流量完全在 Docker 内存的内核态（VxLAN 隧道）直接复制和封装，绕过了宿主机的物理网卡、Loopback 协议栈及 iptables 规则匹配，容器间 Ping 值通常能从 1.5ms 压缩至 0.2ms。

### 免受宿主机 IP 变动影响

不论宿主机的局域网 IP 怎么因重启或 DHCP 改变，Docker 内部的 DNS 永远能精准根据服务名找到目标容器，穿透坚如磐石。

### 安全性拉满（零端口暴露）

外网测通后，你可以安全地把 Portainer、Redis、Postgres 中的 `ports` 模块全部删掉。此时你的服务器在局域网内处于"隐身状态"，完全免疫局域网端口扫描，只有通过你授权的 Cloudflare 域名才能安全访问！

## 六、常用运维命令小结

查看当前运行的所有服务状态：

```bash
sudo docker service ls
```

强行滚动重启某个 Swarm 服务（不影响业务）：

```bash
sudo docker service update --force portainer_portainer
```

检查容器连入网络的虚拟网线（veth）数量：

```bash
ip a | grep veth
```

> 注：每个联网容器都会在宿主机生成一根虚拟网线，数量等于容器总数是完全正常的底层表现。

---

现在，你的 Docker Swarm 集群已经拥有了最标准、健康的"大楼电梯与暗道"网络结构。赶快尝试一下，享受零端口暴露带来的极致安全与内网飙车的快感吧！
