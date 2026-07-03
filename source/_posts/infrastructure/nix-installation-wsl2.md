---
title: Nix 在 WSL2 中的安装
date: 2026-04-10 10:00:00
description: 在 WSL2 环境下安装和配置 Nix 包管理器：系统初始化、flakes 配置、常见问题解决。
keywords: Nix, WSL2, 包管理, Flakes, NixOS, Linux
categories: 基础设施
tags:
  - Nix
  - WSL2
---

## Nix 在 WSL2 中的安装

之前在 WSL2 中安装 Nix 需要打补丁、处理各种兼容性问题，社区也长期讨论 WSL2 支持。现在好消息来了：**新版本的 Nix 安装脚本在 WSL2 上和 Linux 完全一致，无需额外处理**。

### 安装 direnv

direnv 是 Nix 的好搭档，可以根据目录自动切换环境。

```bash
# 安装 direnv
sudo apt update && sudo apt install direnv -y

# 挂载到 Zsh（其他 shell 替换 zsh 即可）
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc

# 挂载到 Bash
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc

# 使配置生效
source ~/.zshrc
source ~/.bashrc
```

### 安装 Nix

```bash
sh <(curl --proto '=https' --tlsv1.2 -L https://nixos.org/nix/install) --daemon
```

这条命令会自动检测系统环境，WSL2 会被识别为 Linux，直接走标准安装流程。`--daemon` 参数会使用 systemd 风格的 daemon 方式运行 Nix，这是目前推荐的安装方式。

### 安装过程

1. 脚本会提示确认安装，按回车继续或 `Ctrl+C` 取消
2. 自动创建 nixbld 用户组和用户
3. 配置 systemd 服务（或 equivalent）
4. 完成后提示重新加载 shell 或重启终端

### 验证安装

```bash
# 检查 Nix 版本
nix --version

# 测试安装包
nix-env --version

# 安装一个简单的包测试
nix-env -iA nixpkgs.hello
hello
```

### 常见问题

**Q: 安装脚本没反应？**
检查网络连接，确保能访问 `nixos.org`。也可以加 `-v` 参数查看详细日志。

**Q: 提示权限错误？**
确保以普通用户运行，脚本会自动处理 sudo 提权，不需要手动 `sudo`。

**Q: 提示 experimental-features 需要手动开启？**
服务器上新装 Nix 后默认不开启 flakes，需要手动配置：

```bash
mkdir -p ~/.config/nix
echo 'experimental-features = flakes nix-command' >> ~/.config/nix/nix.conf
```

重启 shell 后即可正常使用 `nix` 命令和 flakes 相关功能。

**Q: 卸载重装？**
参考官方文档清理残留文件后重新运行安装命令即可。

### 写在最后

Nix 是一个声明式、可复现的包管理器，支持多版本共存，非常适合开发环境管理。WSL2 支持的完善让在 Windows 上使用 Nix 变得更加简单，感兴趣的可以试试。
