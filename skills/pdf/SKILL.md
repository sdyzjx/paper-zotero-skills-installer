---
name: "pdf"
description: "Vision-first PDF reading and PDF generation. Use when users ask to read/summarize/review PDFs where formulas, tables, figures, or layout matter. Default to: PDF -> PNG -> page-by-page reading, and write a markdown transcript of original content."
---

# PDF Skill

Use visual rendering as the default path for PDF understanding.

## Mandatory reading flow (updated)
1. Render PDF pages to PNG first.
2. Create `original.md` transcript file.
3. Read **one page image at a time**.
4. After each page, immediately append that page content into `original.md` before moving to next page.
5. For each page section, include:
   - 正文原文（尽量忠实）
   - 公式（用 LaTeX 形式抄写）
   - 表格数据（逐列逐行）
   - 图像内容描述（Figure caption + visual description）
6. Continue page-by-page until end, avoiding large multi-page context in one step.

## Render commands

Default full render:
```bash
python3 /Users/doosam/.openclaw/workspace/skills/pdf/scripts/pdf_to_png.py \
  /path/to/input.pdf \
  --out-dir /Users/doosam/.openclaw/workspace/tmp/pdfs/<name>/pages \
  --dpi 220 \
  --clean
```

Target pages / higher DPI:
```bash
python3 /Users/doosam/.openclaw/workspace/skills/pdf/scripts/pdf_to_png.py \
  /path/to/input.pdf \
  --out-dir /Users/doosam/.openclaw/workspace/tmp/pdfs/<name>/pages \
  --pages 1-3,8,12-15 \
  --dpi 300
```

Init transcript markdown:
```bash
python3 /Users/doosam/.openclaw/workspace/skills/pdf/scripts/init_pdf_original_md.py \
  --pdf /path/to/input.pdf \
  --out /Users/doosam/.openclaw/workspace/tmp/pdfs/<name>/original.md \
  --dpi 220
```

Detailed guidance: read `references/vision-pdf-workflow.md`.

## Dependencies
System:
```bash
# macOS
brew install poppler
```

Python (optional helpers):
```bash
uv pip install reportlab pdfplumber pypdf
```

Fallback if `uv` unavailable:
```bash
python3 -m pip install reportlab pdfplumber pypdf
```

## Output and temp conventions
- Intermediate images: `tmp/pdfs/<name>/pages/`
- Transcript (original content): `tmp/pdfs/<name>/original.md`
- Final artifacts: `output/pdf/` (or user-specified path)
- Keep stable filenames; remove stale intermediates when done.

## Quality bar
- Do not finalize summary/review until page images are checked.
- Equations, tables, and charts must be derived from rendered pages.
- Important claims should include page references.
- Re-render unclear pages (300 DPI) and overwrite corresponding page section.
