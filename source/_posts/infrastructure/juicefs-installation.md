---
title: Ubuntu 挂载 JuiceFS 分布式文件系统
date: 2026-03-07 10:00:00
description: JuiceFS 分布式文件系统安装与配置教程：对象存储挂载、性能优化、生产环境部署实践。
keywords: JuiceFS, 分布式存储, 对象存储, FUSE, 文件系统
categories: 基础设施
tags:
  - JuiceFS
  - Linux
---

## JuiceFS 简介

JuiceFS 是一个高性能的分布式文件系统，支持将对象存储（如 S3）和 Redis 组合成功能完整的 POSIX 文件系统。本指南详细介绍在 Ubuntu 上安装配置 JuiceFS 的完整流程，适合需要挂载共享存储的场景（如模型存储、AI 训练数据共享等）。

### 前置要求

- Ubuntu 系统（本文基于 Ubuntu 20.04+ / 22.04+ 测试）
- 一个可用的 Redis 实例（用于元数据存储）
- （可选）一块独立的磁盘作为缓存盘

## 1. 安装 JuiceFS 客户端

### 下载并安装

前往 [JuiceFS 官方下载页](https://juicefs.com/zh-cn/download/) 或使用官方一键安装脚本：

```bash
curl -sSL https://d.juicefs.com/install | sh -
```

### 移动到系统路径 

```bash
# 当找不到 juicefs命令时执行
sudo mv juicefs /usr/local/bin/
```

### 创建挂载助手链接

**关键步骤**：让系统 `mount` 命令识别 `juicefs` 文件系统类型：

```bash
sudo ln -s /usr/local/bin/juicefs /sbin/mount.juicefs
```

### 验证安装

```bash
juicefs --version
```

## 2. 准备专用缓存盘

如果机器有独立的磁盘（如 `/dev/sdb`，128G）用作缓存盘，请按以下步骤初始化：

### 2.1 格式化磁盘

```bash
sudo mkfs.ext4 /dev/sdb
```

### 2.2 创建挂载点

```bash
# 物理缓存盘挂载点
sudo mkdir -p /mnt/jfs_cache

# JuiceFS 最终挂载点
sudo mkdir -p /mnt/models

# 确保普通用户可写
sudo chmod 777 /mnt/models
```

## 3. 测试手动挂载

在配置持久化之前，先用手动命令测试能否成功挂载：

```bash
# 先卸载（如果之前有挂载失败的尝试）
sudo umount /mnt/models 2>/dev/null

# 手动挂载 JuiceFS（测试用，后台运行）
sudo juicefs mount -d \
    --cache-dir /mnt/jfs_cache \
    --cache-size 300000 \
    -o allow_other \
    redis://192.168.0.247:6380/0 \
    /mnt/models
```

看到 `OK, xxx is ready at /mnt/models` 即表示挂载成功。

## 5. 查看状态命令

### 5.1 查看挂载点统计信息

```bash
juicefs stats /mnt/models
```

输出示例：
```
juicefs stats /mnt/models
Usage:   juicefs stats <mountpoint>
Flags:   --interval   1s   # 更新间隔（秒）
         --once             # 只输出一次，不持续刷新
```

这个命令会实时显示：
- 当前连接的客户端数量
- 读写吞吐量
- 缓存命中率
- FUSE 操作统计等

### 5.2 查看文件系统整体状态

```bash
sudo juicefs status redis://192.168.0.247:6380/0
```

输出示例：
```
juicefs status redis://192.168.0.247:6380/0
Meta URL:         redis://192.168.0.247:6380/0
Redis Version:    7.0.5
JuiceFS Version:  1.1.0
Total Inodes:     1.2M
Total Space:      20TiB
Used Space:      5.2TiB
Free Space:      14.8TiB
Used Inodes:     256K
Total Sessions:  3
  - 192.168.0.101:/mnt/models (192.168.0.101) [valid]
  - 192.168.0.102:/mnt/models (192.168.0.102) [valid]
```

这个命令显示：
- 文件系统总空间和已用空间
- inode 数量
- 当前连接的客户端会话
- Redis 版本等信息

## 6. （可选）设置容量配额

JuiceFS 默认会显示 1PB 的总容量，如果想显示实际容量，可以设置配额：

```bash
# 设置根目录容量为 20TB（根据实际需求调整）
sudo juicefs quota set redis://192.168.0.247:6380/0 --path / --capacity 20480
```

参数说明：
- `--path /` - 要设置配额的路径
- `--capacity` - 容量大小，单位为 **GiB**

> 注意：这个配额只影响 `df` 命令显示的容量数值，不会限制实际可用空间。

## 7. 配置持久化挂载

测试成功后，将挂载配置写入 `/etc/fstab`，实现开机自动挂载：

```bash
sudo nano /etc/fstab
```

添加以下两行：

```text
# A. 先挂载物理缓存盘
/dev/sdb  /mnt/jfs_cache  ext4  defaults  0  0

# B. 再挂载 JuiceFS (使用独立缓存盘，限制缓存为 300G)
redis://192.168.0.247:6380/0  /mnt/models  juicefs  _netdev,cache-dir=/mnt/jfs_cache,cache-size=300000,allow_other  0  0
```

### 8. 生效持久化配置

```bash
sudo systemctl daemon-reload
sudo mount -a
```

### 9. 查看是否挂载成功

```
safone@fk-gpu-server2:~$ sudo mount -a
mount: (hint) your fstab has been modified, but systemd still uses
       the old version; use 'systemctl daemon-reload' to reload.
2026/04/07 02:16:07.211856 juicefs[1762351] <INFO>: Meta address: redis://192.168.0.247:6380/0 [NewClient@interface.go:578]
2026/04/07 02:16:07.222300 juicefs[1762351] <WARNING>: AOF is not enabled, you may lose data if Redis is not shutdown properly. [checkRedisInfo@info.go:84]
2026/04/07 02:16:07.222748 juicefs[1762351] <INFO>: Ping redis latency: 325.511µs [checkServerConfig@redis.go:3692]
2026/04/07 02:16:07.224575 juicefs[1762351] <INFO>: Data use minio://http://192.168.0.247:19000/jfs-data/jfs-data/modeljfs/ [mount@mount.go:588]
2026/04/07 02:16:07.726620 juicefs[1762351] <INFO>: OK, modeljfs is ready at /mnt/models [checkMountpoint@mount_unix.go:235]
safone@fk-gpu-server2:~$
```

### 10. 磁盘确认

```bash
df -h
```
```
safone@fk-gpu-server2:~$ df -h
Filesystem                    Size  Used Avail Use% Mounted on
tmpfs                          26G  3.3M   26G   1% /run
/dev/mapper/ubuntu--vg-lv--0  2.0T  1.1T  924G  55% /
tmpfs                         126G     0  126G   0% /dev/shm
tmpfs                         5.0M     0  5.0M   0% /run/lock
/dev/sda2                     2.0G  201M  1.6G  11% /boot
tmpfs                          26G   24K   26G   1% /run/user/1000
/dev/sdb                      322G   36K  306G   1% /mnt/jfs_cache
JuiceFS:modeljfs              1.0P   33M  1.0P   1% /mnt/models
```
### 参数说明

| 参数 | 说明 |
|------|------|
| `_netdev` | 等待网络就绪后再挂载，防止启动时挂载失败 |
| `cache-dir` | 指定缓存目录路径 |
| `cache-size` | 缓存大小（单位 MB，112640 = 110G） |
| `allow_other` | 允许非挂载用户访问文件 |

### 生产环境推荐参数

以下参数经过生产环境验证，可有效提升 JuiceFS 稳定性，避免对 NFS 造成额外压力：

| 参数项 | 默认值 | 推荐值 | 作用与优点 |
|--------|--------|--------|------------|
| **缓存大小** | 327680 (320G) | 需根据 `/dev/sdb` 实际大小调整 | 防止磁盘撑爆：确保缓存不会写满物理分区。**避免因缓存盘满导致的写入中断** |
| **异步写入** | 同步写入 (默认) | 不建议开启 `writeback` | 数据安全：因为有项目运行，保持同步写入确保数据必须落到后端存储才返回成功。**掉电不丢数据** |
| **挂载保障** | 无 | `_netdev` | 启动顺序：确保网络服务启动后再挂载。**防止开机时因为网络没通导致挂载失败** |

> **⚠️ 注意**：fstab 中不支持 `attr-cache`、`entry-cache`、`dir-cache` 等参数。这些是 JuiceFS 命令行参数，需要在 `juicefs mount` 命令中单独指定。如果需要调整元数据缓存，请在挂载命令中使用：
> ```bash
> juicefs mount <meta-url> /mnt/models --attrcacheto=60 --entrycacheto=60 --direntrycacheto=60 --update-fstab
> ```

> **注意**：如果你有其他 NFS 或 SMB 共享服务与 JuiceFS 共存，合理的缓存大小和同步写入模式尤为重要。

### 可选：开启 writeback 异步写入模式

如果你对写入性能有极致要求，且可以容忍极小概率的数据丢失（如临时缓存目录），可以开启 `writeback` 模式：

```text
# 确保本地缓存盘先挂载
/dev/sdb  /mnt/jfs_cache  ext4  defaults  0  0

# 开启了 writeback 的 JuiceFS 挂载
redis://192.168.0.247:6380/0  /mnt/models  juicefs  _netdev,cache-dir=/mnt/jfs_cache,cache-size=300000,writeback,allow_other  0  0
```

> **⚠️ 风险提示**：开启 `writeback` 后，数据会先写入本地缓存盘，然后异步同步到后端存储。**在断电、异常关机或 JuiceFS 崩溃时，已写入缓存但未同步的数据可能丢失**。请确保缓存盘上的数据可接受丢失，或用于纯缓存场景。

> **注意**：如果你有其他 NFS 或 SMB 共享服务与 JuiceFS 共存，元数据缓存尤为重要——它可以显著减少对 Redis 的请求频率，避免因高频元数据操作影响其他服务的性能。

### 完整配置示例

```text
/dev/sdb  /mnt/jfs_cache  ext4  defaults  0  0
redis://192.168.0.247:6380/0  /mnt/models  juicefs  _netdev,cache-dir=/mnt/jfs_cache,cache-size=300000,allow_other  0  0
```

配置完成后执行：
```bash
sudo systemctl daemon-reload
sudo mount -a
```



预期结果：同时看到 `/mnt/jfs_cache` 和 `/mnt/models`。

### 缓存确认

```bash
sudo ls -lh /mnt/jfs_cache
```

预期结果：看到一串 UUID 命名的文件夹。

### 权限确认

```bash
touch /mnt/models/test.txt
```

预期结果：普通用户可以成功创建文件。

## 11. 常见问题

### Q: mount -a 没有反应，但也没有报错？

检查 `/etc/fstab` 是否有多余的空行或格式问题，确保每个字段用 Tab 或空格分隔。

### Q: 普通用户无法访问 /mnt/models？

确认添加了 `allow_other` 参数，并检查目录权限为 777 或对应的用户组权限。

### Q: 启动后 JuiceFS 没有自动挂载？

确保 Redis 服务在 JuiceFS 之前启动，`_netdev` 参数可以帮助等待网络就绪。另外确认 `mount.juicefs` 链接已正确创建。

### Q: 如何手动卸载 JuiceFS？

```bash
sudo umount /mnt/models
sudo umount /mnt/jfs_cache
```

## 参考资源

- [JuiceFS 官方文档](https://juicefs.com/docs/zh/)
- [JuiceFS 官方下载页](https://juicefs.com/zh-cn/download/)
- [JuiceFS GitHub 仓库](https://github.com/juicedata/juicefs)

以上就是 Ubuntu 下安装配置 JuiceFS 的完整流程，按照检查清单逐项验证即可确保部署无误。
