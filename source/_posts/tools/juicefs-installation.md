---
title: Ubuntu 挂载 JuiceFS 分布式文件系统
date: 2026-03-07 10:00:00
categories:
  - 工具
  - Linux
tags:
  - JuiceFS
  - Linux
  - 分布式文件系统
  - Ubuntu
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

## 3. 配置持久化挂载

编辑 `/etc/fstab` 文件，将物理盘挂载和 JuiceFS 挂载写入。**顺序非常重要**，必须先挂载物理磁盘，再挂载 JuiceFS：

```bash
sudo nano /etc/fstab
```

添加以下两行：

```text
# A. 先挂载物理缓存盘
/dev/sdb  /mnt/jfs_cache  ext4  defaults  0  0

# B. 再挂载 JuiceFS (使用独立缓存盘，限制缓存为 110G)
redis://192.168.0.247:6380/0  /mnt/models  juicefs  _netdev,cache-dir=/mnt/jfs_cache,cache-size=112640,allow_other  0  0
```
### 4. 查看是否挂载成功
```bash
sudo mount -a
```

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

### 5. 磁盘确认

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

## 5. 常见问题

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
