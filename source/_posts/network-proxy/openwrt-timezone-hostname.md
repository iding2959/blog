---
title: OpenWrt 修改时区与主机名称的两种方式（Web 网页端 + SSH 命令行）
date: 2026-04-10 11:43:00
description: 在 OpenWrt 系统中，正确设置时区和主机名是基础但重要的配置步骤。本文介绍通过 LuCI 网页后台和 SSH 命令行两种方式快速完成时区与主机名的修改。
keywords: OpenWrt, 时区设置, 主机名, Hostname, SSH, LuCI
categories: 网络与代理
tags:
  - OpenWrt
  - Linux
  - SSH
  - Homelab
---

刚刷好 OpenWrt 或者新部署了一台软路由，有两项基础配置建议第一时间搞定：**时区** 和 **主机名**。

时区不对会导致日志时间错乱、定时任务跑偏；主机名不改的话，路由器列表里全是默认的 `OpenWrt`，设备多了根本分不清谁是谁。

下面分别介绍这两种修改的 **Web 网页端（LuCI）** 和 **SSH 命令行** 操作方法，选你觉得顺手的方式就行。

## ⏰ 修改时区

### 方案一：Web 网页端

1. 打开并登录 OpenWrt 网页后台（LuCI）
2. 左侧菜单依次点击：**系统 (System) → 系统 (System)**
3. 在"常规设置"区域找到 **时区 (Timezone)** 下拉框
4. 国内用户选择 `Asia/Shanghai`（对应 UTC+8）
5. 点击右下角 **保存并应用 (Save & Apply)**

![时区设置示意]()

> 💡 如果你发现时区列表里选项太多不好找，直接在浏览器页面按 `Ctrl+F` 搜索 `Shanghai` 即可快速定位。

### 方案二：SSH 命令行

SSH 连上 OpenWrt 后，两条命令搞定：

```bash
# 1. 设置时区为 Asia/Shanghai（UTC+8）
uci set system.@system[0].zonename='Asia/Shanghai'
uci set system.@system[0].timezone='CST-8'

# 2. 提交并重启系统服务
uci commit system && /etc/init.d/system restart
```

执行完后可以用 `date` 命令验证当前时间是否已经变成北京时间：

```bash
date
# 输出示例: Sat Jul  4 18:30:00 CST 2026
```

## 🏷️ 修改主机名

### 方案一：Web 网页端（最直观）

1. 打开并登录 OpenWrt 网页后台（LuCI）
2. 左侧菜单依次点击：**系统 (System) → 系统 (System)**
3. 在"常规设置"区域找到 **主机名 (Hostname)** 输入框（默认通常是 `OpenWrt`）
4. 改成你想要的名字（建议使用英文、数字或连字符 `-`，**不建议用中文**）
5. 点击右下角 **保存并应用 (Save & Apply)**

![主机名设置示意]()

修改完成后，浏览器页面的标题栏就会显示新的主机名。

### 方案二：SSH 命令行（最快）

如果你习惯敲命令，SSH 连上后直接复制运行下面两行，一秒搞定：

```bash
# 1. 使用 uci 工具直接修改系统主机名（把 "My-OpenWrt" 换成你想要的名字）
uci set system.@system[0].hostname='My-OpenWrt'

# 2. 提交并应用修改
uci commit system && /etc/init.d/system restart
```

### 💡 小提示

修改完成后，终端左下角的提示符（比如 `root@OpenWrt:~#`）可能不会立刻刷新。这时候只需要输入 `exit` 退出当前 SSH 连接，重新连进来，就能看到它已经变成 `root@你改的名字:~#` 了！

```bash
exit
ssh root@你的新主机名    # 或者直接用 IP 连接
```

## 📋 总结

| 配置项 | Web 路径 | SSH 命令 |
|--------|---------|----------|
| 时区   | 系统 → 系统 → 时区 | `uci set system.@system[0].zonename='Asia/Shanghai'` |
| 主机名 | 系统 → 系统 → 主机名 | `uci set system.@system[0].hostname='新名称'` |

两条配置共用同一个提交命令：`uci commit system && /etc/init.d/system restart`，可以改完一起提交，不用分两次重启服务。

这两项配置虽然简单，但属于软路由到手后的"必做项"，花一分钟设好，后面使用体验会舒服很多。
