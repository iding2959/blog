# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## 项目概述

基于 **Hexo 7.3.0** + **Fluid 1.9.8** 主题的个人技术博客，部署至 `blog.952405.xyz`。

## 常用命令

```bash
npm run server   # 本地预览 http://localhost:4000
npm run build    # 生成静态文件到 public/
npm run clean    # 清除缓存和已生成文件（含数据库，改了脚本/hook 后需先 clean 再 build）
```

## 文章管理

- 文章存放：`source/_posts/` 下按子目录分类（ai-apps/infrastructure/network-proxy/dev-practice/tools-efficiency/misc）
- 永久链接格式：`:year/:month/:title/`（由 `scripts/subdirectory_posts.js` 自动移除子目录）
- 新建文章：`hexo new [layout] <title>` 或在子目录下新建 `hexo new <subdir/title>`
- 文章模板：`scaffolds/post.md`（包含 SEO 字段）

## 配置文件

- `_config.yml`：Hexo 核心配置（站点信息、永久链接、sitemap 等）
- `_config.fluid.yml`：Fluid 主题配置（导航菜单、暗色模式、代码高亮等）
- `source/css/custom.css`：自定义样式

## 图片路径规范

- 图片统一放在 `source/img/` 目录
- Markdown 中使用相对路径：`../../../img/xxx.png`（三层 `../` 回到 `source/` 根目录）
- ❌ 禁止使用 `/img/...` 或 `/source/img/...`

## 分类规范

- 使用 front-matter 的 `categories` 字段，而非文件路径
- 六大一级分类：**AI 应用、基础设施、网络与代理、开发实践、工具与效率、杂谈**
- 分类采用单行格式（不再使用嵌套）：
  ```yaml
  categories: AI 应用
  ```
- 子目录使用英文命名对应：

| 子目录              | 分类       | 包含内容                                                   |
| ------------------- | ---------- | ---------------------------------------------------------- |
| `ai-apps/`          | AI 应用    | GPUStack、vLLM、SGLang、RAG、模型部署、LLM 推理              |
| `infrastructure/`   | 基础设施   | PVE、Linux、Docker、Kubernetes、存储、虚拟化                  |
| `network-proxy/`    | 网络与代理 | OpenClash、Cloudflare、Cloudflare Tunnel、OpenWrt、HTTPS、QUIC |
| `dev-practice/`     | 开发实践   | Python、Git、FastAPI、数据库、前后端开发                       |
| `tools-efficiency/` | 工具与效率 | VS Code、Typora、Todo Tree、NVM、uv 等工具                     |
| `misc/`             | 杂谈       | 职业规划、学习记录、生活、经验分享等                            |

## SEO 规范

文章 front-matter 必须包含：

```yaml
---
title: 文章标题
date: 2026-06-11 10:00:00
description: 1-2句话概括文章核心内容，50-150字
keywords: 关键词1, 关键词2, 关键词3, 关键词4
categories: 分类
tags:
  - 标签1
---
```

- **description**：用于搜索结果摘要和 meta 标签
- **keywords**：4-6个关键词，逗号分隔

## 标签规范

- **强制使用英文标签**，❌ 禁止中文标签
- 只能从以下标签池中选择，不允许随意新建：

### 可用标签

