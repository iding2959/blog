---
title: Ubuntu 软路由 / 网关代理性能优化实战（Clash / mihomo）
date: 2025-12-17 15:10:00
tags:
  - Linux
  - 软路由
  - 网关代理
  - Clash
  - mihomo
  - 网络优化
  - 性能调优
categories: 教程
---


# Ubuntu 软路由 / 网关代理性能优化记录（Clash / mihomo）

> 硬件平台：AMD Embedded G-Series GX-420GI（4C）  
> 系统：Ubuntu Server 24.04  
> 代理核心：mihomo（Clash Meta）  
> 使用场景：网关代理 / 旁路由 / 多设备透明代理

---

## 一、背景与问题

在使用 Ubuntu Server + Clash(mihomo) 作为网关代理时，遇到以下问题：

- 系统 `load average` 偏高（长期 1.5~2.5）
- Telegram、WebSocket 类应用偶发卡顿
- `/proc/interrupts` 显示网卡中断集中在单个 CPU
- mihomo 与系统 / 中断线程抢占 CPU

硬件性能并不弱，但**调度和中断分布不合理**。

---

## 二、硬件与系统环境

### CPU 信息

```bash
lscpu
```
关键参数：

CPU：AMD GX-420GI

核心数：4

最大频率：2.0 GHz

支持特性：AVX2、AES-NI、SVM

性能足够支撑家庭或小型网络网关

## 三、问题定位
### 1️⃣ 网卡中断集中
```bash
cat /proc/interrupts | grep enp1s0
```
发现：

enp1s0 的 MSI-X 中断几乎全部落在 CPU1

其他 CPU 几乎不参与网络处理

### 2️⃣ mihomo 与系统线程抢 CPU

ps -o pid,psr,comm -C verge-mihomo


mihomo 默认运行在 0-3 全核，容易和：

IRQ

ksoftirqd

systemd

ssh

发生竞争。

## 四、优化目标

让中断和代理分工明确

避免所有高频任务堆在一个 CPU

降低负载，而不是单纯“提频”

## 五、具体优化方案
### ✅ 1. 绑定 mihomo 到指定 CPU（核心优化）

将代理核心固定到 CPU 2,3：
```bash
pgrep -f mihomo
sudo taskset -cp 2,3 <PID>
```

验证：
```bash
ps -o pid,psr,comm -p <PID>
```

效果：
mihomo 不再抢 CPU0
系统与中断更稳定
### 持久化 🔧 使用 systemd 为 clash-verge-service 永久绑定 CPU 核心

<details>
<summary><strong>📌 为什么要给 clash-verge-service 绑定 CPUAffinity？</strong></summary>

在对网关代理进行性能优化时，很多人会直接对 mihomo（Clash Core）进程使用 taskset 进行 CPU 绑定。但在 Clash Verge（Linux） 的场景下，更合理、也更“工程化”的做法，是直接对 systemd 服务 **clash-verge-service** 设置 CPU 亲和性。

这样可以确保：

- 服务重启 / 崩溃自动拉起后，CPU 绑定依然生效  
- 系统重启后无需手动干预  
- 不会被 Clash Verge 的升级覆盖  

### 为什么绑定的是 clash-verge-service，而不是 mihomo？

在 Clash Verge 中：

- `clash-verge-service` 是 systemd 管理的主服务  
- `mihomo`（或 `verge-mihomo`）是其内部拉起的核心进程  
- systemd 的 `CPUAffinity` 会自动继承到子进程  

也就是说：

> 只要限制了 `clash-verge-service`，  
> `mihomo` 自然就会被限制在同一组 CPU 上运行。

这也是 **systemd 官方推荐的做法**。

</details>


🛠 设置 CPUAffinity（推荐方式）

使用 systemd 的 drop-in 覆盖配置：
```bash
sudo systemctl edit clash-verge-service
```

在打开的编辑器中，写入以下内容（只保留这一段）：
```bash
[Service]
CPUAffinity=2 3
```

保存并退出后，执行：
```bash
sudo systemctl daemon-reexec
sudo systemctl restart clash-verge-service
```
🔍 验证 CPU 绑定是否生效
1️⃣ 查看 systemd 层面的 CPUAffinity
```bash
systemctl show clash-verge-service -p CPUAffinity
```bash

期望输出：
```bash
CPUAffinity=2 3
```
2️⃣ 查看服务进程实际运行的 CPU
```bash
ps -o pid,psr,comm -C clash-verge-service
```

示例输出：
```bash
PID     PSR   COMMAND
16340     3   clash-verge-ser
```

其中：

PSR=3 表示进程当前运行在 CPU3

与设置的 CPUAffinity=2 3 完全一致

✅ 为什么不用 taskset？

taskset 虽然能立刻生效，但存在明显问题：

只对当前进程有效

服务重启 / 系统重启后全部失效

容易与 systemd 的调度管理产生冲突

相比之下：

systemd 的 CPUAffinity 是长期、稳定、可维护的解决方案

🧠 实际效果

在为 clash-verge-service 绑定 CPU 后：

网关整体 load average 明显下降

网络转发延迟和抖动减少

高并发场景（Telegram / 多设备同时访问）更加稳定
### ✅ 2. 启用并扩大 RPS（软中断分流）
```bash
echo 32768 | sudo tee /sys/class/net/enp1s0/queues/rx-0/rps_flow_cnt
```
✅ 推荐的持久化方案
方法一：systemd oneshot（推荐）
```bash
# /etc/systemd/system/rps-enp1s0.service
[Unit]
Description=Enable RPS for enp1s0
After=network-online.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo 32768 > /sys/class/net/enp1s0/queues/rx-0/rps_flow_cnt'

[Install]
WantedBy=multi-user.target
```

启用：
```bash
sudo systemctl daemon-reload
sudo systemctl enable rps-enp1s0
sudo systemctl start rps-enp1s0
```

允许更多网络流量在多 CPU 之间分发

避免 RX 堆积在单核

### ✅ 3. 启用 BBR 拥塞控制
```bash
cat <<EOF | sudo tee /etc/sysctl.d/99-gateway-tuning.conf
net.ipv4.tcp_congestion_control=bbr
net.netfilter.nf_conntrack_max=262144
EOF

sudo sysctl --system

```

验证：
```bash
cat /proc/sys/net/netfilter/nf_conntrack_max
```
## 六、优化效果对比
优化前：

load average: 2.13, 1.58, 1.19

优化后：
load average: 0.47, 0.91, 1.17


📉 负载显著下降，且趋势稳定

## 七、结论与经验总结

性能瓶颈不在 CPU 算力，而在调度

网关类系统必须关注：

中断分布

进程亲和性

网络栈参数

对于 Clash / mihomo：

绑核 ≫ 换硬件

RPS ≫ 单核 RX

这套优化适用于：
家庭软路由 / 小型旁路由 / VPS 网关 / 透明代理节点
