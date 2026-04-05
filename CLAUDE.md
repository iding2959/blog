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

## 图片路径规范

- 文章中引用的图片统一放在 `source/img/` 目录下
- Markdown 中图片路径使用相对路径 `../../../img/...`（三层 `../` 回到 `source/` 根目录）
- 禁止使用 `/img/...` 或 `/source/img/...`，前者本地预览会找不到，后者 Hexo 部署后会找不到

## 分类规范

- 分类使用 front-matter 中的 `categories` 字段，而非 source/_posts/ 的子目录结构
- 五大一级分类：**前端、后端、工具、教程、其他**
- 支持嵌套分类，用多行列表格式：
  ```yaml
  categories:
    - 工具
    - Python
  ```
- 子目录按需创建，使用英文名称（如 python/、frontend/、docker/），不可用中文
- 单级分类直接写：`categories: 前端`
- source/_posts/ 下只放五大类目录，文章按实际分类设置 front-matter

## 注意事项

- 分类在 `_config.fluid.yml` 的 `menu` 中手动配置
- 主题自定义 CSS 路径：`source/css/custom.css`
- 暗色模式默认开启（跟随系统），可通过 `_config.fluid.yml` 的 `dark_mode.default` 调整