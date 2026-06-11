---
title: PostgreSQL 开启 SSL（Docker 环境完整实践记录）
date: 2026-05-11 15:00:00
description: 在使用 Docker 部署 PostgreSQL 时，为了提升数据传输安全性，我们需要为数据库连接开启 SSL/TLS 加密。
keywords: PostgreSQL, SSL, Docker, 数据库安全
categories:
  - 工具
  - PostgreSQL
tags: [PostgreSQL, SSL, Docker, Navicat, Cloudflare Tunnel]
---

## 背景

在使用 Docker 部署 PostgreSQL 时，为了提升数据传输安全性，我们需要为数据库连接开启 SSL/TLS 加密。

本文记录在 **Docker + Cloudflare Tunnel + Navicat** 环境下，为 PostgreSQL 启用 SSL 的完整过程与踩坑总结。

## 环境说明

| 组件 | 说明 |
|------|------|
| 操作系统 | Linux（Docker Host） |
| 数据库 | PostgreSQL 18 |
| 部署方式 | Docker / Portainer Stack |
| 客户端 | Navicat |
| 使用场景 | 内网访问 + Cloudflare Tunnel |

## SSL 基本概念

PostgreSQL 的 SSL 加密依赖两类文件：

- `server.crt`：证书（公钥，可分发）
- `server.key`：私钥（必须严格保密）

作用：

- 加密客户端与数据库之间的通信
- 防止数据被抓包
- 提升连接安全性

## 生成 SSL 证书

### 创建目录

```bash
mkdir -p /home/safone/data/postgresql/ssl
cd /home/safone/data/postgresql/ssl
```

### 生成证书

使用 OpenSSL 生成自签名证书：

```bash
openssl req -new -x509 -days 365 -nodes \
  -out server.crt \
  -keyout server.key
```

### 设置权限（非常重要）

```bash
sudo chown 999:999 /home/safone/data/postgresql/ssl/server.key
chmod 600 server.key
chmod 644 server.crt
```

> **注意**：
> - `chown 999:999`：Docker 容器中 PostgreSQL 以 `postgres` 用户（UID 999）运行，宿主机上的私钥文件必须归属该用户，否则容器内无法读取
> - `chmod 600`：如果私钥权限过于宽松（group 或 world 可读），PostgreSQL 会拒绝启动，这是安全机制的一部分

## Docker 配置 PostgreSQL SSL

修改 `docker-compose` / Portainer Stack：

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:18
    container_name: postgres
    restart: unless-stopped

    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: "your_password"
      POSTGRES_DB: iding

    ports:
      - "5432:5432"

    volumes:
      - /home/safone/data/postgresql:/var/lib/postgresql
      - /home/safone/data/postgresql/ssl/server.crt:/var/lib/postgresql/server.crt
      - /home/safone/data/postgresql/ssl/server.key:/var/lib/postgresql/server.key

    command: >
      postgres
      -c ssl=on
      -c ssl_cert_file=/var/lib/postgresql/server.crt
      -c ssl_key_file=/var/lib/postgresql/server.key
```

关键点：

- 证书和私钥通过 **volume 挂载** 注入容器
- `command` 中的 `-c ssl=on` 显式开启 SSL
- `ssl_cert_file` 和 `ssl_key_file` 指向容器内的挂载路径

## 启动与验证

### 重启容器

```bash
docker compose up -d
```

### 检查 SSL 是否开启

进入容器：

```bash
docker exec -it postgres psql -U admin -d iding
```

执行：

```sql
SHOW ssl;
```

返回 `on` 表示 SSL 已开启成功。

## Navicat 连接配置

### 基本配置

| 字段 | 值 |
|------|-----|
| Host | 服务器 IP |
| Port | 5432 |
| User | admin |
| Password | your_password |

### SSL 配置

在 Navicat 的 SSL 选项卡中：

- **SSL Mode**：选择 `require`

或根据需要选择更严格的模式：

- `verify-ca`：需要客户端验证 CA 证书
- `verify-full`：验证证书 + 主机名

## 证书分发说明

| 文件 | 是否可分发 | 说明 |
|------|-----------|------|
| `server.crt` | ✅ 可以 | 公钥证书，可发送给客户端 |
| `server.key` | ❌ 禁止 | 私钥，**绝对不能泄露** |

## 常见问题（踩坑总结）

### 启动失败：找不到证书

**错误信息**：

```
could not load server certificate file "server.crt"
```

**原因**：

- Docker 未正确挂载证书文件
- `command` 中配置的路径与实际挂载路径不一致

**解决**：检查 `volumes` 挂载和 `ssl_cert_file` 路径是否一致。

### 权限错误

**错误信息**：

```
FATAL: private key file has group or world access
```

**解决**：

```bash
chmod 600 server.key
```

PostgreSQL 强制要求私钥文件权限为 `600`，否则拒绝启动。

### Navicat 无法连接

**可能原因**：

- SSL mode 不匹配（服务端开启了 SSL，客户端却未启用）
- 自签名证书未在客户端信任

**解决**：在 Navicat 中将 SSL Mode 设为 `require`（不验证证书），或导入证书后使用 `verify-ca`。

## 架构建议

在实际生产或小型项目中，更推荐以下方案：

### 方案 A（推荐）

- PostgreSQL **不对公网开放**
- 使用 SSH 隧道访问数据库
- 数据库仅监听 `127.0.0.1` 或内网 IP

### 方案 B

- API 层访问数据库
- 数据库仅内网通信
- 应用层处理鉴权与加密

## 总结

PostgreSQL SSL 的几个要点：

1. **本质是传输加密**，而非身份认证系统
2. **Docker 环境需要手动挂载证书**，注意路径和权限
3. 自签名证书足以满足内网加密需求
4. 对于个人服务器或小工具系统，SSL 并非必须，但**公网访问场景下强烈建议开启**
5. 更安全的做法是 **不暴露数据库端口到公网**，通过 SSH 隧道或内网访问
