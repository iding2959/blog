# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 [Hexo](https://hexo.io/) + [Fluid](https://github.com/fluid-dev/hexo-theme-fluid) 主题的个人技术博客，部署在 `blog.iding.qzz.io`。

## 常用命令

```bash
npm run server   # 本地预览，访问 http://localhost:4000
npm run build    # 生成静态文件到 public/ 目录
npm run clean    # 清除缓存和生成的文件
npm run deploy   # 部署到服务器（需先配置 deploy 类型）
```

## 文章管理

- 文章放在 `source/_posts/` 下，按子目录分类（frontend/backend/tools/tutorial/others 等）
- 文章永久链接格式：`:year/:month/:title/`，与子目录无关（由 `scripts/subdirectory_posts.js` 处理）
- 新建文章默认 front-matter 模板见 `scaffolds/post.md`
- 创建新页面：`hexo new page <name>`

## 配置说明

- `_config.yml`：Hexo 核心配置（站点信息、部署方式等）
- `_config.fluid.yml`：Fluid 主题配置（导航菜单、样式、功能开关等）
- 主题本身在 `themes/fluid/`，一般不需要直接修改

## 注意事项

- 分类在 `_config.fluid.yml` 的 `menu` 中手动配置，同时需要在每篇文章的 front-matter 中声明 `categories`
- 主题自定义 CSS 路径：`source/css/custom.css`
- 暗色模式默认开启（跟随系统），可通过 `_config.fluid.yml` 的 `dark_mode.default` 调整