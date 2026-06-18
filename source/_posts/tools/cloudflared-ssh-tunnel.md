---
title: 使用 cloudflared 穿透内网实现 SSH 免密连接
date: 2026-06-14 10:00:00
description: 介绍如何通过 cloudflared access tcp 命令作为 SSH ProxyCommand，实现穿透内网防火墙安全连接到 Git 服务器或其他 SSH 服务。
keywords: cloudflared, SSH, 内网穿透, Cloudflare Access, ProxyCommand, Git, 免密连接, TCP隧道
categories:
  - 工具
  - 网络
tags:
  - Cloudflare
  - SSH
  - 内网穿透
  - cloudflared
  - 安全
---

## 使用 cloudflared 穿透内网实现 SSH 免密连接

在日常开发和运维中，我们经常需要 SSH 连接到内网服务器。如果服务器没有公网 IP，或者隐藏在防火墙 / NAT 后面，传统的直连方式就行不通了。借助 **Cloudflare Tunnel（cloudflared）+ Cloudflare Access**，可以安全、稳定地实现 SSH 内网穿透，并配合 SSH config 做到"一键连接"。

### 工作原理

整个链路分为两段：

1. **服务端 → Cloudflare 边缘节点**：内网服务器运行 `cloudflared tunnel`，与 Cloudflare 边缘建立持久化的 HTTP/2 隧道（国内用户建议阅读 [Cloudflare Tunnel HTTP/2 优化指南](/2026/05/cloudflare-tunnel-http2-china/)）。
2. **客户端 → Cloudflare 边缘节点**：本地使用 `cloudflared access tcp` 作为 SSH 的 `ProxyCommand`，由 cloudflared 负责与 Cloudflare 边缘建立连接并转发 TCP 流量。

```
本地 SSH 客户端
    │
    ▼
cloudflared access tcp --hostname giteassh.cq.de5.net
    │
    ▼
Cloudflare 边缘节点（全球加速）
    │
    ▼
内网 cloudflared tunnel（HTTP/2 长连接）
    │
    ▼
内网 SSH 服务（如 Gitea / GitLab）
```

### 安装 cloudflared

**Linux (Debian/Ubuntu)**：

```bash
# 添加 Cloudflare 源并安装
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt update && sudo apt install cloudflared
```

**手动下载（通用）**：

```bash
# 以 Linux amd64 为例
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

### 登录 Cloudflare Access

在客户端侧，需要先通过 `cloudflared login` 获取认证凭据。如果你的 Tunnel 绑定了 Cloudflare Access 策略（如一次性 PIN 验证），首次使用时会自动打开浏览器提示登录：

```bash
cloudflared access login
```

浏览器会自动打开，选择对应的团队域名完成授权即可。授权成功后凭据会保存到 `~/.cloudflared/` 目录，后续连接无需再次登录。

### 配置 SSH ProxyCommand

在 `~/.ssh/config` 中添加如下配置：

```ssh-config
Host giteassh.cq.de5.net
    HostName giteassh.cq.de5.net
    User git
    IdentityFile ~/.ssh/fzno1
    IdentitiesOnly yes
    ProxyCommand /home/iding/bin/cloudflared access tcp --hostname %h
