#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def parse_pages(spec: str, total_hint: int | None = None):
    pages = set()
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            a, b = int(a), int(b)
            if a > b:
                a, b = b, a
            pages.update(range(a, b + 1))
        else:
            pages.add(int(part))
    if total_hint:
        pages = {p for p in pages if 1 <= p <= total_hint}
    return sorted(pages)


def main():
    p = argparse.ArgumentParser(description="Render PDF pages to PNG with pdftoppm")
    p.add_argument("pdf", help="input PDF path")
    p.add_argument("--out-dir", default="tmp/pdfs/pages", help="output directory")
    p.add_argument("--dpi", type=int, default=220, help="render DPI (default: 220)")
    p.add_argument("--pages", default="", help="page spec, e.g. 1-3,7,10-12")
    p.add_argument("--prefix", default="page", help="output filename prefix")
    p.add_argument("--clean", action="store_true", help="remove existing PNGs in out-dir first")
    args = p.parse_args()

    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.exists():
        print(f"ERROR: PDF not found: {pdf}", file=sys.stderr)
        sys.exit(2)

    if shutil.which("pdftoppm") is None:
        print("ERROR: pdftoppm not found. Install Poppler first.", file=sys.stderr)
        sys.exit(3)

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.clean:
        for f in out_dir.glob("*.png"):
            f.unlink(missing_ok=True)

    prefix_path = out_dir / args.prefix

    if args.pages:
        pages = parse_pages(args.pages)
        if not pages:
            print("ERROR: no valid pages in --pages", file=sys.stderr)
            sys.exit(4)
        for pg in pages:
            cmd = [
                "pdftoppm", "-f", str(pg), "-singlefile", "-r", str(args.dpi), "-png",
                str(pdf), str(prefix_path.with_name(f"{args.prefix}_{pg:04d}"))
            ]
            subprocess.run(cmd, check=True)
    else:
        cmd = ["pdftoppm", "-r", str(args.dpi), "-png", str(pdf), str(prefix_path)]
        subprocess.run(cmd, check=True)

    pngs = sorted(out_dir.glob("*.png"))
    print(f"OK: rendered {len(pngs)} page image(s) to {out_dir}")
    for f in pngs:
        print(str(f))


if __name__ == "__main__":
    main()
