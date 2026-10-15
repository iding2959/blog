---
title: PVE 虚拟机 XFS 系统盘在线扩容指南（非 LVM）
date: 2026-10-15 16:20:00
description: 当 PVE 虚拟机使用 XFS 文件系统时如何在线扩容：growpart 扩分区、xfs_growfs 扩文件系统，并对照 ext4 说明两者在工具、作用对象和缩容能力上的关键差异。
keywords: Proxmox VE, PVE, XFS, xfs_growfs, growpart, 磁盘扩容
categories: 基础设施
tags:
  - PVE
  - Linux
  - XFS
  - Ubuntu
---

上一篇文章[《PVE 虚拟机 Linux 系统盘扩容指南（ext4+LVM）》](/2026/02/pve-vm-disk-extend/)讲的是 **LVM + ext4** 的标准路子：`growpart` → `pvresize` → `lvextend` → `resize2fs`。

这篇专门讲 **XFS**。XFS 常见于 CentOS/RHEL 系，也是 openEuler、Anolis、麒麟等国产发行版的默认根文件系统；在 Ubuntu cloud image 手动分区、或者 PVE 里手工建的 VM 上也经常见到。

两者**流程骨架一样，但最后一步完全不同**，而且 XFS 有一条 ext4 没有的硬限制：**只能扩，不能缩**。下面就按实际排障顺序走一遍。

## 0. 先判断你该看哪一篇

```text
lsblk 看到 / 挂在什么上面？
├─ /dev/mapper/xxx-xxx (LVM 逻辑卷)
│   ├─ 文件系统是 ext4  → 看旧文（resize2fs）
│   └─ 文件系统是 XFS   → 看本文第 6.1 节（LVM + XFS）
└─ /dev/sdaN (裸分区)
    ├─ 文件系统是 ext4  → 看旧文
    └─ 文件系统是 XFS   → 看本文主线
```

一条命令同时看清这两件事：

```bash
lsblk -f
findmnt -no SOURCE,FSTYPE /
```

本文的实操环境是一台裸分区 + XFS 的 Ubuntu 22.04 虚拟机（`/dev/sda2` 直接挂 `/`，外面没有 LVM）。

## 1. XFS 与 ext4 的四个关键差异

先把差异摆出来，后面每一步的"为什么"就都好理解了。

| 维度 | ext4 | XFS |
|------|------|-----|
| 扩容工具 | `resize2fs` | `xfs_growfs` |
| **作用对象** | **块设备**（`/dev/sda2`、`/dev/mapper/xxx`） | **挂载点**（`/`、`/data`）⚠️ |
| 在线扩容前提 | 挂载中可在线扩，也支持离线扩 | **必须处于挂载状态**，未挂载无法扩 |
| 缩容 | 支持（需先 `e2fsck`，离线进行） | ❌ **不支持**，官方明确只能扩 |
| 元数据组织 | 块组 + 块组描述符 | AG（Allocation Group）分配组 |
| 一致性修复 | `e2fsck` | `xfs_repair`（必须卸载后执行） |

**最容易踩的就是第二行**：`xfs_growfs` 吃的是挂载点，不是设备。习惯了 `resize2fs /dev/sda2` 的人，第一次敲 `xfs_growfs /dev/sda2` 必然报错：

```text
xfs_growfs: /dev/sda2 is not a mounted XFS filesystem
```

## 2. PVE 侧：先把虚拟磁盘撑大

Web UI 路径：**虚拟机 → 硬件 → 选中磁盘 → 磁盘操作 → 调整大小**。

命令行等价操作：

```bash
# 增量扩容：在原有基础上 +256G
qm resize 100 scsi0 +256G

# 也可以直接给绝对值
qm resize 100 scsi0 356G
```

扩容后 PVE 侧的配置立刻反映出来：

```bash
qm config 100 | grep scsi0
# scsi0: local-hdd:100/vm-100-disk-1.qcow2,iothread=1,size=356G
```

> 这一步只是把 qcow2 这个"容器"变大了。**虚拟机里的分区和文件系统完全没变**，必须进系统继续操作。
>
> 好消息：qcow2 支持**在线扩容**，虚拟机不用关机；客人机也能自动感知（见下一节）。

## 3. guest 侧：确认内核已识别新容量

```bash
lsblk
```

```text
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda      8:0    0  356G  0 disk 
├─sda1   8:1    0    1G  0 part /boot/efi
└─sda2   8:2    0 98.9G  0 part /

df -h /
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/sda2        99G   14G   86G  14% /
```

