#!/usr/bin/env python3
"""将 CSDN 导出的 Markdown 文件批量转换为 Jekyll 格式。

批量模式（推荐）:
    python scripts/convert-csdn.py \
      --input ~/Downloads/csdn-posts/ \
      --output _posts/ \
      --tags "AI,技术"

交互模式:
    python scripts/convert-csdn.py --input ~/Downloads/csdn-posts/

单文件模式:
    python scripts/convert-csdn.py --file ~/Downloads/csdn-posts/某篇文章.md

功能:
    1. 从文件名/首行标题提取文章标题
    2. 生成 Jekyll Front Matter (title, date, tags)
    3. 文件名转英文 slug（中文→拼音，数字/英文保留）
    4. 移除 CSDN 特有语法 (@[toc], @[TOC])
    5. 按 Jekyll 规范命名输出文件 (YYYY-MM-DD-slug.md)
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List

ROOT = Path(__file__).resolve().parent.parent


# ── Slug 生成 ──────────────────────────────────────────
try:
    from pypinyin import lazy_pinyin, Style
    HAS_PYPINYIN = True
except ImportError:
    HAS_PYPINYIN = False


def title_to_slug(title: str) -> str:
    """将中文标题转为英文 slug，优先用拼音"""
    title = title.strip().strip("#").strip()
    # 移除常见前缀：数字序号、【】
    title = re.sub(r"^[\d\.\s、]+", "", title)
    title = re.sub(r"[【】]", " ", title)

    if HAS_PYPINYIN:
        parts = lazy_pinyin(title, style=Style.NORMAL, errors="ignore")
        slug = "-".join(p for p in parts if p.strip())
    else:
        slug = title

    # 只保留字母、数字、连字符、下划线
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff_-]", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    slug = slug.strip("-").lower()

    # 如果 slug 太短或全中文，用 hash
    if len(slug) < 3 or not re.search(r"[a-z0-9]", slug):
        import hashlib
        h = hashlib.md5(title.encode()).hexdigest()[:8]
        slug = f"post-{h}"

    return slug or "untitled"


# ── 元数据提取 ──────────────────────────────────────────
def extract_title_from_filename(filename: str) -> str:
    """从 CSDN 导出文件名提取标题"""
    name = Path(filename).stem
    # 移除常见的 CSDN 前缀/后缀
    name = re.sub(r"^[\d_]+", "", name)
    name = re.sub(r"[【】\[\]]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def extract_title_from_content(content: str) -> Optional[str]:
    """从正文第一个 # 标题提取"""
    m = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def extract_date_from_filename(filename: str) -> Optional[str]:
    """尝试从文件名提取日期"""
    name = Path(filename).stem
    # 匹配 YYYY-MM-DD, YYYYMMDD, YYYY.MM.DD
    for pat in [r"(\d{4})-(\d{2})-(\d{2})", r"(\d{4})(\d{2})(\d{2})", r"(\d{4})\.(\d{2})\.(\d{2})"]:
        m = re.search(pat, name)
        if m:
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


# ── 内容清理 ────────────────────────────────────────────
def clean_content(content: str) -> str:
    """移除 CSDN 特有语法"""
    # 先处理 BOM
    content = content.lstrip("\ufeff")
    # @[toc] / @[TOC] / @[TOC](文章目录) / [toc]
    content = re.sub(r"^@\[toc\](\([^)]*\))?\s*$", "", content, flags=re.MULTILINE | re.IGNORECASE)
    content = re.sub(r"^\[toc\]\s*$", "", content, flags=re.MULTILINE | re.IGNORECASE)
    # 移除开头的空行
    content = content.lstrip("\n")
    return content


