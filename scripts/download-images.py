#!/usr/bin/env python3
"""批量下载 CSDN 图片并替换文章中的链接为本地路径。

用法:
    python scripts/download-images.py          # 处理 _posts/ 下全部文章
    python scripts/download-images.py --post 2025-07-04-vector-search-intro.md  # 单篇
"""

import os
import re
import sys
import argparse
import urllib.request
import hashlib
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"
IMAGES_DIR = ROOT / "assets" / "images" / "posts"

# CSDN 图片 URL 模式
CSDN_PATTERNS = [
    re.compile(r"https?://i-blog\.csdnimg\.cn/[^\s\)]+"),
    re.compile(r"https?://img-blog\.csdnimg\.cn/[^\s\)]+"),
    re.compile(r"https?://img-blog\.csdn\.net/[^\s\)]+"),
]

# Markdown 图片语法：![alt](url)
MD_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^\)]+)\)")

# HTML img 标签：<img src="url" ...>
HTML_IMAGE = re.compile(r'<img\s+[^>]*src="([^"]+)"[^>]*>')


def extract_csdn_urls(content: str) -> list[str]:
    """从文章内容中提取所有 CSDN 图片 URL"""
    urls = set()
    for pattern in CSDN_PATTERNS:
        urls.update(pattern.findall(content))
    return list(urls)


def download_image(url: str, save_path: Path) -> bool:
    """下载单张图片"""
    if save_path.exists():
        print(f"  [跳过] 已存在: {save_path.name}")
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_bytes(resp.read())
        print(f"  [下载] {save_path.name}")
        return True
    except Exception as e:
        print(f"  [失败] {url}: {e}")
        return False


def get_image_name(url: str) -> str:
    """从 URL 提取文件名，无法提取则用 hash"""
    path = urlparse(url).path
    name = os.path.basename(path)
    if name and "." in name:
        return name
    # 没有扩展名，用 hash 生成
    h = hashlib.md5(url.encode()).hexdigest()[:10]
    return f"{h}.png"


def replace_images_in_markdown(content: str, url_map: dict[str, str], slug: str) -> str:
    """替换 Markdown 和 HTML 中的图片链接为 Jekyll 本地路径"""
    target_dir = f"/assets/images/posts/{slug}"

    def replace_md(match):
        alt = match.group(1)
        url = match.group(2)
        if url in url_map:
            return f"![{alt}]({{{{ '{target_dir}/{url_map[url]}' | relative_url }}}})"
        return match.group(0)

    def replace_html(match):
        original = match.group(0)
        url = match.group(1)
        if url in url_map:
            return original.replace(
                f'src="{url}"',
                f'src="{{{{ \'{target_dir}/{url_map[url]}\' | relative_url }}}}"',
            )
        return original

    content = MD_IMAGE.sub(replace_md, content)
    content = HTML_IMAGE.sub(replace_html, content)
    return content


def process_post(post_path: Path) -> int:
    """处理单篇文章：下载图片并替换链接"""
    slug = post_path.stem  # YYYY-MM-DD-slug
    content = post_path.read_text(encoding="utf-8")

    urls = extract_csdn_urls(content)
    if not urls:
        print(f"[无图片] {slug}")
        return 0

    print(f"\n{'='*50}")
    print(f"处理: {post_path.name}")
    print(f"发现 {len(urls)} 张 CSDN 图片")
    print(f"{'='*50}")

    post_img_dir = IMAGES_DIR / slug
    url_map = {}

    for url in urls:
        fname = get_image_name(url)
        save_path = post_img_dir / fname
        if download_image(url, save_path):
            url_map[url] = fname

    if not url_map:
        print("  所有图片下载失败")
        return 0

    new_content = replace_images_in_markdown(content, url_map, slug)
    post_path.write_text(new_content, encoding="utf-8")
    print(f"\n  [完成] 替换 {len(url_map)} 个链接，文件已更新")
    return len(url_map)


def main():
    parser = argparse.ArgumentParser(description="下载 CSDN 图片并替换为本地路径")
    parser.add_argument("--post", help="处理单篇文章（文件名）")
    args = parser.parse_args()

    if args.post:
        post_path = POSTS_DIR / args.post
        if not post_path.exists():
            print(f"文件不存在: {post_path}")
            sys.exit(1)
        process_post(post_path)
    else:
        posts = sorted(POSTS_DIR.glob("*.md"))
        if not posts:
            print("_posts/ 目录下没有 md 文件")
            return
        total = 0
        for p in posts:
            n = process_post(p)
            total += n
        print(f"\n{'='*50}")
        print(f"全部完成，共处理 {len(posts)} 篇文章，下载 {total} 张图片")
        print(f"图片目录: {IMAGES_DIR}")
        print(f"{'='*50}")


if __name__ == "__main__":
    main()
