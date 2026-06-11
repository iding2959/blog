# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## 项目概述

基于 **Hexo 7.3.0** + **Fluid 1.9.8** 主题的个人技术博客，部署至 `blog.iding.qzz.io`。

## 常用命令

```bash
npm run server   # 本地预览 http://localhost:4000
npm run build    # 生成静态文件到 public/
npm run clean    # 清除缓存和生成文件
```

## 文章管理

- 文章存放：`source/_posts/` 下按子目录分类（backend/frontend/tools/tutorial/others）
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
- 五大一级分类：**前端、后端、工具、教程、其他**
- 嵌套分类示例：
  ```yaml
  categories:
    - 工具
    - Python
  ```
- 子目录使用英文命名（backend/frontend/tools/tutorial/others）

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

## 辅助工具

- `scripts/subdirectory_posts.js`：自动处理子目录文章的永久链接

## 其他说明

- 暗色模式：默认 `auto`（跟随系统），可在 `_config.fluid.yml` 调整
- SEO 配置：已启用 sitemap 生成器，Google 网站验证文件为 `source/googleb0cf6bcaf11a4a08.html`
- 导航菜单：在 `_config.fluid.yml` 的 `menu` 中配置，支持子菜单