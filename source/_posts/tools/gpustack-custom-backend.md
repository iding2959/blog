---
title: GPUStack 添加自定义 vLLM / SGLang 版本教程
date: 2026-04-07 15:30:00
description: GPUStack 自定义推理后端教程：添加 vLLM、SGLang 自定义版本，构建支持 Gemma 4 的专用镜像，实现多版本推理引擎共存。
keywords: GPUStack, vLLM, SGLang, 推理引擎, 模型部署, LLM
categories:
  - 工具
  - AI
tags:
  - GPUStack
  - vLLM
  - SGLang
  - 模型部署
  - LLM推理
---

## 概述

GPUStack 支持可插拔的推理引擎架构，允许自定义推理后端及其版本，用于引入 GPUStack 未内置的 vLLM / SGLang / MindIE 版本，或接入其他自定义推理引擎镜像。

本文以 vLLM v0.19.0 和 SGLang v0.5.10 为例，演示如何在 GPUStack 中添加自定义推理后端版本。

## 添加 vLLM 自定义版本

在推理后端菜单中，编辑 vLLM，在版本配置中选择添加版本，配置如下：

| 配置项 | 值 |
|--------|----|
| 版本 | 0.19.0 |
| 镜像名称 | vllm/vllm-openai:v0.19.0 |
| 框架 | CUDA |
| 覆盖镜像入口命令（ENTRYPOINT） | `vllm serve` |
| 执行命令 | `{{model_path}} --host {{worker_ip}} --port {{port}} --served-model-name {{model_name}}` |

## 添加 SGLang 自定义版本

同样地，在推理后端菜单中，编辑 SGLang，添加新版本：

| 配置项 | 值 |
|--------|----|
| 版本 | 0.5.10 |
| 镜像名称 | lmsysorg/sglang:v0.5.10 |
| 框架 | CUDA |
| 覆盖镜像入口命令（ENTRYPOINT） | `sglang serve` |
| 执行命令 | `--model-path {{model_path}} --host {{worker_ip}} --port {{port}}` |

## 使用 YAML 模式导入

如果需要批量配置或导入，也可以切换到 YAML 模式直接导入配置。

### vLLM YAML 配置

```yaml
backend_name: vLLM
version_configs:
  0.19.0-custom:
    image_name: vllm/vllm-openai:v0.19.0
    entrypoint: vllm serve
    run_command: >-
      {{model_path}} --host {{worker_ip}} --port {{port}} --served-model-name
      {{model_name}}
    env: {}
    custom_framework: cuda
```

### SGLang YAML 配置

```yaml
backend_name: SGLang
version_configs:
  0.5.10-custom:
    image_name: lmsysorg/sglang:v0.5.10
    entrypoint: sglang serve
    run_command: '--model-path {{model_path}} --host {{worker_ip}} --port {{port}}'
    env: {}
    custom_framework: cuda
```

> **注意**：如果当前已有其他自定义版本，需要将其他自定义版本一同添加在 `version_configs` 中一起导入，避免配置覆盖。

## 构建支持 Gemma 4 的 vLLM 镜像

截止 2026.2.9，SGLang 对 Gemma 4 的支持代码还未合并，建议使用 vLLM 来运行 Gemma 4。

由于运行 Gemma 4 需要 `transformers 5.5.0` 以及 `vllm[audio]` 依赖，建议自行构建支持 Gemma 4 的镜像。参考 Dockerfile 如下：

```dockerfile
FROM vllm/vllm-openai:v0.19.0

RUN uv pip install --system vllm[audio] \
  && uv pip install --system transformers==5.5.0
```

构建镜像：

```bash
docker build -t vllm/vllm-openai:v0.19.0-gemma4 .
```

然后在推理后端菜单中编辑 vLLM，切换到 YAML 模式导入以下配置（声明了两个版本：官方的 0.19.0 和自定义的 0.19.0-gemma4）：

```yaml
backend_name: vLLM
version_configs:
  0.19.0-custom:
    image_name: vllm/vllm-openai:v0.19.0
    entrypoint: vllm serve
    run_command: >-
      {{model_path}} --host {{worker_ip}} --port {{port}} --served-model-name
      {{model_name}}
    env: {}
    custom_framework: cuda
  0.19.0-gemma4-custom:
    image_name: vllm/vllm-openai:v0.19.0-gemma4
    entrypoint: vllm serve
    run_command: >-
      {{model_path}} --host {{worker_ip}} --port {{port}} --served-model-name
      {{model_name}}
    env: {}
    custom_framework: cuda
```

成功导入后，可在 vLLM 卡片中查看两个自定义版本配置。

## 多版本共存 YAML 示例

如果需要在同一个后端中配置多个自定义版本（例如同时支持 Qwen3.5 和 Gemma 4），可以统一在 `version_configs` 中声明所有版本：

```yaml
backend_name: vLLM
version_configs:
  qwen3-5-custom:
    image_name: quay.io/gpustack/runner:cuda12.9-vllm0.17.1
    run_command: ''
    entrypoint: ''
    custom_framework: cuda
    env:
      LD_LIBRARY_PATH: /usr/local/nvidia/lib64:/usr/local/nvidia/lib:/usr/lib/x86_64-linux-gnu
  0.19.0-gemma-custom:
    image_name: vllm/vllm-openai:v0.19.0
    run_command: >-
      {{model_path}} --host {{worker_ip}} --port {{port}} --served-model-name
      {{model_name}}
    entrypoint: vllm serve
    custom_framework: cuda
    env: {}
default_backend_param: []
default_env: {}
```

上述配置声明了两个自定义版本：
- **qwen3-5-custom**：使用 GPUStack 官方 runner 镜像，兼容 Qwen3.5 系列模型
- **0.19.0-gemma-custom**：使用官方 vLLM 镜像，支持 Gemma 4 等最新模型

> **提示**：在 GPUStack UI 中切换到 YAML 模式导入时，只需将所有需要保留的版本一并写入 `version_configs` 即可，旧版本不会被自动覆盖。

## 注意事项

1. **镜像拉取**：GPUStack 会自动调用主机容器运行时拉取容器镜像，需要确保 Worker 节点可访问 Docker Hub，或者提前拉取好并重新 tag，按需修改 UI 配置中的镜像地址；
2. **模板变量**：保持执行命令中的 `{{}}` 不变，此为 GPUStack 的模板化配置，会在运行时自动替换为实际值。