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
'''
cat /proc/interrupts | grep enp1s0
'''
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
'''
pgrep -f mihomo
sudo taskset -cp 2,3 <PID>
'''

验证：
'''
ps -o pid,psr,comm -p <PID>
'''

效果：
'''
mihomo 不再抢 CPU0
'''
系统与中断更稳定

### ✅ 2. 启用并扩大 RPS（软中断分流）
'''
echo 32768 | sudo tee /sys/class/net/enp1s0/queues/rx-0/rps_flow_cnt
'''

说明：

允许更多网络流量在多 CPU 之间分发

避免 RX 堆积在单核

### ✅ 3. 启用 BBR 拥塞控制
'''
sudo sysctl -w net.ipv4.tcp_congestion_control=bbr
'''

永久生效：
'''
echo "net.ipv4.tcp_congestion_control=bbr" | sudo tee -a /etc/sysctl.conf
'''
### ✅ 4. 提高 conntrack 上限（高并发必须）
'''
sudo sysctl -w net.netfilter.nf_conntrack_max=262144
'''

验证：
'''
cat /proc/sys/net/netfilter/nf_conntrack_max
'''
六、优化效果对比
优化前：
'''
load average: 2.13, 1.58, 1.19
'''
优化后：
'''
load average: 0.47, 0.91, 1.17
'''

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
