#!/usr/bin/env python3
import argparse
from datetime import datetime
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Initialize markdown transcript for page-by-page PDF vision reading")
    ap.add_argument("--pdf", required=True, help="source pdf path")
    ap.add_argument("--out", required=True, help="output markdown path")
    ap.add_argument("--dpi", type=int, default=220, help="render dpi")
    args = ap.parse_args()

    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""# PDF 原文转写

- Source PDF: {Path(args.pdf).expanduser().resolve()}
- Render DPI: {args.dpi}
- Generated at: {ts}

"""
    out.write_text(content, encoding="utf-8")
    print(str(out))


if __name__ == "__main__":
    main()