注意看：**磁盘已经是 356G，但分区 sda2 还是 98.9G** —— 这正是我们要处理的对象。

确认内核真的读到了新容量：

```bash
cat /sys/class/block/sda/size
# 746586112   （× 512B = 356 GiB）
```

### 如果内核没识别到新容量

`virtio-scsi`（PVE 默认的 `scsihw: virtio-scsi-single`）支持容量变更通知，通常**不需要手动干预**。但如果用的是老式 IDE/SATA 控制器，或者磁盘是热插的，可能要在 guest 里手动触发重扫：

```bash
echo 1 | sudo tee /sys/class/block/sda/device/rescan
# 多路径/SCSI 场景也可以用：
sudo rescan-scsi-bus.sh
```

再跑一次 `lsblk` 确认磁盘容量变了，才继续下一步。

## 4. 扩展分区表：growpart

`growpart` 来自 `cloud-guest-utils` 包，Ubuntu 一般自带；没有就装：

```bash
sudo apt update && sudo apt install -y cloud-guest-utils
```

执行扩容（命令格式是 `growpart 设备 分区号`，**分区号前有空格**）：

```bash
sudo growpart /dev/sda 2
```

```text
CHANGED: partition=2 start=2203648 old: size=207509504 end=209713152 new: size=744382431 end=746586079
```

`start` 没变、`end` 顶到磁盘末尾、`size` 从 207509504 扇区涨到 744382431 扇区 —— 说明分区已经吃满整块磁盘。

此时 `lsblk` 里 sda2 应该显示新的容量：

```text
sda      8:0    0  356G  0 disk 
├─sda1   8:1    0    1G  0 part /boot/efi
└─sda2   8:2    0 354.9G  0 part /
```

但 `df -h` **还是旧的 99G** —— 因为文件系统本身还没扩，这是下一步的事。

### 两个常见的 growpart 失败场景

**① 目标分区不是磁盘上最后一个分区**

`growpart` 只能"向后长"，如果 sda2 后面还跟着 sda3（比如独立 swap），它会直接拒绝：

```text
NOCHANGE: partition 2 is not the last partition
```

处置：先把后面的分区挪走或删掉（`swapoff` + 删除 + 重建），顺序整理好后再扩 sda2。

**② `WARNING: the kernel failed to re-read the partition table`**

分区表内核缓存没刷新。二选一：

```bash
sudo partprobe /dev/sda     # 让内核重读分区表
# 或者
sudo reboot                 # 实在不行重启一次，之后 df 看是否已生效
```

**③ GPT 备份头不在磁盘末尾**

用 `growpart` 扩 GPT 磁盘时偶尔会看到：

```text
WARNING: The backup GPT table is not at the end of the disk
```

这会把分区表往后挪，需要顺手把 GPT 备份头也搬到新的磁盘末尾：

```bash
sudo sgdisk -e /dev/sda
```

## 5. 扩展 XFS 文件系统：xfs_growfs

**关键：参数是挂载点，不是设备。**

```bash
sudo xfs_growfs /
```

```text
meta-data=/dev/sda2              isize=512    agcount=4, agsize=6484672 blks
         =                       sectsz=512   attr=2, projid32bit=1
         =                       crc=1        finobt=1, sparse=0, rmapbt=0
         =                       reflink=1    bigtime=0 inobtcount=0
data     =                       bsize=4096   blocks=25938688, imaxpct=25
         =                       sunit=0      swidth=0 blks
naming   =version 2              bsize=4096   ascii-ci=0, ftype=1
log      =internal log           bsize=4096   blocks=12665, version=2
         =                       sectsz=512   sunit=0 blks, lazy-count=1
realtime =none                   extsz=4096   blocks=0, rtextents=0
data blocks changed from 25938688 to 93047803
```

最后那行 `data blocks changed from A to B` 就是成功标志 —— 数据块数从 25938688 涨到 93047803。

常用参数：

| 参数 | 含义 |
|------|------|
| `-d` | 只扩数据区（默认行为，最常用） |
| `-l` | 扩内部日志区（很少需要） |
| `-n` | **干跑**，只打印当前几何信息不实际扩容，扩容前确认用 |
| `-R` | 实时设备（realtime device）扩容 |

扩容前想先看一眼现状，用干跑：

```bash
sudo xfs_growfs -n /
```

> **XFS 必须处于挂载状态才能扩容**。如果文件系统没挂载，先用 `xfs_growfs` 是行不通的 —— 得先 `mount` 上来再扩（这点和 ext4 的 `resize2fs` 正好相反，后者可以对未挂载设备离线扩）。

