---
title: PyTorch 三件套版本对应关系与安装指南
date: 2025-11-17 18:00:00
categories:
  - 深度学习
  - Python
tags:
  - PyTorch
  - 深度学习
  - 机器学习
  - 环境配置
---

## PyTorch 三件套 - torch、torchvision、torchaudio

PyTorch 生态系统主要由三个核心库组成：`torch`（核心库）、`torchvision`（计算机视觉）和 `torchaudio`（音频处理）。正确安装匹配的版本对于项目的稳定运行至关重要。

### 什么是 PyTorch 三件套？

- **torch**：PyTorch 核心库，提供张量计算、自动微分、神经网络等基础功能
- **torchvision**：计算机视觉工具包，包含常用的数据集、模型架构和图像变换
- **torchaudio**：音频处理工具包，提供音频 I/O、变换和常用数据集

⚠️ **重要提示**：三个库的版本必须互相兼容，否则可能导致运行时错误！

## 版本对应关系表

### 主要版本对应关系

| torch 版本 | torchvision 版本 | torchaudio 版本 | Python 版本       |
|-----------|-----------------|----------------|------------------|
| 2.9       | 0.24.*          | 2.9.*          | >=3.10, <=3.14   |
| 2.8       | 0.23.*          | 2.8.*          | >=3.9, <=3.13    |
| 2.7       | 0.22.*          | 2.7.*          | >=3.9, <=3.13    |
| 2.6       | 0.21.*          | 2.6.*          | >=3.9, <=3.12    |
| 2.5       | 0.20.*          | 2.5.*          | >=3.9, <=3.12    |
| 2.4       | 0.19.*          | 2.4.*          | >=3.8, <=3.12    |
| 2.3       | 0.18.*          | 2.3.*          | >=3.8, <=3.12    |
| 2.2       | 0.17.*          | 2.2.*          | >=3.8, <=3.11    |
| 2.1       | 0.16.*          | 2.1.*          | >=3.8, <=3.11    |
| 2.0       | 0.15.*          | 2.0.*          | >=3.8, <=3.11    |

<details>
<summary>📋 查看更多旧版本对应关系</summary>

| torch 版本 | torchvision 版本 | torchaudio 版本 | Python 版本         |
|-----------|-----------------|----------------|---------------------|
| 1.13      | 0.14.*          | 0.13.*         | >=3.7.2, <=3.10     |
| 1.12      | 0.13.*          | 0.12.*         | >=3.7, <=3.10       |
| 1.11      | 0.12.*          | 0.11.*         | >=3.7, <=3.10       |
| 1.10      | 0.11.*          | 0.10.*         | >=3.6, <=3.9        |
| 1.9       | 0.10.*          | 0.9.*          | >=3.6, <=3.9        |
| 1.8       | 0.9.*           | 0.8.*          | >=3.6, <=3.9        |

</details>

💡 **版本说明**：
- `*` 表示该位置的版本号可以是任意数字
- 例如：`0.23.*` 可以是 `0.23.0`、`0.23.1`、`0.23.2` 等

## 安装方法

### 使用 uv 安装（推荐 ⭐）

uv 是新一代的 Python 包管理工具，速度更快，依赖解析更智能。

#### 安装最新稳定版本

```bash
# 自动匹配 torchvision 版本
uv add torch torchvision torchaudio
```

#### 安装指定版本（推荐方式）

```bash
# 安装 PyTorch 2.8 系列
uv add "torch==2.8.*" torchvision "torchaudio==2.8.*"

# 安装 PyTorch 2.7 系列
uv add "torch==2.7.*" torchvision "torchaudio==2.7.*"

# 安装 PyTorch 2.6 系列
uv add "torch==2.6.*" torchvision "torchaudio==2.6.*"
```

💡 **为什么 torchvision 不指定版本**？
- 只指定 torch 版本，torchvision 会自动匹配对应的版本
- 这是因为 torchvision 的版本号与 torch 不一致（例如 torch 2.8 对应 torchvision 0.23）
- uv 的智能依赖解析会自动选择正确的版本

#### 安装特定精确版本

```bash
# 安装特定的精确版本
uv add torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0
```

#### 使用 CPU 版本

