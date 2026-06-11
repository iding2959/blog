---
title: Cloudflare Tunnel 国内优化指南：强制使用 HTTP/2 解决 QUIC 连接问题
date: 2026-05-19 14:00:00
description: 在使用 Cloudflare Tunnel（cloudflared）进行内网穿透时，国内用户经常会遇到连接不稳定、延迟极高甚至完全无法访问的问题。这背后的根本原因是：
keywords: Cloudflare, Cloudflare Tunnel, 网络优化
categories:
  - 工具
  - 网络
tags:
  - Cloudflare
  - 内网穿透
  - HTTP/2
  - QUIC
  - 网络优化
---

## 问题背景

在使用 Cloudflare Tunnel（cloudflared）进行内网穿透时，国内用户经常会遇到连接不稳定、延迟极高甚至完全无法访问的问题。这背后的根本原因是：

**中国大陆部分运营商（如中国电信、中国联通、中国移动）对 UDP 流量（尤其是 443 端口的 UDP）存在极其严格的 QoS（服务质量）限制甚至直接丢包**。

这就导致基于 UDP 的 HTTP/3 (QUIC) 协议在跨国连接时经常处于"半死不活"的状态。

而 **Cloudflare Tunnel 默认会优先尝试使用 QUIC 协议 (HTTP/3)** 来建立本地服务器到 Cloudflare 边缘节点的连接。如果遭遇运营商拦截，就会导致：

- 🔴 连接不断断开重连
- 🔴 延迟极高（数秒到十几秒）
- 🔴 部分请求超时
- 🔴 完全无法访问

## 解决方案核心思路

**强制 cloudflared 在本地回源时使用基于 TCP 的 HTTP/2 协议**，彻底绕过 UDP 限制。

根据你的部署方式（命令行、配置文件或 Docker），选择对应的修改方法。

---

## 🛠️ 方法一：命令行启动方式

如果你是通过命令行直接启动 Cloudflare Tunnel，只需在 `cloudflared tunnel run` 命令后面加上 `--protocol http2` 参数。

### 示例命令

```bash
cloudflared tunnel --protocol http2 run <你的隧道名称或ID>
```

### 完整示例

```bash
# 假设你的隧道名称是 my-tunnel
cloudflared tunnel --protocol http2 run my-tunnel
```

### 验证是否生效

启动后，观察输出日志中是否包含类似信息：

```
INFO Connection established protocol=http2
```

如果看到 `protocol=http2`，说明配置生效。

---

## 🛠️ 方法二：使用配置文件（推荐）

如果你使用配置文件管理 Cloudflare Tunnel，这是最推荐的方式，便于长期维护和版本控制。

### 配置文件位置

通常位于以下路径之一：
- Linux/macOS: `~/.cloudflared/config.yml`
- Windows: `%USERPROFILE%\.cloudflared\config.yml`
- 自定义路径: 通过 `--config` 参数指定

### 配置示例

```yaml
tunnel: <你的Tunnel-ID>
credentials-file: /root/.cloudflared/<Tunnel-ID>.json

# 🎯 核心配置：强制使用 http2 替代 quic
protocol: http2

ingress:
  - hostname: yoursite.com
    service: http://localhost:8080
  - hostname: api.yoursite.com
    service: http://localhost:3000
  # 捕获所有其他请求，返回 404
  - service: http_status:404
```

### 关键配置说明

| 配置项 | 说明 |
| --- | --- |
| `tunnel` | 你的 Tunnel ID（在 Cloudflare Zero Trust 后台创建隧道时生成） |
| `credentials-file` | 凭证文件路径（创建隧道时自动生成） |
| `protocol: http2` | **核心配置**，强制使用 HTTP/2 协议 |
| `ingress` | 路由规则，定义域名到本地服务的映射 |

### 修改后重启服务

如果你使用 systemd 管理服务：

```bash
sudo systemctl restart cloudflared
```

如果是手动启动：

```bash
cloudflared tunnel run
```

---

## 🛠️ 方法三：Systemd 服务托管方式

如果你是使用 `systemctl` 托管的 cloudflared 服务，只需要修改 Systemd 服务配置文件或其关联的环境配置文件即可。

### 1. 查找服务文件位置

通常，cloudflared 官方安装脚本会自动创建名为 `cloudflared.service` 的服务。你可以通过以下命令直接编辑：

```bash
sudo systemctl edit --full cloudflared.service
```

> 💡 提示：如果习惯使用 vim，也可以手动执行 `sudo vim /etc/systemd/system/cloudflared.service`

### 2. 修改配置（根据启动方式选择）