## 6. 验证结果

```bash
df -h /
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda2       355G   16G  340G   5% /
```

从 **99G 到 355G**，数据完好、服务不停、没有重启。再确认一次块设备层面：

```bash
lsblk
```

```text
sda      8:0    0  356G  0 disk 
├─sda1   8:1    0    1G  0 part /boot/efi
└─sda2   8:2    0 354.9G  0 part /
```

## 6.1 补充：XFS 跑在 LVM 上怎么办

如果 `lsblk` 显示 `/` 挂在 `/dev/mapper/ubuntu--vg-ubuntu--lv` 这类逻辑卷上，流程比裸分区**多两步**，但最后一步依然是 `xfs_growfs`：

```bash
# 1. 扩分区（假设 PV 在 sda3）
sudo growpart /dev/sda 3

# 2. 通知 LVM 物理卷容量变化
sudo pvresize /dev/sda3

# 3. 扩逻辑卷
sudo lvextend -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv

# 4. 扩 XFS 文件系统 —— 注意这里传的还是挂载点，不是 /dev/mapper/xxx
sudo xfs_growfs /
```

和旧文（ext4）唯一的差别就在第 4 步：ext4 写 `resize2fs /dev/mapper/xxx`，XFS 写 `xfs_growfs /`。

## 7. 一键命令

裸分区 + XFS（本文主线场景）：

```bash
sudo growpart /dev/sda 2 && sudo xfs_growfs /
```

LVM + XFS：

```bash
sudo growpart /dev/sda 3 && sudo pvresize /dev/sda3 && sudo lvextend -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv && sudo xfs_growfs /
```

## 8. 报错速查表

| 报错 | 原因 | 处置 |
|------|------|------|
| `xfs_growfs: /dev/sda2 is not a mounted XFS filesystem` | 把设备当参数了 | 改成挂载点：`xfs_growfs /` |
| `XFS_IOC_FSGEOMETRY: Inappropriate ioctl for device` | 该设备不是 XFS | `file -s /dev/sda2`、`findmnt -no FSTYPE /` 核实类型 |
| `xfs_growfs: data size unchanged` | 分区还没扩，文件系统无空间可长 | 回到第 4 步确认 `growpart` 成功、`lsblk` 分区已变大 |
| `NOCHANGE: partition N is not the last partition` | 目标分区后面还有分区 | 先处理后面的分区（swap 等）再扩 |
| `WARNING: the kernel failed to re-read the partition table` | 内核分区表缓存未刷新 | `partprobe /dev/sda`，或重启 |
| `WARNING: The backup GPT table is not at the end of the disk` | GPT 备份头位置过时 | `sgdisk -e /dev/sda` |
| `xfs_growfs: / is not a mounted XFS filesystem`（明明挂着） | 挂载点写错（如 `/data/` 带尾斜杠或软链路径） | 用 `findmnt` 输出的**真实挂载点** |

## 9. XFS 运维提醒

- **永远记住 XFS 不能缩小**。规划分区时宁可留富余；真要缩容，只有"备份 → 重建文件系统 → 恢复数据"这一条路（`xfsdump` / `xfsrestore` 是配套工具）。
- **`xfs_repair` 必须在卸载状态下跑**。对挂载中的 XFS 执行会直接拒绝甚至造成损坏；根分区要做检查得进 rescue 模式或从 live 介质启动。
- 查看几何信息用 `xfs_info /`，等价于 `xfs_growfs -n /`。
- `xfs_growfs` 是**在线**操作，扩容期间业务读写可以继续，不需要停服务。
- 扩容是"加 AG 或撑大现有 AG"的过程，`agcount` 可能变化；如果扩容后 `agcount` 没变而 `agsize` 变大，也属正常。

## 总结

| 步骤 | 命令（XFS，裸分区） | 作用 |
|------|--------------------|------|
| 1 | `qm resize 100 scsi0 +256G` | PVE 侧撑大虚拟磁盘 |
| 2 | `lsblk` / `cat /sys/class/block/sda/size` | 确认 guest 已识别新容量 |
| 3 | `growpart /dev/sda 2` | 扩展分区表 |
| 4 | `xfs_growfs /` | 扩展 XFS 文件系统（**传挂载点**） |
| 5 | `df -h /` | 验证 |

和 ext4 那篇对照着看，差异其实只有三条：**工具名不同、参数给挂载点而不是设备、XFS 不可缩容**。其余（PVE 侧扩容、`growpart`、在线不重启）完全一致。
