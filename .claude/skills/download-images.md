---
name: download-images
description: Download external images from CSDN CDN and replace links with local paths. Use when the user wants to download images in blog posts, convert CSDN image links to local, or fix broken external images. Also use when the user mentions 图片下载, 图片本地化, CSDN 图片, images broken, or after using convert-csdn.
---

Download external images referenced in blog posts and replace URLs with local Jekyll paths.

## Usage

```bash
# Process all posts in _posts/
python3 scripts/download-images.py

# Process a single post
python3 scripts/download-images.py --post 2025-07-04-vector-search-intro.md
```

## Script location
`scripts/download-images.py`

## What it does
- Scans `_posts/*.md` for CSDN image URLs (i-blog.csdnimg.cn, img-blog.csdnimg.cn)
- Downloads each image to `assets/images/posts/<slug>/`
- Replaces external URLs with Jekyll `relative_url` paths in markdown
- Skips already-downloaded images

## Important notes
- Images are stored in `assets/images/posts/<slug>/` — commit them to git
- The script is idempotent: re-running won't re-download existing files
- After running, do `bundle exec jekyll build` to verify
