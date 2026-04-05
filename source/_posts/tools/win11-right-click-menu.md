---
title: Win11 右键菜单恢复 Win10 风格
date: 2026-01-03 13:00:00
categories:
  - 工具
tags:
  - Windows
  - Win11
  - 注册表
---

很多朋友升级到 Windows 11 后，会对新的右键菜单感到不适应——常用选项被收纳到「显示更多选项」里，每次都要多点一次才能看到想要的内容。其实通过一条注册表命令，就可以把 Win11 的右键菜单恢复成 Win10 的样式。本文就来详细介绍操作步骤。

## 操作步骤

### 第一步：打开管理员终端

用鼠标右键点击「开始」按钮，或者直接按 `Win + X` 组合键，选择 **「Windows 终端（管理员）」**。

![打开 Windows 终端](/source/img/win11setmouce/1openpowershell.png)

### 第二步：输入注册表命令

在终端中粘贴以下命令并按回车：

```powershell
reg.exe add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /f /ve
```

![执行注册表命令](/source/img/win11setmouce/2comand.png)

看到「操作成功完成」的提示后，**重启电脑**即可。

### 第三步：查看效果

重启后，右键菜单就会变成熟悉的 Win10 风格，所有选项一目了然，再也不用多点一次「显示更多选项」了。

下面是修改前（Win11 新样式）和修改后（Win10 风格）的对比：

![修改前 Win11 右键菜单](/source/img/win11setmouce/3win11.png)

![修改后 Win10 右键菜单](/source/img/win11setmouce/4win10.png)

## 如何恢复原状

如果后悔了，想要恢复 Win11 原生的右键菜单，同样打开管理员终端，输入以下命令后重启即可：

```powershell
reg.exe delete "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /va /f
```

## 总结

通过修改注册表项 `{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}`，实际上是禁用了 Win11 右键菜单的折叠功能，将选项全部展开显示。整个过程只需一条命令，不需要安装任何第三方工具，非常简单。