| 标签 | 使用场景 |
|------|---------|
| `AI` | AI 相关综合 |
| `Algorithm` | 数据结构与算法 |
| `API` | API 设计与开发 |
| `Anaconda` | Anaconda 发行版 |
| `Career` | 职业规划相关 |
| `Cloudflare` | Cloudflare 平台相关 |
| `Cloudflare Tunnel` | Cloudflare Tunnel 内网穿透 |
| `Clash` | Clash 代理客户端 |
| `Conda` | Conda 包/环境管理 |
| `CSS` | CSS 样式 |
| `CUDA` | NVIDIA CUDA 工具包 |
| `CV` | 计算机视觉 (Computer Vision) |
| `Database` | 数据库相关 |
| `DevOps` | DevOps 实践 |
| `DNS` | DNS 域名解析 |
| `Docker` | Docker 容器 |
| `Docker Compose` | Docker Compose 编排 |
| `Docker Swarm` | Docker Swarm 集群 |
| `ext4` | ext4 文件系统 |
| `Gemini` | Google Gemini |
| `Git` | Git 版本控制 |
| `GitHub` | GitHub 平台 |
| `GPU` | GPU 硬件相关 |
| `GPUStack` | GPUStack 推理平台 |
| `Hexo` | Hexo 博客框架 |
| `Homelab` | 家庭实验室 |
| `HTML` | HTML |
| `HTTP/2` | HTTP/2 协议 |
| `IDE` | IDE 编辑器 |
| `ifplugd` | ifplugd 网卡检测 |
| `JavaScript` | JavaScript |
| `JuiceFS` | JuiceFS 分布式文件系统 |
| `K8s` | Kubernetes |
| `Linux` | Linux 系统 |
| `LLM` | 大语言模型推理 |
| `LVM` | LVM 逻辑卷管理 |
| `Markdown` | Markdown 标记语言 |
| `Milvus` | Milvus 向量数据库 |
| `etcd` | etcd 分布式键值存储 |
| `Miniconda` | Miniconda 发行版 |
| `MNIST` | MNIST 数据集 |
| `mihomo` | mihomo 内核 |
| `Navicat` | Navicat 数据库客户端 |
| `Nix` | Nix 包管理器 |
| `Node.js` | Node.js 运行时 |
| `NVM` | Node Version Manager |
| `NVIDIA` | NVIDIA 硬件/驱动 |
| `OpenClash` | OpenClash 插件 |
| `OpenWrt` | OpenWrt 软路由系统 |
| `PAT` | Personal Access Token |
| `PCIe` | PCIe 总线 |
| `PostgreSQL` | PostgreSQL 数据库 |
| `Proxy` | 代理相关 |
| `PVE` | Proxmox VE 虚拟化 |
| `Python` | Python 语言 |
| `PyTorch` | PyTorch 框架 |
| `QUIC` | QUIC 协议 |
| `ripgrep` | ripgrep 搜索工具 |
| `Serial Console` | 串口控制台 |
| `SGLang` | SGLang 推理引擎 |
| `SSH` | SSH 协议 |
| `SSL` | SSL/TLS 证书 |
| `Todo Tree` | VS Code Todo Tree 插件 |
| `TortoiseGit` | TortoiseGit 客户端 |
| `Typora` | Typora 编辑器 |
| `Ubuntu` | Ubuntu 系统 |
| `uv` | uv 包管理器 |
| `vLLM` | vLLM 推理引擎 |
| `VS Code` | VS Code 编辑器 |
| `Windows` | Windows 系统 |
| `Win11` | Windows 11 |
| `WSL2` | WSL2 子系统 |
| `YOLOv8` | YOLOv8 目标检测 |

- **标签数量**：每篇文章 2-5 个标签
- **新增标签**：确需新增时，在此文档的标签表中追加并注明场景

## 辅助工具

- `scripts/subdirectory_posts.js`：自动处理子目录文章的永久链接
- `scripts/category_order.js`：自定义分类页排序（通过 `before_generate` hook + `sort_order` 字段，非侵入式，换主题不受影响）

## 分类页排序

分类页顺序由 `scripts/category_order.js` 控制，而非主题配置：

- 脚本通过 `before_generate` filter 在生成前为每个 Category 模型注入 `sort_order` 字段
- 主题 `_config.yml` 中 `category.order_by: "sort_order"` 配合使用
- 修改排序只需编辑脚本中的 `CATEGORY_ORDER` 数组即可，无需改动主题文件
- 排序顺序：AI 应用 → 基础设施 → 开发实践 → 网络与代理 → 工具与效率 → 杂谈

## 其他说明

- 暗色模式：默认 `auto`（跟随系统），可在 `_config.fluid.yml` 调整
- SEO 配置：已启用 sitemap 生成器，Google 网站验证文件为 `source/googleb0cf6bcaf11a4a08.html`
- 导航菜单：在 `_config.fluid.yml` 的 `menu` 中配置，支持子菜单