进入编辑界面后，根据你的具体服务内容选择对应的修改方式：

#### 情况 A：通过 Token 启动的服务

如果你的服务文件里 `ExecStart` 后面跟着的是 `--token`，请直接在后面加上 `--protocol http2`。

**修改前：**

```ini
[Service]
ExecStart=/usr/local/bin/cloudflared tunnel run --token eyJ...
```

**修改后：**

```ini
[Service]
ExecStart=/usr/local/bin/cloudflared tunnel --protocol http2 run --token eyJ...
```

#### 情况 B：通过配置文件（config.yml）启动的服务

如果你的服务文件里指定了 `config.yml` 的路径：

**修改前：**

```ini
[Service]
ExecStart=/usr/local/bin/cloudflared --config /etc/cloudflared/config.yml tunnel run
```

**修改后：**

```ini
[Service]
ExecStart=/usr/local/bin/cloudflared --config /etc/cloudflared/config.yml tunnel --protocol http2 run
```

> 💡 提示：如果是情况 B，你其实也可以不用动这个服务文件，直接去修改 `/etc/cloudflared/config.yml`，在里面加一行 `protocol: http2`，效果是完全一样的（推荐使用配置文件方式，更便于维护）。

### 3. 重新加载并重启服务

修改并保存服务文件后，必须刷新 Systemd 守护进程并重启服务才能生效：

```bash
# 1. 重新加载 Systemd 配置
sudo systemctl daemon-reload

# 2. 重启 cloudflared 服务
sudo systemctl restart cloudflared

# 3. 检查服务状态是否正常
sudo systemctl status cloudflared
```

### 4. 验证是否成功切换为 HTTP/2

重启后，查看 cloudflared 的实时日志，确认它是否已经成功使用了 `http2` 协议：

```bash
sudo journalctl -u cloudflared.service -n 50 -f
```

**成功标志**：

- 日志中出现 `protocol=http2` 或 `Protocol: http2`
- 连接端口变成了 **7844**（Cloudflare 的 HTTP/2 隧道专用端口）

**失败标志**：

- 依然在使用 **443 端口**并提示 `quic`
- 请检查上面的参数位置是否放错（`--protocol http2` 必须在 `run` 之前）

### 完整服务文件示例

以下是一个完整的 `cloudflared.service` 文件示例供参考：

```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/cloudflared tunnel --protocol http2 run --token eyJhIjoiY2xvdWRmbGFyZS10dW5uZWwiLCJ0IjoiZXhhbXBsZS10b2tlbi1oZXJlIn0
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

---

## 🛠️ 方法四：Docker 部署方式

如果你通过 Docker 容器运行 Cloudflare Tunnel，需要在启动命令中加入 `--protocol http2` 参数。

### Docker Run 方式

```bash
docker run -d \
  --name cloudflared \
  --restart unless-stopped \
  -v ~/.cloudflared:/etc/cloudflared \
  cloudflare/cloudflared:latest \
  tunnel --protocol http2 run --token <你的TUNNEL_TOKEN>
```

### Docker Compose 方式（推荐）

创建 `docker-compose.yml` 文件：

```yaml
version: '3'
services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: cloudflared
    restart: unless-stopped
    command: tunnel --protocol http2 run --token <你的TUNNEL_TOKEN>
    # 如果使用配置文件方式，可以挂载配置文件
    # volumes:
    #   - ./config.yml:/etc/cloudflared/config.yml
    #   - ./tunnel-credentials.json:/etc/cloudflared/tunnel-credentials.json
```

### 启动容器

```bash
docker-compose up -d
```

### 查看日志验证

```bash
docker logs -f cloudflared
```

确认日志中包含 `protocol=http2` 字样。

---

## 💡 原理解析：为什么这样就能解决问题？

### 默认状态（使用 QUIC，问题状态）

```
cloudflared ──(UDP/443)──> 运营商 QoS 限制（拦截/丢包） ──✗──> Cloudflare 节点
                                    ❌ 连接不稳定/失败
```

### 优化后状态（使用 HTTP/2，正常状态）

```
cloudflared ──(TCP/7844 或 443)──> 运营商放行 ──✓──> Cloudflare 节点
                                    ✅ 稳定连接
