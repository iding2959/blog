---
title: Ubuntu + Clash Verge 打造全屋科学上网网关（超详细实战教程）
date: 2025-12-07 14:30:00
categories:
  - 教程
tags:
  - Clash
  - 代理，路由器
  - 科学上网
---

太棒了，恭喜你成功 🎉！下面我已经帮你把**整个 Ubuntu + Clash Verge 网关代理 + 二级路由器科学上网方案**完整整理成了一篇**可直接发布的 Markdown 博客**，你可以直接复制保存为 `*.md` 文件使用。

---

```md
# Ubuntu + Clash Verge 打造全屋科学上网网关（超详细实战教程）

> 适用场景：  
> ✅ Ubuntu 已安装 Clash Verge  
> ✅ 开启 TUN 模式作为网关代理  
> ✅ 通过网线给普通家用路由器“供网”  
> ✅ 路由器不支持 AP 模式，仅支持：拨号 / 固定 IP / 自动获取 IP  

最终目标：  
👉 让 **整个路由器下的所有设备（手机 / 电脑 / 电视 / 平板）自动科学上网**，无需单独设置代理。

---

## 一、整体网络拓扑结构

```

互联网
↓
enx5c7dae4142f1  （Ubuntu 上游网卡）
↓
Clash Verge TUN 接管
↓
enp1s0 : 192.168.50.1 （Ubuntu 下游供网口）
↓（WAN 口）
路由器：自动获取 IP
↓
WiFi / 有线设备
↓
全屋设备自动科学上网 ✅

````

---

## 二、你的真实网卡情况说明

通过 `ip a` 确认：

- ✅ 上游联网口：`enx5c7dae4142f1`（192.168.0.222）
- ✅ Clash 虚拟网卡：`Mihomo`（198.18.0.1）
- ✅ 下游供网口：`enp1s0`（接路由器）

---

## 三、开启 Ubuntu IPv4 转发（必须）

### 1️⃣ 临时生效

```bash
sudo sysctl -w net.ipv4.ip_forward=1
````

验证：

```bash
cat /proc/sys/net/ipv4/ip_forward
```

输出 `1` 即成功。

---

### 2️⃣ 永久生效（防止重启失效）

```bash
sudo nano /etc/sysctl.conf
```

添加或取消注释：

```
net.ipv4.ip_forward=1
```

执行：

```bash
sudo sysctl -p
```

---

## 四、启用 NAT 网络共享（关键核心）

```bash
sudo iptables -t nat -A POSTROUTING -o enx5c7dae4142f1 -j MASQUERADE
sudo iptables -A FORWARD -i enp1s0 -j ACCEPT
sudo iptables -A FORWARD -o enp1s0 -j ACCEPT
```

验证：

```bash
sudo iptables -t nat -L -n -v
```

看到 `MASQUERADE` 即代表 NAT 生效 ✅

---

## 五、解决 enp1s0 无法自动 UP 的问题

如果出现：

```
enp1s0: state DOWN
```

手动拉起网卡：

```bash
sudo ip link set enp1s0 up
```

确认：

```bash
ip a | grep enp1s0 -A 5
```

出现：

```
state UP
```

说明物理链路已打通 ✅

---

## 六、路由器不支持 AP 模式的解决方案说明

你的路由器仅支持三种上网方式：

* 宽带拨号 ❌
* 固定 IP ❌
* ✅ 自动获取 IP（DHCP） ✅✅✅

因此采用方案：

> ✅ Ubuntu 做“上级网关 + DHCP + NAT”
> ✅ 路由器做“二级路由 + 自动获取 IP”

---

## 七、给 enp1s0 配置固定网关 IP

```bash
sudo ip addr add 192.168.50.1/24 dev enp1s0
```

检查：

```bash
ip a | grep enp1s0 -A 5
```

应看到：

```
inet 192.168.50.1/24 ✅
```

---

## 八、安装并配置 DHCP 服务器（给路由器分 IP）

### 1️⃣ 安装 DHCP 服务

```bash
sudo apt update
sudo apt install isc-dhcp-server -y
```

---

### 2️⃣ 绑定 DHCP 工作网卡

```bash
sudo nano /etc/default/isc-dhcp-server
```

修改为：

```
INTERFACESv4="enp1s0"
```

---

### 3️⃣ 配置 DHCP 地址池

```bash
sudo nano /etc/dhcp/dhcpd.conf
```

添加：

```
subnet 192.168.50.0 netmask 255.255.255.0 {
  range 192.168.50.100 192.168.50.200;
  option routers 192.168.50.1;
  option domain-name-servers 8.8.8.8, 1.1.1.1;
}
```

---

### 4️⃣ 启动 DHCP 服务

```bash
sudo systemctl restart isc-dhcp-server
sudo systemctl enable isc-dhcp-server
systemctl status isc-dhcp-server
```

确保状态为：

```
active (running)
```

---

## 九、路由器后台设置方式（最终关键）

### ✅ 接线方式：

```
Ubuntu enp1s0  ←——网线——→  路由器 WAN 口
```

### ✅ 路由器上网方式选择：

> ✅【自动获取 IP（DHCP）】

不要选择：

* ❌ 宽带拨号
* ❌ 固定 IP

---

## 十、成功验证方法

### ✅ 1️⃣ 路由器后台查看 WAN 口 IP

应显示：

```
192.168.50.xxx ✅
```

---

### ✅ 2️⃣ 手机连 WiFi 测试公网 IP

访问：

```
https://ip.sb
```

如果显示：

* 🇯🇵 日本
* 🇭🇰 香港
* 🇺🇸 美国
* 🇸🇬 新加坡

✅✅✅ 代表全屋科学上网 **彻底成功**！

---

## 十一、方案总结对比

| 方案                | 性能    | 稳定性   | 自由度   | 可玩性   |
| ----------------- | ----- | ----- | ----- | ----- |
| Ubuntu + Clash 网关 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 传统 OpenWRT 旁路由    | ⭐⭐⭐   | ⭐⭐⭐⭐  | ⭐⭐⭐   | ⭐⭐⭐   |

✅ 本方案优势：

* 全透明科学上网
* 支持全设备
* 支持 Docker / 服务器
* 性能远高于普通软路由

---

## 十二、最终结语

这套方案本质上是：

> ✅ Ubuntu = 企业级软路由
> ✅ Clash Verge = 企业级代理网关
> ✅ 普通家用路由器 = 纯 WiFi AP

组合后可以实现：

✅ 稳定
✅ 高速
✅ 全屋无感科学上网
✅ 所有设备免配置

---

如果你愿意，我还可以额外帮你写进阶篇：

* ✅ iptables 规则持久化
* ✅ systemd 自启动网关
* ✅ 多网卡分流策略
* ✅ Docker 容器透明代理

你可以随时告诉我 😄

```

---

✅ 如果你需要，我还可以顺手帮你：

- 美化为 **Hexo / VuePress / Typora 风格**
- 补一份 **网络结构示意图（Mermaid）**
- 做一个 **发布用封面标题+摘要**

你可以告诉我：  
👉 你是打算发在 **CSDN / 博客园 / 个人博客 / 语雀 / Obsidian** 哪个平台？我可以再帮你做一次适配优化。
```
