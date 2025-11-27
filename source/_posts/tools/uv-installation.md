---
title: uv 安装指南 - 极速 Python 包管理工具
date: 2025-11-27 16:45:00
categories:
  - 工具
  - Python
tags:
  - uv
  - Python
  - 包管理
  - 效率工具
---

## uv - 下一代 Python 包管理工具

uv 是由 Astral 开发的新一代 Python 包管理工具，以其极快的速度和简洁的设计理念受到开发者的青睐。本文将介绍如何在不同平台上安装 uv。

### 什么是 uv？

uv 是一个极速的 Python 包管理器，旨在替代传统的 pip、pip-tools 等工具。它提供了：

- ⚡ **极快的速度**：比 pip 快 10-100 倍
- 🔒 **可靠的依赖解析**：智能的依赖冲突解决
- 🎯 **简洁的 API**：易于使用的命令行界面
- 🔄 **完整的工具链**：包含项目管理、工具运行等功能

### Windows 系统安装

#### 独立安装器（推荐）

使用 PowerShell 运行以下命令：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

安装特定版本：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/0.9.13/install.ps1 | iex"
```

💡 **提示**：安装前可以先查看脚本内容：

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | more"
```

#### 使用包管理器

**WinGet**：

```powershell
winget install --id=astral-sh.uv -e
```

**Scoop**：

```powershell
scoop install main/uv
```

### macOS 和 Linux 系统安装

#### 独立安装器（推荐）

使用 `curl` 下载并安装：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

如果系统没有 `curl`，可以使用 `wget`：

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

安装特定版本：

```bash
curl -LsSf https://astral.sh/uv/0.9.13/install.sh | sh
```

💡 **提示**：安装前可以先检查脚本内容：

```bash
curl -LsSf https://astral.sh/uv/install.sh | less
```

#### macOS 包管理器

**Homebrew**：

```bash
brew install uv
```

**MacPorts**：

```bash
sudo port install uv
```

### 使用 PyPI 安装

如果您已经有 Python 环境，可以使用 `pipx` 安装（推荐）：

```bash
pipx install uv
```

或者使用 `pip`：

```bash
pip install uv
```

⚠️ **注意**：uv 为大多数平台提供了预编译的二进制包（wheels）。如果您的平台没有可用的 wheel，uv 将从源码构建，这需要 Rust 工具链。

### 其他安装方式

#### Docker

uv 提供了官方 Docker 镜像：

```bash
docker pull ghcr.io/astral-sh/uv
```

详见[官方 Docker 使用指南](https://docs.astral.sh/uv/guides/integration/docker/)。

#### GitHub Releases

可以直接从 [GitHub Releases](https://github.com/astral-sh/uv/releases) 下载预编译的二进制文件，适用于所有支持的平台。

#### Cargo（从源码构建）

如果您有 Rust 环境，可以使用 Cargo 安装：

```bash
cargo install --locked uv
```

⚠️ **注意**：此方法会从源码编译 uv，需要兼容的 Rust 工具链。

### 升级 uv

如果使用独立安装器安装，可以通过以下命令自动更新：

```bash
uv self update
```

💡 **提示**：更新 uv 时会重新运行安装器，可能会修改 shell 配置文件。如果要禁用此行为，请设置环境变量：

```bash
UV_NO_MODIFY_PATH=1 uv self update
```

如果通过其他方式安装，self-update 功能将被禁用，请使用对应的包管理器升级：

**使用 pip**：
```bash
pip install --upgrade uv
```

**使用 Homebrew**：
```bash
brew upgrade uv
```

**使用 WinGet**：
```powershell
winget upgrade astral-sh.uv
```

### 启用 Shell 自动补全

为了更好的使用体验，建议启用 shell 自动补全功能。

💡 **提示**：运行 `echo $SHELL` 可以查看您当前使用的 shell。

#### 为 uv 启用自动补全

**Bash**：
```bash
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
```

**Zsh**：
```bash
echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc
```

**Fish**：
```bash
echo 'uv generate-shell-completion fish | source' > ~/.config/fish/completions/uv.fish
```

**Elvish**：
```bash
echo 'eval (uv generate-shell-completion elvish | slurp)' >> ~/.elvish/rc.elv
```

**PowerShell**：
```powershell
if (!(Test-Path -Path $PROFILE)) {
  New-Item -ItemType File -Path $PROFILE -Force
}
Add-Content -Path $PROFILE -Value '(& uv generate-shell-completion powershell) | Out-String | Invoke-Expression'
```

#### 为 uvx 启用自动补全

**Bash**：
```bash
echo 'eval "$(uvx --generate-shell-completion bash)"' >> ~/.bashrc
```

**Zsh**：
```bash
echo 'eval "$(uvx --generate-shell-completion zsh)"' >> ~/.zshrc
```

**Fish**：
```bash
echo 'uvx --generate-shell-completion fish | source' > ~/.config/fish/completions/uvx.fish
```

**Elvish**：
```bash
echo 'eval (uvx --generate-shell-completion elvish | slurp)' >> ~/.elvish/rc.elv
```

**PowerShell**：
```powershell
if (!(Test-Path -Path $PROFILE)) {
  New-Item -ItemType File -Path $PROFILE -Force
}
Add-Content -Path $PROFILE -Value '(& uvx --generate-shell-completion powershell) | Out-String | Invoke-Expression'
```

设置完成后，重启终端或重新加载配置文件使其生效。

### 验证安装

安装完成后，运行以下命令验证：

```bash
uv --version
```

### 卸载 uv

如果需要从系统中移除 uv，请按以下步骤操作：

#### 1. 清理存储的数据（可选）

```bash
# 清理缓存
uv cache clean

# 删除 Python 安装目录
rm -r "$(uv python dir)"

# 删除工具目录
rm -r "$(uv tool dir)"
```

💡 **提示**：在删除二进制文件之前，建议先清理 uv 存储的数据。详见[存储参考文档](https://docs.astral.sh/uv/reference/storage/)。

#### 2. 删除可执行文件

**macOS 和 Linux**：
```bash
rm ~/.local/bin/uv ~/.local/bin/uvx
```

**Windows (PowerShell)**：
```powershell
rm $HOME\.local\bin\uv.exe
rm $HOME\.local\bin\uvx.exe
rm $HOME\.local\bin\uvw.exe
```

⚠️ **注意**：0.5.0 之前的版本安装在 `~/.cargo/bin`，如果从旧版本升级，需要手动删除该目录下的二进制文件。

### 下一步

安装完成后，您可以：

1. 创建新的 Python 项目：`uv init my-project`
2. 安装依赖包：`uv add <package-name>`
3. 运行脚本：`uv run python script.py`
4. 管理 Python 版本：`uv python install 3.12`

查看[第一步指南](https://docs.astral.sh/uv/getting-started/first-steps/)或直接跳转到[使用指南](https://docs.astral.sh/uv/guides/)开始使用 uv。

### 参考资源

- [官方安装文档](https://docs.astral.sh/uv/getting-started/installation/)
- [GitHub 仓库](https://github.com/astral-sh/uv)
- [官方指南](https://docs.astral.sh/uv/guides/)

使用 uv 可以大幅提升 Python 开发效率，告别漫长的依赖安装等待时间，享受更流畅的开发体验！

