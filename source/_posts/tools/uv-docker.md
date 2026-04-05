---
title: 使用 uv 优化 Docker 镜像构建
date: 2026-02-01 15:00:00
categories: 工具
tags: [Python, uv, Docker]
---

## 前言

在 Python 项目中，使用 uv 作为包管理工具可以显著提升依赖安装速度。本文介绍如何用 uv 优化 Docker 镜像构建，实现更好的缓存命中和更小的镜像体积。

## 核心思路

uv 的设计目标之一就是**快**，这体现在 Docker 构建场景中就是：
1. **更小的基础镜像** - 不需要预装 pip、venv 等
2. **更好的缓存命中** - 分离依赖安装和代码拷贝
3. **更快的安装速度** - uv 安装依赖比 pip 快 10-100 倍

## 完整 Dockerfile 示例

```dockerfile
# 第一阶段：构建阶段
FROM registry.safone.ltd:1443/cqsafone/python:3.13-slim

# 1️⃣ 基础系统依赖（极少）
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2️⃣ 安装 uv（官方推荐方式）
RUN pip install --no-cache-dir uv

WORKDIR /app

# 3️⃣ 先拷贝依赖文件，最大化缓存命中
COPY pyproject.toml uv.lock ./

# 4️⃣ 安装依赖（不装项目本身）
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 5️⃣ 再拷贝代码
COPY . .

# 暴露 FastAPI 默认端口
EXPOSE 8000

ENV PATH="/app/.venv/bin:$PATH"

# 启动命令：直接调用 uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 关键步骤解析

### 1. 安装 uv

```dockerfile
RUN pip install --no-cache-dir uv
```

直接用 pip 安装 uv，这是官方推荐的方式。安装后立即拥有极速的包管理能力。

### 2. 分离依赖和代码

```dockerfile
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
```

**关键点**：
- 先只拷贝依赖文件，不拷贝代码
- 这样即使代码变了，只要 `pyproject.toml` 和 `uv.lock` 没变，Docker 就能命中缓存
- `--frozen` 确保使用锁文件版本，不会有意外更新
- `--no-dev` 不安装开发依赖，减小镜像体积

### 3. 使用 BuildKit 缓存

```dockerfile
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
```

`--mount=type=cache` 是 Docker BuildKit 的特性，它会在多次构建之间保留 `uv` 的缓存目录，即使这一层重新构建，缓存依然可用。

### 4. 添加 venv 到 PATH

```dockerfile
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

把 `.venv/bin` 加入 PATH 后，启动命令可以直接写 `uvicorn` 而不需要写完整路径。

## 构建命令

确保开启了 BuildKit：

```bash
# 方式一：环境变量
DOCKER_BUILDKIT=1 docker build -t myapp .

# 方式二：Docker Buildx
docker buildx build -t myapp .
```

## 注意事项

1. **uv.lock 必须提交到仓库** - 使用 `--frozen` 依赖锁文件
2. **BuildKit 必须开启** - `--mount=type=cache` 需要 BuildKit 支持
3. **不要在镜像中开发** - 所有依赖都是锁定版本，适合生产部署
4. **基础镜像选择** - 可以用官方 `python:3.13-slim`，也可以用公司内部定制镜像

## 对比传统 pip 方式

| 特性 | pip | uv |
|------|-----|-----|
| 安装速度 | 慢 | 极快（10-100x） |
| 缓存复用 | 差 | 好（BuildKit cache） |
| 锁文件 | 需手动维护 | 自动生成 |
| 镜像体积 | 较大 | 较小 |

## 总结

使用 uv 优化 Docker 构建的核心在于：
1. 分离依赖安装和代码拷贝，最大化缓存命中
2. 利用 BuildKit 的 cache mount 保留下载缓存
3. 精简依赖，只安装生产环境所需的包

这样构建出来的 Docker 镜像既小又快，是现代化 Python 项目部署的最佳实践。