```

**配置说明**：

| 字段 | 含义 |
|---|---|
| `Host` | 别名，用于 `ssh <别名>` 直接连接 |
| `HostName` | 实际主机名，必须与 Cloudflare Access 中配置的公开主机名一致 |
| `User` | SSH 登录用户名 |
| `IdentityFile` | 指定私钥文件路径 |
| `IdentitiesOnly yes` | 仅使用指定的私钥，不尝试其他密钥（避免 `Too many authentication failures`） |
| `ProxyCommand` | 将 SSH 流量通过 cloudflared 转发，`%h` 自动替换为 HostName |

**关键点**：

- `ProxyCommand` 中的 `--hostname %h`，`%h` 是 SSH 的内置变量，会自动展开为 `HostName` 字段的值。这样当你修改 `HostName` 时，无需同步修改 `ProxyCommand`。
- cloudflared 二进制路径建议使用绝对路径，避免 `PATH` 查找问题。
- `IdentitiesOnly yes` 很重要——如果本地有多个 SSH 密钥，不开启此选项可能会一次性尝试所有密钥，导致目标服务器返回 `Too many authentication failures`。

### 验证连接

配置完成后，直接使用 `ssh` 别名即可连接：

```bash
ssh giteassh.cq.de5.net
```

**测试连通性（详细输出）**：

```bash
ssh -v giteassh.cq.de5.net 2>&1 | head -20
```

正常情况下，你会看到类似输出：

```
debug1: Executing proxy command: exec /home/iding/bin/cloudflared access tcp --hostname giteassh.cq.de5.net
debug1: identity file /home/iding/.ssh/fzno1 type -1
debug1: identity file /home/iding/.ssh/fzno1-cert type -1
debug1: Local version string SSH-2.0-OpenSSH_8.9p1
...
```

### 使用场景

#### 场景一：Git 免密克隆 / 推送

内网部署了 Gitea / GitLab / GitBucket 等代码托管平台，通过 cloudflared 暴露 SSH 端口后，可以像使用 GitHub 一样正常操作：

```bash
git clone ssh://giteassh.cq.de5.net/username/repo.git
# 或者在现有的仓库中推送
git remote set-url origin ssh://giteassh.cq.de5.net/username/repo.git
git push
```

由于 SSH config 中已配置了 `IdentityFile` 和 `IdentitiesOnly`，整个过程无需输入密码。

#### 场景二：管理多台内网服务器

如果有多个内网 SSH 服务暴露在同一个域名下不同端口，或者不同的子域名：

```ssh-config
Host home-server
    HostName ssh-home.example.com
    User root
    Port 22
    IdentityFile ~/.ssh/home_key
    ProxyCommand /usr/local/bin/cloudflared access tcp --hostname %h

Host dev-server
    HostName ssh-dev.example.com
    User ubuntu
    Port 2222
    IdentityFile ~/.ssh/dev_key
    ProxyCommand /usr/local/bin/cloudflared access tcp --hostname %h
```

#### 场景三：SCP / SFTP 文件传输

连接方式与 SSH 完全一致：

```bash
# SCP
scp myfile.txt giteassh.cq.de5.net:/path/to/destination/

# SFTP
sftp giteassh.cq.de5.net
```

### 常见问题

#### Q: 连接时报 `failed to dial to tunnel` 错误

首先检查 `cloudflared access login` 是否已完成认证。如果凭据过期，重新执行登录即可。

#### Q: 连接超时卡住不动

国内网络环境下，可能与 QUIC 协议被运营商干扰有关。可以参考 [Cloudflare Tunnel HTTP/2 优化指南](/2026/05/cloudflare-tunnel-http2-china/) 将协议强制切换为 HTTP/2。

#### Q: `Permission denied (publickey)` 认证失败

- 确认 `IdentityFile` 路径正确且私钥文件权限为 `600`
- 确认公钥已添加到目标服务器的 `~/.ssh/authorized_keys`
- 尝试用 `ssh -v` 查看详细的认证流程

#### Q: `Too many authentication failures` 错误

确保配置中设置了 `IdentitiesOnly yes`，它会让 SSH 客户端只使用你指定的那一个密钥，而不会把所有本地密钥都试一遍。

#### Q: 如何让 cloudflared 在后台持续运行？

对于客户端侧，`cloudflared access tcp` 是每次 SSH 连接时由 ProxyCommand 临时启动的，无需后台常驻。服务端则需要将 `cloudflared tunnel` 配置为 systemd 服务：

```bash
sudo cloudflared service install
```

### 小结

`cloudflared access tcp` + SSH ProxyCommand 的组合，让我们可以在不暴露公网端口、不修改防火墙规则的前提下，安全地访问内网 SSH 服务。配合 SSH config 的别名机制，使用体验与直连几乎无差异。无论是 Git 免密推送、远程服务器管理还是文件传输，这套方案都能胜任。
