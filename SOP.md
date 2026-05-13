# 博客文章发布 SOP

## 一、创建文章文件

在 `_posts/` 目录下新建 Markdown 文件，命名格式：

```
YYYY-MM-DD-slug.md
```

示例：`2026-05-15-building-a-simple-database.md`

## 二、编写 Front Matter

在文件顶部填写元数据（`---` 包裹）：

```yaml
---
layout: post
title: "文章标题"
date: 2026-05-15
tags: [Rust, Database, Systems]
read_time: "6 分钟"
---
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `layout` | 是 | 固定为 `post` |
| `title` | 是 | 文章标题，双引号包裹 |
| `date` | 是 | 发布日期，格式 `YYYY-MM-DD` |
| `tags` | 否 | 标签列表，用逗号分隔 |
| `read_time` | 否 | 预估阅读时间 |
| `featured` | 否 | 设为 `true` 标记为精选文章 |

## 三、编写正文

Front Matter 下方用 Markdown 写正文：

```markdown
---
layout: post
title: "从零构建一个简易数据库"
date: 2026-05-15
tags: [Database, Rust]
read_time: "10 分钟"
---

## 引言

为什么从零构建数据库是理解系统的绝佳方式……

## 核心架构

```

支持标准 Markdown 语法：标题、列表、代码块、引用、链接、图片等。

## 四、本地预览

```bash
cd /Users/mars/Work/white_blog

# 确保使用 Homebrew Ruby
export PATH="/opt/homebrew/opt/ruby@3.2/bin:$PATH"

# 启动预览服务器
bundle exec jekyll serve

# 浏览器打开 http://localhost:4000
```

修改文件后自动重新生成，刷新页面即可看到效果。

## 五、发布上线

```bash
cd /Users/mars/Work/white_blog

# 1. 添加文章文件
git add _posts/YYYY-MM-DD-slug.md

# 2. 提交
git commit -m "Add post: 文章标题"

# 3. 推送到 GitHub
git push

# 等待 1-2 分钟自动部署
```

## 六、验证

推送后 1-2 分钟，访问 https://superwhite18.github.io 确认：

- [ ] 首页能看到新文章卡片
- [ ] 点击卡片能进入文章详情页
- [ ] 标签、日期、阅读时间显示正确
- [ ] 代码块、图片等正常渲染

---

## 常见问题

**Q: 文章没有出现在首页？**
检查 Front Matter 中的 `date` 是否填了未来的日期。Jekyll 只显示当前日期及之前的文章。另外确认首页文章数量是否超过分页上限（默认 5 篇），超出会出现在第 2 页。

**Q: 本地预览报错？**
```bash
# 确保使用正确 Ruby 版本
export PATH="/opt/homebrew/opt/ruby@3.2/bin:$PATH"
bundle exec jekyll serve
```

**Q: push 后网站没更新？**
查看构建状态：https://github.com/SuperWhite18/superwhite18.github.io/actions
如果构建失败，查看错误日志修复后重新 push。

**Q: 文章链接是什么格式？**
默认格式：`https://superwhite18.github.io/posts/slug/`
其中 `slug` 是文件名的 `YYYY-MM-DD-slug.md` 中 `slug` 部分。
