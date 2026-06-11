---
title: GPUStack 使用 Docker Compose 自定义 vLLM 镜像升级 Transformers
date: 2026-04-17 15:00:00
description: 在实际生产环境中，GPUStack 内置的 vLLM 版本可能无法及时适配最新的模型。例如某些新模型需要 `transformers 5.5.0` 以上版本以及 `vllm[audio]` 依赖，而官方镜像尚未包含这些依赖。
keywords: GPUStack, GPU管理, AI推理, vLLM, Transformers
categories:
  - 工具
  - Docker
tags:
  - GPUStack
  - vLLM
  - Docker Compose
  - 模型部署
  - LLM推理
---

## 概述

在实际生产环境中，GPUStack 内置的 vLLM 版本可能无法及时适配最新的模型。例如某些新模型需要 `transformers 5.5.0` 以上版本以及 `vllm[audio]` 依赖，而官方镜像尚未包含这些依赖。

本文介绍如何通过 Docker Compose + 自定义 Dockerfile 的方式，快速构建适配 `vllm/vllm-openai:v0.19.0` 的推理镜像并部署。

## 构建自定义镜像

### Dockerfile

使用国内镜像源加速拉取 vLLM 官方镜像：

```dockerfile
FROM docker.1ms.run/vllm/vllm-openai:v0.19.0

RUN uv pip install --system vllm[audio] \
  && uv pip install --system transformers==5.5.0
```

> 这里使用 `docker.1ms.run` 作为 Docker Hub 的国内镜像代理，解决网络访问问题。如果你可以直接访问 Docker Hub，将 `FROM` 改为 `vllm/vllm-openai:v0.19.0` 即可。

### 构建命令

```bash
docker build -t vllm/vllm-openai:v0.19.0-custom .
```

构建完成后，本地会生成一个包含 `vllm[audio]` 和 `transformers==5.5.0` 的推理引擎镜像。

## Docker Compose 部署

### docker-compose.yml

```yaml
services:
  vllm:
    image: vllm/vllm-openai:v0.19.0-custom
    container_name: vllm-server
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./models:/models
    environment:
      - HF_HOME=/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    command: >-
      vllm serve /models/your-model-name
      --host 0.0.0.0
      --port 8000
      --served-model-name your-model-name
```

### 启动服务

```bash
docker compose up -d
```

### 验证服务

```bash
# 检查容器状态
docker compose ps

# 查看日志
docker compose logs -f vllm

# 测试 API
curl http://localhost:8000/v1/models
```

## 对接 GPUStack

如果要将这个自定义镜像用于 GPUStack，需要在 GPUStack 的推理后端中添加自定义版本：

### 方式一：UI 界面配置

在推理后端菜单中，编辑 vLLM，添加新版本：

| 配置项 | 值 |
|--------|----|
| 版本 | 0.19.0-custom |
| 镜像名称 | vllm/vllm-openai:v0.19.0-custom |
| 框架 | CUDA |
| 覆盖镜像入口命令（ENTRYPOINT） | `vllm serve` |
| 执行命令 | `{{model_path}} --host {{worker_ip}} --port {{port}} --served-model-name {{model_name}}` |

### 方式二：YAML 模式导入

如果需要同时保留其他自定义版本，可以在 YAML 模式下统一导入：

```yaml
backend_name: vLLM
version_configs:
  0.19.0-custom:
    image_name: vllm/vllm-openai:v0.19.0-custom
    entrypoint: vllm serve
    run_command: >-
      {{model_path}} --host {{worker_ip}} --port {{port}} --served-model-name
      {{model_name}}
    env: {}
    custom_framework: cuda
```

> **注意**：如果已有其他自定义版本，需要将所有版本一并写入 `version_configs`，否则导入后会覆盖旧版本配置。

## 国内镜像源说明

构建过程中使用的 `docker.1ms.run` 是一个 Docker Hub 镜像代理服务，适用于国内网络环境。常见的 Docker Hub 国内镜像源包括：

| 镜像源 | 格式示例 |
|--------|----------|
| docker.1ms.run | `docker.1ms.run/vllm/vllm-openai:v0.19.0` |
| 阿里云（需配置） | `registry.cn-hangzhou.aliyuncs.com/...` |
| 直接拉取（需科学上网） | `vllm/vllm-openai:v0.19.0` |

如果 Worker 节点无法直接访问 Docker Hub，可以提前拉取镜像并重新 tag：

```bash
docker pull docker.1ms.run/vllm/vllm-openai:v0.19.0
docker tag docker.1ms.run/vllm/vllm-openai:v0.19.0 vllm/vllm-openai:v0.19.0
```

## 注意事项

1. **依赖兼容性**：`transformers==5.5.0` 与 `vllm[audio]` 需要匹配 vLLM 的对应版本，升级前建议查阅 vLLM 的 release notes 确认兼容性。
2. **GPU 驱动**：确保 Worker 节点已正确安装 NVIDIA 驱动和 Container Toolkit。
3. **镜像推送**：如果是多节点部署，需要将构建好的镜像推送到 Worker 节点可访问的私有仓库。
4. **模板变量**：GPUStack 配置中的 `{{}}` 模板变量保持不变，运行时会自动替换为实际值。

## 总结

通过 Dockerfile 自定义构建 + Docker Compose 部署的组合，可以快速适配 vLLM 新版本所需的依赖，解决官方镜像尚未更新时的兼容性问题。核心步骤就是三步：

1. 编写 Dockerfile，在官方镜像基础上安装额外依赖
2. 构建自定义镜像
3. 在 GPUStack 中添加自定义推理后端版本
