# Vision-first PDF reading workflow (page-by-page, markdown transcript)

## Goal
Convert PDF to PNG first, then read images **one page at a time** and write a faithful markdown transcript (`original.md`) to avoid context overflow.

## Canonical process
1. Render PDF pages to PNG.
2. Create transcript markdown file.
3. Process page `i` only:
   - Read image `page-i.png`.
   - Write page content to markdown section `## Page i`.
   - Include:
     - body text (as faithful as possible)
     - formulas (LaTeX style if possible)
     - table data (row/column values)
     - figure descriptions (if image exists)
4. Save and continue with page `i+1`.
5. Repeat until all pages are done.

## Required markdown structure

```markdown
# PDF 原文转写

- Source PDF: /abs/path/to/file.pdf
- Render DPI: 220
- Generated at: YYYY-MM-DD HH:mm:ss

## Page 1
### 正文
...

### 公式
- (1) ...

### 表格
- Table 1:
  - 列: ...
  - 行1: ...

### 图片描述
- Fig. 1: ...

## Page 2
...
```

## Commands

Render:
```bash
python3 /Users/doosam/.openclaw/workspace/skills/pdf/scripts/pdf_to_png.py \
  /path/to/input.pdf \
  --out-dir /Users/doosam/.openclaw/workspace/tmp/pdfs/<name>/pages \
  --dpi 220 \
  --clean
```

Init markdown:
```bash
python3 /Users/doosam/.openclaw/workspace/skills/pdf/scripts/init_pdf_original_md.py \
  --pdf /path/to/input.pdf \
  --out /Users/doosam/.openclaw/workspace/tmp/pdfs/<name>/original.md \
  --dpi 220
```

## Context-safety rule
- Never batch too many pages in one reasoning step.
- Strictly process one page then persist to markdown, then move to next page.
- If formula/table is unclear, re-render that page at 300 DPI and overwrite that page section.
