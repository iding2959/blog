---
title: WSL2 虚拟磁盘压缩瘦身指南（diskpart 一键回收空间）
date: 2026-05-07 16:00:00
description: WSL2 的 ext4.vhdx 虚拟磁盘只会膨胀不会自动缩小，即使删除了文件，Windows 硬盘空间也不会释放。本文介绍使用 diskpart 对虚拟磁盘进行压缩的完整步骤，真正回收被占用的空间。
keywords: WSL2, vhdx, 磁盘压缩, diskpart, compact, 虚拟磁盘瘦身, Windows, 硬盘空间释放
categories: 基础设施
tags:
  - WSL2
  - Windows
  - Ubuntu
  - ext4
---

## 问题背景

WSL2 的 Linux 发行版数据存储在 Windows 宿主机的一个 `.vhdx` 虚拟磁盘文件中（通常位于 `D:\WSL\<发行版名>\ext4.vhdx`）。即使 WSL2 默认使用稀疏文件（Sparse VHDX），这个文件依然存在一个很"坑"的特性：

**虚拟磁盘只会动态增长，不会自动缩小。**

举个例子：你在 Ubuntu 里编译了一个大项目，产生了 20G 的临时文件，`ext4.vhdx` 膨胀到了 25G。之后你把那些临时文件删了，Ubuntu 里 `df -h` 显示只用了 5G，但在 Windows 文件资源管理器里，`ext4.vhdx` 依然占据 25G 的硬盘空间。

## 为什么会这样？

WSL2 的虚拟磁盘本质上是一个稀疏分配的 VHDX 文件。稀疏分配（Sparse）意味着文件实际大小 = 实际写入过的数据量，而不是虚拟磁盘的容量上限。

但问题在于：**WSL2 只做了"标记空间为可用"这件事，并没有通知 Windows 宿主机回收这部分空闲区域。** 对于宿主机来说，那些曾经被写入过、后来被 Linux 标记为"已删除"的区块，仍然是"有效数据"。

解决思路也很直接：用工具对虚拟磁盘执行一次 **Compact（压缩）** 操作，把内部已标记为空闲的区块真正释放回宿主机。

## 准备工作

> ⚠️ 操作前请确保 WSL 中的重要工作已经保存。

### 第一步：彻底关闭 WSL

压缩操作要求虚拟磁盘文件不被任何进程占用，因此必须先关闭所有 WSL 实例。

打开 **Windows PowerShell**（建议以管理员身份运行），执行：

```powershell
wsl --shutdown
```

确认所有实例已停止：

```powershell
wsl --list --verbose
```

输出中所有发行版的 `STATE` 都应为 `Stopped`。

## 核心步骤：diskpart 压缩

`diskpart` 是 Windows 自带的磁盘管理命令行工具，无需安装任何第三方软件。

在 PowerShell 中输入 `diskpart` 进入交互模式：

```powershell
diskpart
```

你会看到提示符变为 `DISKPART>`，然后按顺序执行以下命令：

### 1. 选择虚拟磁盘文件

```plaintext
DISKPART> select vdisk file="D:\WSL\Ubuntu2404\ext4.vhdx"
```

> 路径请替换为你自己的实际路径。如果不确定路径，可以用 `wsl --list --verbose` 查看发行版名称，然后去对应的安装目录下找 `.vhdx` 文件。

选择成功后，diskpart 会提示已选择虚拟磁盘文件。

### 2. 以只读模式挂载

```plaintext
DISKPART> attach vdisk readonly
```

只读挂载是压缩前的必要步骤，它让 diskpart 能够读取磁盘内部的空闲空间信息，同时又不会修改任何数据。

### 3. 执行压缩

```plaintext
DISKPART> compact vdisk
```

这是核心步骤——diskpart 会分析虚拟磁盘内部哪些区块是真正被占用的、哪些是空闲的，然后把空闲区块从宿主机文件中释放。**执行时间取决于虚拟磁盘大小和硬盘速度**，通常在几秒到几分钟之间。

压缩进度和结果会直接显示在当前窗口中。

### 4. 分离并退出

```plaintext
DISKPART> detach vdisk
DISKPART> exit
```

至此，压缩完成！

## 验证结果

回到 `.vhdx` 文件所在的目录查看大小：

```powershell
Get-ChildItem "D:\WSL\Ubuntu2404\ext4.vhdx" | Select-Object Name, @{Name="Size(GB)";Expression={[math]::Round($_.Length/1GB,2)}}
```

或者在文件资源管理器中右键查看属性，你会发现文件大小已经有了明显缩水，硬盘空间真正被释放了。

## 一键脚本

如果你不想每次都手动输入 diskpart 命令，可以把上述步骤写成一个批处理脚本 `compact-wsl.ps1`：

```powershell
# compact-wsl.ps1
# 使用前请先保存 WSL 中的工作，然后以管理员身份运行

param(
    [string]$VhdxPath = "D:\WSL\Ubuntu2404\ext4.vhdx"
)

Write-Host "正在关闭 WSL..." -ForegroundColor Yellow
wsl --shutdown
Start-Sleep -Seconds 3

Write-Host "开始压缩虚拟磁盘: $VhdxPath" -ForegroundColor Yellow

$script = @"
select vdisk file="$VhdxPath"
attach vdisk readonly
compact vdisk
detach vdisk
exit
"@

$script | diskpart

Write-Host "压缩完成！" -ForegroundColor Green

# 显示压缩后大小
Get-ChildItem $VhdxPath | ForEach-Object {
    $sizeGB = [math]::Round($_.Length / 1GB, 2)
    Write-Host "当前虚拟磁盘大小: ${sizeGB} GB" -ForegroundColor Green
}
```

以后只需要右键以管理员身份运行这个脚本即可。

## 常见问题

### Q: 压缩会影响 WSL 里的数据吗？

不会。`compact vdisk` 只是释放已经被 Linux 标记为空闲的空间，不会触碰任何有效数据。而且我们是以 `readonly` 模式挂载的，对原数据零风险。

### Q: 需要多久操作一次？

不需要固定周期。当你发现 WSL 里删了大量文件但 Windows 硬盘空间没有明显释放时，做一次压缩就好。

### Q: 操作失败提示"文件被占用"？

确保执行了 `wsl --shutdown`。如果仍然提示被占用，重启一次 Windows 后再试。

### Q: 能不能让 WSL2 自动回收空间？

目前 WSL2 本身没有内置的自动压缩机制。不过微软在较新的 WSL 版本中加入了 `[wsl2] sparseVhd=true` 的 `.wslconfig` 配置项（默认已启用），这只是保证新数据稀疏写入，并不能回收已膨胀的空间。手动 compact 仍是唯一可靠的方式。

## 小结

WSL2 虚拟磁盘膨胀是个老生常谈的问题，好在解决起来非常简单：

1. `wsl --shutdown` 关闭 WSL
2. `diskpart` → `compact vdisk` 压缩虚拟磁盘
3. 硬盘空间回来了 🎉

建议收藏本文或把上面的 PowerShell 脚本存下来，以备不时之需。
