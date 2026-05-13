---
name: convert-csdn
description: Convert CSDN exported Markdown files to Jekyll blog format. Use when the user wants to import, convert, or migrate CSDN blog posts to this Jekyll blog. Also use when the user mentions CSDN import, CSDN 导入, 博客迁移, CSDN 转换.
---

Convert CSDN Markdown export files to Jekyll-compatible blog posts.

## Usage

```bash
# Preview mode (see what will change without writing files)
python3 scripts/convert-csdn.py --input <path-to-csdn-md-dir> --dry-run

# Batch convert
python3 scripts/convert-csdn.py --input <path-to-csdn-md-dir> --output _posts/ [--tags "tag1,tag2"]

# Single file
python3 scripts/convert-csdn.py --file <path-to-single-md> --output _posts/
```

## Script location
`scripts/convert-csdn.py`

## What it does
- Removes CSDN-specific syntax (`@[toc]`)
- Extracts title from filename or first markdown heading
- Generates Jekyll Front Matter (title, date, tags)
- Converts Chinese filenames to pinyin English slugs
- Names output files as `YYYY-MM-DD-slug.md`

## Important notes
- Always run `--dry-run` first to preview results
- After conversion, run the download-images skill to handle external images
- The script requires `pypinyin`. If missing: `pip3 install pypinyin`