```bash
# CPU 版本（体积更小）
uv add "torch==2.8.*" torchvision "torchaudio==2.8.*" --index-url https://download.pytorch.org/whl/cpu
```

#### 使用 CUDA 版本

```bash
# CUDA 11.8 版本
uv add "torch==2.8.*" torchvision "torchaudio==2.8.*" --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1 版本
uv add "torch==2.8.*" torchvision "torchaudio==2.8.*" --index-url https://download.pytorch.org/whl/cu121

# CUDA 12.4 版本
uv add "torch==2.8.*" torchvision "torchaudio==2.8.*" --index-url https://download.pytorch.org/whl/cu124
```

### 使用 pip 安装

如果你使用传统的 pip 工具，可以使用以下命令：

#### 安装最新稳定版本

```bash
# 自动匹配版本
pip install torch torchvision torchaudio
```

#### 安装指定版本

```bash
# 安装 PyTorch 2.8 系列
pip install torch==2.8.* torchvision torchaudio==2.8.*

# 安装 PyTorch 2.7 系列
pip install torch==2.7.* torchvision torchaudio==2.7.*

# 或者指定精确版本
pip install torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0
```

#### 使用 CPU 版本

```bash
# CPU 版本
pip install torch==2.8.* torchvision torchaudio==2.8.* --index-url https://download.pytorch.org/whl/cpu
```

#### 使用 CUDA 版本

```bash
# CUDA 11.8 版本
pip install torch==2.8.* torchvision torchaudio==2.8.* --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1 版本
pip install torch==2.8.* torchvision torchaudio==2.8.* --index-url https://download.pytorch.org/whl/cu121

# CUDA 12.4 版本
pip install torch==2.8.* torchvision torchaudio==2.8.* --index-url https://download.pytorch.org/whl/cu124
```

### 国内镜像加速

对于国内用户，可以使用镜像源加速下载：

#### 使用 uv（清华镜像）

```bash
# 使用清华镜像
uv add "torch==2.8.*" torchvision "torchaudio==2.8.*" \
  --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 使用 pip（清华镜像）

```bash
# 使用清华镜像
pip install torch==2.8.* torchvision torchaudio==2.8.* \
  -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 其他国内镜像源

```bash
# 阿里云镜像
-i https://mirrors.aliyun.com/pypi/simple/

# 中科大镜像
-i https://pypi.mirrors.ustc.edu.cn/simple/

# 豆瓣镜像
-i https://pypi.douban.com/simple/
```

⚠️ **注意**：官方 PyTorch 镜像（download.pytorch.org）可能不在国内镜像源中，CUDA 版本建议直接使用官方源。

## 如何选择合适的版本？

### 1. 确定 Python 版本

首先检查你的 Python 版本：

```bash
python --version
```

根据上面的版本对应表，选择支持你 Python 版本的 PyTorch 版本。

### 2. 确定 CUDA 版本（GPU 用户）

如果你要使用 GPU，需要检查 CUDA 版本：

```bash
# Linux/macOS
nvidia-smi

# Windows (PowerShell)
nvidia-smi
```

常见 CUDA 版本对应关系：
- **CUDA 11.8**：兼容性好，适合大多数场景
- **CUDA 12.1**：较新版本，性能更好
- **CUDA 12.4**：最新版本，支持最新特性

### 3. 选择 PyTorch 版本

一般建议：
- 🔹 **新项目**：使用最新稳定版（当前 2.8 或 2.9）
- 🔹 **生产环境**：使用 LTS 版本（2.4+ 较稳定）
- 🔹 **旧项目**：保持与项目要求一致的版本

### 4. CPU vs GPU

- **CPU 版本**：适合学习、轻量级任务、没有 GPU 的机器
- **GPU 版本**：适合训练深度学习模型、大规模计算

💡 **提示**：CPU 版本的安装包更小，下载更快。

## 验证安装

安装完成后，可以运行以下 Python 代码验证：

