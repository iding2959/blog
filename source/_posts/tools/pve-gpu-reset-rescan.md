---
title: PVE 显卡“掉卡”自救：免重启强制重置 PCIe 设备
date: 2026-06-23 10:00:00
description: 当 PVE 宿主机显卡突然“掉卡”导致虚拟机无法开机时，通过命令行强制移除并重新扫描 PCIe 设备，免重启恢复可用性。
keywords: PVE, 显卡掉卡, PCIe 重置, rescan, GPU 直通, 虚拟机自救
categories:
  - 工具
  - 虚拟化
tags:
  - PVE
  - GPU
  - PCIe
  - 虚拟化
---

## 背景

在使用 PVE（Proxmox VE）做 GPU 直通时，偶尔会遇到**显卡"掉卡"**的情况：宿主机还在正常运行，但显卡从 PCIe 总线上"消失"了，导致依赖该显卡的虚拟机无法启动，或者正在运行的虚拟机突然异常。

传统做法是直接重启整个 PVE 宿主机——但生产环境里重启代价很大，所有虚拟机都得跟着停。

其实有一种**纯软件层面的自救手段**，相当于在操作系统层面对 PCIe 设备执行"拔出再插回"，大多数情况下能让显卡重新被识别，虚拟机恢复正常。

## 操作步骤

### 1. 找到显卡的 PCIe 编号

通过 SSH 登录 PVE 宿主机，先确认显卡在哪个 PCIe 插槽上：

```bash
lspci | grep -i NVIDIA  # 你的显卡类型
```

输出示例：

```
01:00.0 3D controller: NVIDIA Corporation AD104GL [L4] (rev a1)
21:00.0 3D controller: NVIDIA Corporation AD104GL [L4] (rev a1)
41:00.0 3D controller: NVIDIA Corporation AD104GL [L4] (rev a1)
43:00.0 3D controller: NVIDIA Corporation AD102GL [L40] (rev a1)
```

记住目标显卡的编号，例如 `0000:01:00.0`（格式为 `0000:总线:设备.功能`）。多卡环境下会有多条输出，每张卡的编号不同，操作时选择你需要重置的那张即可。

### 2. 强制"拔掉"设备

```bash
echo 1 > /sys/bus/pci/devices/0000\:01\:00.0/remove
```

> **注意**：路径中的冒号前要加反斜杠转义。请将 `01:00.0` 替换为你实际的 PCI 编号。

执行后，显卡在 `lspci` 中就会消失。等待 2 秒让系统完成清理。

### 3. 重新扫描 PCIe 总线

```bash
sleep 2
echo 1 > /sys/bus/pci/rescan
```

系统会重新枚举所有 PCIe 设备，显卡应该会重新出现在 `lspci` 列表中。

### 4. 验证恢复

```bash
lspci | grep -i NVIDIA
```

如果能再次看到你的显卡，说明"掉卡"已自救成功，虚拟机可以正常开机了。

### 一键脚本

为了方便下次使用，可以把以上命令保存为一个脚本 `/usr/local/bin/pve-gpu-reset`：

```bash
#!/bin/bash
# PVE 显卡强制重置脚本
# 用法: pve-gpu-reset 01:00.0

if [ -z "$1" ]; then
    echo "用法: $0 <PCI_ID>"
    echo "示例: $0 01:00.0"
    echo "先执行 lspci | grep -i NVIDIA 查看显卡编号"
    exit 1
fi

PCI_ID=$1
DEVICE_PATH="/sys/bus/pci/devices/0000:${PCI_ID}"

if [ ! -d "$DEVICE_PATH" ]; then
    echo "错误: 设备 $DEVICE_PATH 不存在"
    exit 1
fi

echo "正在移除设备 0000:${PCI_ID} ..."
echo 1 > "$DEVICE_PATH/remove"

sleep 2

echo "正在重新扫描 PCIe 总线..."
echo 1 > /sys/bus/pci/rescan

echo "完成！验证结果："
lspci | grep -i NVIDIA
```

赋予执行权限：

```bash
chmod +x /usr/local/bin/pve-gpu-reset
```

以后掉卡直接：

```bash
pve-gpu-reset 01:00.0
```

## 适用场景与注意事项

| 场景 | 是否适用 |
|------|----------|
| 显卡在 `lspci` 中消失 | ✅ 适用 |
| 虚拟机报 "device not found" | ✅ 适用 |
| 显卡出现在 `lspci` 中但显示为 `(rev ff)` | ✅ 可以尝试 |
| 显卡驱动内核 panic | ⚠️ 可能需要重启 |
| 硬件物理故障（散热、供电） | ❌ 不适用，应排查硬件 |

- **不影响其他虚拟机**：该操作只针对指定的 PCIe 设备，宿主机和其他使用不同设备的虚拟机不受影响。
- **正在使用该显卡的虚拟机** 执行前需要先关闭。
- 此方法本质上是触发 Linux 内核的 PCIe 热插拔机制，比 `vfio-pci` 解绑再重新绑定更底层。

## 参考

- [Linux Kernel PCI Documentation](https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-bus-pci)
- Proxmox VE Wiki: [PCI Passthrough](https://pve.proxmox.com/wiki/PCI_Passthrough)
