---
title: Ubuntu + Clash Verge 打造全屋科学上网网关（超详细实战教程）
date: 2025-12-07 14:30:00
categories:
  - 教程
  - 代理
tags:
  - Clash
  - 代理，路由器
  - 科学上网
---

# Ubuntu + Clash Verge 打造全屋科学上网网关（完整实战记录）

本文完整记录一次从 0 到 1 搭建 **Ubuntu + Clash Verge 作为网关，为普通家用路由器供网，实现全屋设备自动科学上网** 的真实过程。  
无论你的路由器是否支持 AP 模式，都可以参考本文复现。

---

## 一、最终网络拓扑结构


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

## 二、真实环境说明

- 操作系统：Ubuntu Server / Desktop
- 代理程序：Clash Verge
- 工作模式：TUN 透明代理（网关模式）
- 上游网卡：`enx5c7dae4142f1`（192.168.0.222）
- 下游供网口：`enp1s0`
- 路由器能力：仅支持
  - 宽带拨号
  - 固定 IP
  - 自动获取 IP（DHCP）

---

## 三、开启 IPv4 转发（必须启用）

### 1. 临时生效（立即启用）

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```
验证：

```
cat /proc/sys/net/ipv4/ip_forward
```

输出：
```
1
```
表示生效。
### 2. 永久生效（防止重启失效）
```
sudo nano /etc/sysctl.conf
```

添加或取消注释：
```
net.ipv4.ip_forward=1
```

应用配置：
```
sudo sysctl -p
```
## 四、配置 NAT 网络共享（核心步骤）
```bash
sudo iptables -t nat -A POSTROUTING -o enx5c7dae4142f1 -j MASQUERADE
sudo iptables -A FORWARD -i enp1s0 -j ACCEPT
sudo iptables -A FORWARD -o enp1s0 -j ACCEPT
```

验证 NAT 是否生效：
```
sudo iptables -t nat -L -n -v
```

看到 MASQUERADE 即代表配置成功。

### 永久生效
你现在这套规则是 “内存临时的”，必须马上做：
```
sudo apt install iptables-persistent -y
```

安装过程中：
```
Save current IPv4 rules? → 选 Yes ✅
Save current IPv6 rules? → 选 Yes ✅
```

然后验证是否真正保存：
```
sudo cat /etc/iptables/rules.v4
```

如果你看到：
```
-A POSTROUTING -o enx5c7dae4142f1 -j MASQUERADE
-A FORWARD -i enp1s0 -j ACCEPT
-A FORWARD -o enp1s0 -j ACCEPT
```

✅ 这就代表：
哪怕你断电 + 重启 + 更新系统，路由器都还能继续科学上网

## 五、修复 enp1s0 物理网口为 DOWN 的问题

当发现 enp1s0 为：
```
state DOWN
```

可手动拉起：
```
sudo ip link set enp1s0 up
```

验证：
```
ip a | grep enp1s0 -A 5
```

只要出现：
```
state UP
```

说明物理链路正常。

## 六、路由器不支持 AP 模式的解决方案说明

由于路由器仅支持：

宽带拨号（PPPoE）

固定 IP

自动获取 IP（DHCP）

✅ 正确方案为：

Ubuntu 作为：

上级网关

DHCP 服务器

NAT 转发设备

路由器作为：

二级路由

通过 WAN 口自动获取 IP 上网

## 七、为 enp1s0 设置固定网关 IP
```
sudo ip addr add 192.168.50.1/24 dev enp1s0
```

验证：
```
ip a | grep enp1s0 -A 5
```

应看到：
```
inet 192.168.50.1/24
```
## 八、安装并配置 DHCP 服务（为路由器分配 IP）
### 1. 安装 DHCP 服务
```
sudo apt update
sudo apt install isc-dhcp-server -y
```
### 2. 指定 DHCP 服务生效的网卡
```
sudo nano /etc/default/isc-dhcp-server
```

修改：
```
INTERFACESv4="enp1s0"
```
### 3. 配置 DHCP 地址池
```
sudo nano /etc/dhcp/dhcpd.conf
```

在文件末尾添加：
```bash
subnet 192.168.50.0 netmask 255.255.255.0 {
  range 192.168.50.100 192.168.50.200;
  option routers 192.168.50.1;
  option domain-name-servers 8.8.8.8, 1.1.1.1;
}
```
### 4. 启动 DHCP 服务
```
sudo systemctl restart isc-dhcp-server
sudo systemctl enable isc-dhcp-server
```

检查状态：
```
systemctl status isc-dhcp-server
```

状态需为：
```
active (running)
```
## 九、路由器后台最终设置方式
### 1. 正确接线方式
Ubuntu enp1s0  ←——网线——→  路由器 WAN 口

### 2. 路由器上网方式选择

✅ 选择：

自动获取 IP（DHCP）

❌ 不要选择：

宽带拨号

固定 IP

## 十、最终验证
### 1. 查看路由器 WAN 口 IP

应获取到：

192.168.50.xxx

### 2. 手机测试公网 IP

连接路由器 WiFi 后访问：

https://ip.sb


若显示：

🇭🇰 香港

🇯🇵 日本

🇸🇬 新加坡

🇺🇸 美国

✅ 代表全屋科学上网成功。

### 十一、方案优劣势总结
| 方案                | 性能    | 稳定性   | 自由度   | 可扩展性  |
| ----------------- | ----- | ----- | ----- | ----- |
| Ubuntu + Clash 网关 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 普通 OpenWRT 旁路由    | ⭐⭐⭐   | ⭐⭐⭐⭐  | ⭐⭐⭐   | ⭐⭐⭐   |


本方案优势：

所有设备无需单独配置代理

代理规则完全由 Clash 控制

可兼容 Docker、服务器部署

性能远高于传统软路由

## 十二、结语

本方案本质上是：

Ubuntu = 企业级软路由

Clash Verge = 企业级透明代理网关

普通家用路由器 = 纯 WiFi 接入设备

最终效果：

全屋设备自动科学上网

无感知、零配置

稳定、高速、可长期运行

至此，本次 Ubuntu + Clash Verge 网关代理实战部署完整结束。