```

### 关键点说明

1. **QUIC 基于 UDP**：HTTP/3 使用 QUIC 协议，底层是 UDP。国内运营商对 UDP（尤其是 443 端口）有严格限制。

2. **HTTP/2 基于 TCP**：当指定 `protocol: http2` 后，Cloudflare Tunnel 会改用标准的 TCP 协议（通常是 7844 端口或 443 端口的 TCP）与 Cloudflare 边缘节点建立长连接。

3. **TCP 优先级更高**：TCP 协议在国内跨国网络中的优先级和稳定性远高于 UDP，从而彻底避免了因 QUIC 被墙或被限制导致的无法访问问题。

---

## 🎯 进阶优化：配合优选 IP 效果更佳

仅仅修改为 `http2` 只能保证**你的内网服务器到 Cloudflare 节点**这一段是稳定的。

但**中国用户到 Cloudflare 节点**这一段（即公网访问段），依然可能会因为 Cloudflare 默认分配的 Anycast IP 在国内被限速。

### 优化建议

#### 1. 在 Cloudflare 后台关闭 HTTP/3 (QUIC)

这样可以确保国内用户访问你的网站时，浏览器也会强制降级到 HTTP/2 (TCP) 访问，进一步提升稳定性。

**操作步骤**：
1. 登录 [Cloudflare 仪表盘](https://dash.cloudflare.com/)
2. 选择你的域名
3. 进入 **网络 (Network)** 菜单
4. 找到 **HTTP/3 (with QUIC)** 开关，将其关闭

![Cloudflare 网络设置](../../img/cloudflare-tunnel/network-http3-disable.png)

#### 2. 使用 Cloudflare 优选 IP（SaaS 域名重定向）

配合市面上的 Cloudflare 优选 IP 脚本，将国内用户的流量解析到国内延迟较低的 Cloudflare 边缘 IP 上。

**实现方式**：
- 使用 DNS 智能解析（如 Cloudflare Workers 或第三方 DNS 服务）
- 针对国内 IP 返回优选的 Cloudflare IP
- 针对海外 IP 返回默认的 Anycast IP

**优选 IP 工具推荐**：
- [CloudflareSpeedTest](https://github.com/XIU2/CloudflareSpeedTest)
- [better-cloudflare-ip](https://github.com/badafans/better-cloudflare-ip)

#### 3. 启用 Argo Smart Routing（付费功能）

Cloudflare Argo 可以智能选择最优路由路径，进一步提升跨国访问速度和稳定性。

**价格**：$5/月 + $0.10/GB 流量费

对于高流量或对稳定性要求极高的业务，Argo 是值得考虑的选项。

---

## 📋 常见问题 FAQ

### Q1: 修改为 HTTP/2 会影响性能吗？

**A**: 理论上 QUIC (HTTP/3) 比 HTTP/2 性能更好，但在国内网络环境下，由于 UDP 被限制，QUIC 反而会导致极差的体验。**使用 HTTP/2 后，虽然理论性能略低，但实际体验会大幅提升**，因为稳定性是第一位的。

### Q2: 我的 cloudflared 版本较老，支持 `--protocol` 参数吗？

**A**: `--protocol` 参数在较新版本中引入，建议升级到最新版本：

```bash
# Linux/macOS
cloudflared update

# 或重新下载安装
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### Q3: 如何验证当前使用的协议？

**A**: 查看 cloudflared 的日志输出，搜索 `protocol` 关键字：

```bash
# 查看 systemd 日志
sudo journalctl -u cloudflared -f | grep protocol

# 查看 Docker 日志
docker logs -f cloudflared | grep protocol
```

正常情况下应该看到 `protocol=http2`。

### Q4: 配置后仍然不稳定怎么办？

**A**: 依次检查以下几点：
1. 确认配置已生效（查看日志中的 `protocol=http2`）
2. 检查是否在 Cloudflare 后台关闭了 HTTP/3
3. 尝试使用优选 IP
4. 检查本地网络是否稳定（排除本地网络问题）
5. 尝试更换 Cloudflare Tunnel 的边缘节点（重启服务会自动重新连接）

---

## 🎉 总结

通过强制 Cloudflare Tunnel 使用 HTTP/2 协议，可以有效解决国内运营商对 UDP/QUIC 的限制问题，大幅提升连接稳定性和访问速度。

### 核心要点

✅ **必做**：在 cloudflared 配置中添加 `protocol: http2`  
✅ **推荐**：在 Cloudflare 后台关闭 HTTP/3 (QUIC)  
✅ **进阶**：配合优选 IP 进一步提升国内访问速度

希望这篇教程能帮助你彻底解决 Cloudflare Tunnel 在国内的连接问题！

---

## 参考资料

- [Cloudflare Tunnel 官方文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [cloudflared GitHub 仓库](https://github.com/cloudflare/cloudflared)
- [QUIC 协议详解](https://datatracker.ietf.org/doc/html/rfc9000)
