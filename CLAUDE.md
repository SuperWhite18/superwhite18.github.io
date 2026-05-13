# White Blog — Claude 项目指令

## 项目概述

基于 Jekyll 的技术博客，部署在 GitHub Pages：https://superwhite18.github.io

## 常用命令

```bash
# 本地预览
export PATH="/opt/homebrew/opt/ruby@3.2/bin:$PATH"
bundle exec jekyll serve                    # http://localhost:4000

# 构建验证
bundle exec jekyll build

# 发布
git add <files> && git commit -m "..." && git push
# 推送后 1-2 分钟自动部署
```

## 目录结构

```
_config.yml       # Jekyll 配置（site title, url, paginate 等）
_layouts/         # default（骨架）, home（首页）, post（文章详情）
_includes/        # head, nav, sidebar, footer, search
_posts/           # Markdown 文章，命名: YYYY-MM-DD-slug.md
assets/           # css（style.scss）, js（main.js）, images/posts/
scripts/          # 工具脚本
SOP.md            # 发布操作手册
```

## 文章格式

每篇 `_posts/` 下的 Markdown 文件需要 Front Matter：

```yaml
---
layout: post
title: "文章标题"
date: 2025-07-04
tags: [标签1, 标签2]
read_time: "5 分钟"
featured: false
---
```

## 工具脚本

### CSDN 文章导入

当用户提到「导入 CSDN 文章」「CSDN 转换」「博客迁移」时：

```bash
# 1. 预览转换结果
python3 scripts/convert-csdn.py --input <目录> --dry-run

# 2. 正式转换
python3 scripts/convert-csdn.py --input <目录> --output _posts/ --tags "标签"

# 3. 下载文章中的远程图片到本地
python3 scripts/download-images.py

# 4. 本地预览验证
bundle exec jekyll build
```

### 图片本地化

当用户提到「下载图片」「图片本地化」「图片无法显示」时：

```bash
# 批量处理所有文章
python3 scripts/download-images.py

# 单篇文章
python3 scripts/download-images.py --post <文件名>
```
