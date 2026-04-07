---
title: 开启 PVE 虚拟机的 Serial TTY 实现无头服务器连接
date: 2026-02-18 17:00
categories:
  - 工具
tags: [PVE, Proxmox, 虚拟机, Serial Console, 运维]
---

在管理无头（Headless）服务器或虚拟机时，没有图形界面，SSH 虽然常用，但有时候内核崩溃或网络配置出错后 SSH 就连不上了。这时候 Serial Console（串口控制台）就派上用场了——它直接通过串口与虚拟机通信，不依赖网络，只要串口通了就能进入系统。

本文记录如何在 PVE 虚拟机中开启 Serial TTY，即让虚拟机通过 `ttyS0` 暴露一个串口终端，方便在 PVE Web UI 或命令行中直接连接。

## 1. 修改 GRUB 引导参数

首先编辑 GRUB 配置，为内核添加串口参数：

```bash
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="console=tty0 console=ttyS0,115200 /' /etc/default/grub
```

这条命令做了两件事：
- `console=tty0`：保留图形控制台
- `console=ttyS0,115200`：将串口 `ttyS0` 也作为控制台，波特率设为 `115200`

然后重新生成 GRUB 配置：

```bash
sudo update-grub
```

执行后会扫描可用的内核并更新引导配置，类似输出如下：

```text
Sourcing file `/etc/default/grub'
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.0-107-generic
Found initrd image: /boot/initrd.img-6.8.0-107-generic
Warning: os-prober will not be executed to detect other bootable partitions.
Systems on them will not be added to the UEFI boot configuration.
Check GRUB_DISABLE_OS_PROBER documentation entry.
Adding boot menu entry for UEFI Firmware Settings ...
done
```

## 2. 启用 Serial Getty 服务

GRUB 配置好后，还需要让系统启动后自动在 `ttyS0` 上启动一个登录终端。使用 systemd 的 `serial-getty` 服务：

```bash
sudo systemctl enable --now serial-getty@ttyS0.service
```

这会创建一个持久化的服务，开机自动启动，无需每次手动运行。

## 3. 在 PVE 中添加串口硬件

如果虚拟机是 QEMU/KVM 类型（`qm`），还需要在 PVE 中为虚拟机添加一个串口设备，否则虚拟机内部配置好了也没用。

**通过 PVE Web UI 操作：**

1. 选择目标虚拟机 -> **硬件** -> **添加** -> **串口设备**
2. 串口类型选择 `Socket` 或直接使用宿主机的 `ttyS0`

**或者通过命令行操作：**

```bash
# 查看当前虚拟机配置
qm config <VM_ID>

# 添加一个串口设备（类型为 socket）
qm set <VM_ID> -serial0 socket

# 如果要映射到宿主机的物理串口
qm set <VM_ID> -serial0 /dev/ttyS0
```

添加后虚拟机需要重启才能生效。

## 4. 验证 Serial Console 是否正常

虚拟机重启后，可以通过以下方式测试连接：

**方式一：通过 PVE 命令行连接**

```bash
# 使用 qm 的终端功能（推荐，已内置）
qm terminal <VM_ID>

# 或者用 screencpy（较老的方式）
qm screencpy <VM_ID>
```

**方式二：直接用 socat 连接串口 socket**

```bash
# 连接虚拟机的串口 socket
socat -,raw,echo=0,escape=0x1c /run/pve/qemu-server/<VM_ID>.serial0

# 退出时按 Ctrl+C
```

**方式三：通过 SSH 登录后直接访问本地串口**

```bash
# 如果已经通过 SSH 登录到 PVE 宿主机
cu -l /dev/ttyS0 -s 115200
```

## 5. 内核参数详解

以下是常用串口内核参数的含义，便于按需调整：

| 参数 | 说明 |
|------|------|
| `console=ttyS0` | 将 `ttyS0` 设为主控制台 |
| `console=tty0` | 保留图形虚拟控制台 |
| `console=ttyS0,115200` | 指定波特率为 115200 |
| `ttyS0` | 启用第一个串口终端 |

波特率 `115200` 是最常用的标准值，兼容性最好。如果设备不支持，可以尝试 `57600` 或 `9600`。

## 6. 常见问题排查

### 虚拟机启动后串口无输出

**检查项：**
1. 虚拟机是否已添加串口硬件（PVE 侧）
2. GRUB 是否已正确更新：`grep console /boot/grub/grub.cfg`
3. `serial-getty` 服务是否运行：`systemctl status serial-getty@ttyS0.service`

### 连接后只有光标闪烁，无法输入

这通常是 `getty` 服务未正确启动。尝试手动重启：

```bash
sudo systemctl restart serial-getty@ttyS0.service
```

### 波特率不匹配

确保连接端使用的波特率与 GRUB 配置一致（默认为 `115200`）。常见的错误率有 `9600`、`57600`、`115200`。

## 7. 适用场景总结

| 场景 | 推荐程度 | 说明 |
|------|----------|------|
| 内核 panic 调试 | 必开 | 网络断了也能看到崩溃日志 |
| 无头服务器管理 | 推荐 | 不依赖 SSH，网络配置失误也不怕 |
| 批量虚拟机初始化 | 辅助 | Cloud-Init + Serial Console 配合使用 |
| 日常使用 | 可选 | 有 SSH 就够用了 |

## 总结

开启 Serial TTY 的核心步骤就三步：

1. **GRUB 加参数**：`console=ttyS0,115200`
2. **启动 getty**：`systemctl enable serial-getty@ttyS0.service`
3. **PVE 挂串口**：`qm set <VM_ID> -serial0 socket`

完成后，无论虚拟机网络是否正常，都可以通过 PVE 的终端功能连接到虚拟机，是运维工作中非常实用的保底手段。