```python
import torch
import torchvision
import torchaudio

# 查看版本
print(f"PyTorch 版本: {torch.__version__}")
print(f"TorchVision 版本: {torchvision.__version__}")
print(f"TorchAudio 版本: {torchaudio.__version__}")

# 检查 CUDA 是否可用
print(f"CUDA 是否可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA 版本: {torch.version.cuda}")
    print(f"GPU 设备数量: {torch.cuda.device_count()}")
    print(f"当前 GPU: {torch.cuda.get_device_name(0)}")
```

预期输出示例：

```
PyTorch 版本: 2.8.0
TorchVision 版本: 0.23.0
TorchAudio 版本: 2.8.0
CUDA 是否可用: True
CUDA 版本: 12.1
GPU 设备数量: 1
当前 GPU: NVIDIA GeForce RTX 4090
```

## 常见问题

### 版本冲突怎么办？

如果遇到版本冲突，可以使用以下方法：

**使用 uv（推荐）**：
```bash
# uv 会自动解决依赖冲突
uv sync
```

**使用 pip**：
```bash
# 先卸载再重新安装
pip uninstall torch torchvision torchaudio
pip install torch==2.8.* torchvision torchaudio==2.8.*
```

### 如何升级到新版本？

**使用 uv**：
```bash
# 升级到最新版本
uv add --upgrade torch torchvision torchaudio

# 升级到指定版本
uv add --upgrade "torch==2.9.*" torchvision "torchaudio==2.9.*"
```

**使用 pip**：
```bash
# 升级到最新版本
pip install --upgrade torch torchvision torchaudio

# 升级到指定版本
pip install --upgrade torch==2.9.* torchvision torchaudio==2.9.*
```

### 安装太慢怎么办？

1. **使用国内镜像源**（见上文）
2. **使用 uv 替代 pip**（速度快 10-100 倍）
3. **使用 CPU 版本**（安装包更小）
4. **检查网络连接**

### CUDA 版本不匹配怎么办？

如果安装的 PyTorch CUDA 版本与系统 CUDA 版本不匹配：

1. PyTorch 自带 CUDA 运行时，不需要系统安装 CUDA
2. 只需要安装 NVIDIA 驱动即可
3. 选择与显卡驱动兼容的 CUDA 版本

驱动版本要求：
- **CUDA 11.8**：需要驱动 >= 450.80.02 (Linux) 或 >= 452.39 (Windows)
- **CUDA 12.1**：需要驱动 >= 525.60.13 (Linux) 或 >= 528.33 (Windows)

## 完整示例

### 场景 1：新建深度学习项目（使用 uv）

```bash
# 创建项目
uv init my-dl-project
cd my-dl-project

# 安装 PyTorch 2.8（CUDA 12.1）
uv add "torch==2.8.*" torchvision "torchaudio==2.8.*" \
  --index-url https://download.pytorch.org/whl/cu121

# 验证安装
uv run python -c "import torch; print(torch.cuda.is_available())"
```

### 场景 2：在现有项目中安装（使用 pip）

```bash
# 进入项目目录
cd existing-project

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate
# 或者（Linux/macOS）
source venv/bin/activate

# 安装 PyTorch
pip install torch==2.8.* torchvision torchaudio==2.8.*

# 验证安装
python -c "import torch; print(torch.__version__)"
```

### 场景 3：CPU 版本用于学习

```bash
# 使用 uv（推荐）
uv add "torch==2.8.*" torchvision "torchaudio==2.8.*" \
  --index-url https://download.pytorch.org/whl/cpu

# 或使用 pip
pip install torch==2.8.* torchvision torchaudio==2.8.* \
  --index-url https://download.pytorch.org/whl/cpu
```

## 参考资源

- [PyTorch 官方网站](https://pytorch.org/)
- [PyTorch GitHub - vision](https://github.com/pytorch/vision)
- [PyTorch GitHub - audio](https://github.com/pytorch/audio)
- [PyTorch 官方安装指南](https://pytorch.org/get-started/locally/)
- [TorchVision 文档](https://pytorch.org/vision/stable/index.html)
- [TorchAudio 文档](https://pytorch.org/audio/stable/index.html)

---

💡 **小贴士**：建议使用 uv 管理 Python 项目依赖，它不仅安装速度快，而且能够智能解决版本冲突问题。配合本文的版本对应表，可以快速搭建稳定的 PyTorch 开发环境！