# ── 核心转换 ────────────────────────────────────────────
def convert_file(
    src: Path,
    dst_dir: Path,
    *,
    tags: Optional[List[str]] = None,
    date: Optional[str] = None,
    slug: Optional[str] = None,
    title: Optional[str] = None,
    dry_run: bool = False,
) -> bool:
    """转换单个 md 文件"""
    content = src.read_text(encoding="utf-8", errors="replace")

    # 提取标题
    if not title:
        title = extract_title_from_content(content) or extract_title_from_filename(src.name)
    if not title:
        print(f"  [跳过] 无法提取标题: {src.name}")
        return False

    # 提取日期
    if not date:
        date = extract_date_from_filename(src.name)
    if not date:
        date = datetime.fromtimestamp(src.stat().st_mtime).strftime("%Y-%m-%d")

    # 生成 slug
    if not slug:
        slug = title_to_slug(title)

    # 生成 Jekyll 文件名
    jekyll_name = f"{date}-{slug}.md"
    dst = dst_dir / jekyll_name

    if dst.exists() and not dry_run:
        print(f"  [警告] 目标文件已存在，跳过: {jekyll_name}")
        return False

    # 构建 Front Matter
    tags_str = ", ".join(tags) if tags else ""
    fm = "---\n"
    fm += f'title: "{title}"\n'
    fm += f"date: {date}\n"
    if tags:
        fm += f"tags: [{tags_str}]\n"
    fm += "---\n\n"

    # 清理内容
    body = clean_content(content)
    # 如果正文首行是标题（与 title 相同），去掉避免重复
    body = re.sub(rf"^#\s+{re.escape(title)}\s*\n", "", body, count=1)

    output = fm + body

    if dry_run:
        print(f"  [预览] {src.name}")
        print(f"          -> {jekyll_name}")
        print(f"          title: {title}")
        print(f"          date: {date}")
        print(f"          tags: {tags_str}")
        print(f"          slug: {slug}")
        return True

    dst.write_text(output, encoding="utf-8")
    print(f"  [转换] {src.name} -> {jekyll_name}")
    return True


# ── CLI ─────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="CSDN Markdown → Jekyll 格式转换器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览转换结果（不写入文件）
  python scripts/convert-csdn.py --input ~/csdn-posts/ --dry-run

  # 批量转换，统一标签
  python scripts/convert-csdn.py --input ~/csdn-posts/ --output _posts/ --tags "AI,技术"

  # 转换单文件
  python scripts/convert-csdn.py --file ~/csdn-posts/向量检索入门.md --output _posts/
""",
    )
    parser.add_argument("--input", help="CSDN md 文件所在目录")
    parser.add_argument("--file", help="转换单个文件")
    parser.add_argument("--output", default="_posts", help="输出目录（默认 _posts）")
    parser.add_argument("--tags", help="统一标签，逗号分隔")
    parser.add_argument("--date", help="统一日期 YYYY-MM-DD（不指定则从文件名/文件时间提取）")
    parser.add_argument("--slug", help="统一 slug（批量模式不建议使用）")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际写入")
    args = parser.parse_args()

    if not args.input and not args.file:
        parser.print_help()
        sys.exit(1)

    # 切换到项目根目录
    os.chdir(ROOT)
    dst_dir = Path(args.output)
    dst_dir.mkdir(parents=True, exist_ok=True)

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None

    # 单文件模式
    if args.file:
        src = Path(args.file)
        if not src.exists():
            print(f"文件不存在: {src}")
            sys.exit(1)
        convert_file(src, dst_dir, tags=tags, date=args.date, slug=args.slug, dry_run=args.dry_run)
        return

    # 批量模式
    src_dir = Path(args.input)
    if not src_dir.is_dir():
        print(f"目录不存在: {src_dir}")
        sys.exit(1)

    md_files = sorted(src_dir.glob("*.md"))
    if not md_files:
        print(f"目录下没有 .md 文件: {src_dir}")
        sys.exit(1)

    print(f"发现 {len(md_files)} 个 Markdown 文件\n")

    ok = 0
    for f in md_files:
        if convert_file(f, dst_dir, tags=tags, date=args.date, slug=args.slug, dry_run=args.dry_run):
            ok += 1

    action = "预览" if args.dry_run else "转换"
    print(f"\n{action}完成: {ok}/{len(md_files)} 篇")


if __name__ == "__main__":
    main()
