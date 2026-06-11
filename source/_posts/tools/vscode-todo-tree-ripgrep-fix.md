---
title: VS Code Todo Tree 插件无法运行（ripgrep 未找到）的修复方法
date: 2026-05-27 16:30:00
description: - 按下 `Ctrl+Shift+P` 搜不到 `Todo Tree: Refresh` 命令
keywords: VS, Code, Todo, Tree, 插件无法运行, ripgrep
categories:
  - 工具
tags:
  - VS Code
  - Todo Tree
  - ripgrep
  - 效率工具
---

在 VS Code 新版本中使用 Todo Tree 插件时，可能会遇到 `command 'todo-tree.refresh' not found` 的错误，即便 Todo Tree 已经安装且显示为"已启用"状态。本文记录排查过程和解决方案。

## 问题现象

- 按下 `Ctrl+Shift+P` 搜不到 `Todo Tree: Refresh` 命令
- 左侧活动栏不显示 Todo Tree 图标
- 手动在命令面板执行 `todo-tree.refresh` 提示 `command 'todo-tree.refresh' not found`

## 根本原因

Todo Tree 依赖 [ripgrep](https://github.com/BurntSushi/ripgrep)（`rg`）来做文件搜索，但插件有时候无法从系统 `$PATH` 中定位到 ripgrep 可执行文件，导致插件初始化失败，所有命令都不可用。

这个问题比较隐蔽，因为 VS Code 不会弹出任何错误提示——插件只是静默失败。

## 排查方法

先把插件**禁用 → 重新加载窗口 → 启用**，让插件重新初始化，这时候打开 VS Code 的开发者工具（`Ctrl+Shift+I` 或 `Help → Toggle Developer Tools`），在 Console 面板中就能看到真正的错误日志，其中会明确指出 `rg` 查找失败。

## 解决方案

在 VS Code 设置中显式指定 ripgrep 的绝对路径，绕过 `$PATH` 查找：

### 1. 找到 ripgrep 的绝对路径

```bash
which rg
# 输出示例: /usr/bin/rg
```

Windows 用户可以在 Git Bash 或 WSL 中运行，或者直接在文件资源管理器中找到 `rg.exe` 的路径。

### 2. 在 VS Code 配置中添加路径

打开 `settings.json`（`Ctrl+Shift+P` → `Preferences: Open User Settings (JSON)`），添加：

```json
"todo-tree.ripgrep.ripgrep": "/usr/bin/rg"
```

Windows 示例（注意双反斜杠转义）：

```json
"todo-tree.ripgrep.ripgrep": "C:\\Program Files\\ripgrep\\rg.exe"
```

### 3. 重新加载插件

配置生效后，再次**禁用 → 重新加载窗口 → 启用** Todo Tree，此时插件应该能正常找到 ripgrep 并完成初始化。

## 自定义标签配置

Todo Tree 默认只高亮 `TODO`、`FIXME` 等几个标签，可以根据需要添加自定义标签。以下是我常用的配置：

```json
"todo-tree.general.tags": [
    "BUG",
    "HACK",
    "FIXME",
    "TODO",
    "XXX",
    "[x]",
    "TODO-z",
    "BUG-z",
    "NOTE-z"
]
```

这样代码中所有带这些标记的注释都会被 Todo Tree 统一管理，点击即可跳转。

配置后的效果：
- `TODO-z`、`BUG-z`、`NOTE-z` 带 `-z` 后缀是我个人的标记习惯，方便与团队通用的 `TODO` / `BUG` 区分
- `[x]` 用于标记已完成待清理的临时代码
- `XXX` 用于标记需要紧急关注的问题

## 延伸：ripgrep 全局配置

如果你使用 Linux/WSL，还可以给 ripgrep 配一个全局配置文件 `~/.ripgreprc`，让命令行搜索体验更好：

```
--smart-case
--max-columns=200
--max-columns-preview
--colors=match:fg:yellow
--colors=match:style:bold
--colors=line:fg:blue
--colors=path:fg:green
```

## 总结

这个问题本质上不是 Todo Tree 本身的 bug，而是 VS Code 扩展的运行时环境和交互式 shell 的 `$PATH` 可能存在差异。**直接写绝对路径是最稳妥的解决方式**，`which rg` 一步就能拿到路径，配置一条 JSON 即可永久修复。
