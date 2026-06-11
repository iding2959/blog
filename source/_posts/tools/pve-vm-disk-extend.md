---
title: PVE 虚拟机 Linux 系统盘扩容指南（ext4+LVM）
date: 2026-02-21 09:00:00
categories:
  - 工具
  - PVE
tags:
  - PVE
  - Proxmox
  - 虚拟机
  - Linux
  - LVM
  - ext4
  - 运维
---

在 PVE 环境中创建的 Linux 虚拟机（尤其是使用 Q35 虚拟化类型），默认分配的磁盘空间可能不够用。本文详细介绍如何在虚拟机内部在线扩容 ext4 文件系统，整个过程无需重启。

## 0. 前置知识

在扩容之前，先了解当前磁盘的层次结构：

```text
物理磁盘 /dev/sda
  ├─ /dev/sda1  (1G, EFI 分区)
  ├─ /dev/sda2  (2G, /boot 分区)
  └─ /dev/sda3  (剩余空间, PV 物理卷)
       └─ ubuntu-vg (LVM 卷组)
            └─ ubuntu-lv (LVM 逻辑卷) → 挂载为 /
```

典型的 Ubuntu 安装使用 **LVM（逻辑卷管理）**，这使得在线扩容变得非常安全。

## 1. 查看当前磁盘状态

```bash
lsblk
```

输出示例：
```
NAME                      MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
sda                         8:0    0   512G  0 disk 
├─sda1                      8:1    0     1G  0 part /boot/efi
├─sda2                      8:2    0     2G  0 part /boot
└─sda3                      8:3    0 252.9G  0 part 
  └─ubuntu--vg-ubuntu--lv 252:0    0 252.9G  0 lvm  /
sdb                         8:16   0   328G  0 disk /mnt/jfs_cache
```

可以看到：
- 磁盘总容量已通过 PVE 扩展为 **512G**
- 但 sda3 分区仍是 **252.9G**（旧大小）
- 逻辑卷 ubuntu-lv 也是 252.9G，挂载在根目录 `/`

> **提示**：如果提示 `growpart` 命令不存在，安装它：
> ```bash
> sudo apt update && sudo apt install cloud-guest-utils -y
> ```

## 2. 扩展分区表

首先用 `growpart` 扩展分区 3，使其占满整个磁盘：

```bash
sudo growpart /dev/sda 3
```

输出：
```
CHANGED: partition=3 start=6397952 old: size=530472927 end=536870878 new: size=1067343839 end=1073741790
```

> **注意**：命令格式是 `growpart 设备 分区号`，分区号前无空格。

## 3. 扩展 LVM 物理卷

分区扩展后，需要告诉 LVM 物理卷容量已变化：

```bash
sudo pvresize /dev/sda3
```

输出：
```
Physical volume "/dev/sda3" changed
1 physical volume(s) resized or updated
```

可以用 `pvs` 验证：
```bash
sudo pvs
```

## 4. 扩展 LVM 逻辑卷

将卷组中全部可用空间分配给逻辑卷：

```bash
sudo lvextend -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv
```

输出：
```
Size of logical volume ubuntu-vg/ubuntu-lv changed from <252.95 GiB (64754 extents) to <508.95 GiB (130290 extents).
Logical volume ubuntu-vg/ubuntu-lv successfully resized.
```

> `-l +100%FREE` 表示使用全部可用空间。如果只想扩容一半，可以用 `lvextend -L +100G`。

## 5. 扩展文件系统

最后一步，将 ext4 文件系统扩展到新的逻辑卷大小：

```bash
sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
```

输出：
```
resize2fs 1.47.0 (5-Feb-2023)
Filesystem at /dev/mapper/ubuntu--vg-ubuntu--lv is mounted on /; on-line resizing required
old_desc_blocks = 32, new_desc_blocks = 64
The filesystem on /dev/mapper/ubuntu--vg-ubuntu--lv is now 133416960 (4k) blocks long.
```

> 关键点：**resize2fs 支持在线操作**，无需卸载文件系统或重启机器。

## 6. 验证结果

```bash
df -h
```

输出：
```
Filesystem                         Size  Used Avail Use% Mounted on
/dev/mapper/ubuntu--vg-ubuntu--lv  501G  151G  329G  32% /
```

磁盘空间已从 **252.9G** 扩容到 **501G**，且原数据完好无损。

或者再次查看 lsblk：

```bash
lsblk
```

```
NAME                      MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
sda                         8:0    0   512G  0 disk 
├─sda1                      8:1    0     1G  0 part /boot/efi
├─sda2                      8:2    0     2G  0 part /boot
└─sda3                      8:3    0 508.9G  0 part 
  └─ubuntu--vg-ubuntu--lv 252:0    0 508.9G  0 lvm  /
```

sda3 现在是 508.9G，逻辑卷也是 508.9G。

## 7. 一键命令

完整流程可以合并为一行：

```bash
sudo growpart /dev/sda 3 && sudo pvresize /dev/sda3 && sudo lvextend -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv && sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
```

## 8. XFS 文件系统扩容（补充）

如果你的逻辑卷使用的是 **XFS** 文件系统（常见于 CentOS/RHEL），最后一步需要用 `xfs_growfs` 替代 `resize2fs`：

```bash
# XFS 在线扩容
sudo xfs_growfs /mount/point

# 例如根目录
sudo xfs_growfs /
```

## 总结

| 步骤 | 命令 | 作用 |
|------|------|------|
| 1 | `growpart /dev/sda 3` | 扩展分区表 |
| 2 | `pvresize /dev/sda3` | 通知 LVM 物理卷容量变化 |
| 3 | `lvextend -l +100%FREE /dev/mapper/xxx` | 扩展逻辑卷 |
| 4 | `resize2fs /dev/mapper/xxx` | 扩展 ext4 文件系统 |

整个过程可以在 **在线状态** 下完成，无需停机，适合生产环境操作。