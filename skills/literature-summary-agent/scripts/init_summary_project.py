#!/usr/bin/env python3
"""Initialize a LaTeX paper-summary project from the bundled template."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
from pathlib import Path


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "paper"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create LaTeX summary project")
    parser.add_argument("--title", required=True, help="Paper title")
    parser.add_argument("--output-root", default=".", help="Where to create the folder")
    parser.add_argument("--slug", default=None, help="Optional folder slug")
    parser.add_argument("--compile", action="store_true", help="Compile after creation")
    return parser.parse_args()


def compile_latex(target_dir: Path) -> None:
    if shutil.which("latexmk"):
        cmd = ["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]
        subprocess.run(cmd, cwd=target_dir, check=True)
        return

    if not shutil.which("pdflatex"):
        raise RuntimeError("Neither latexmk nor pdflatex is available in PATH")

    cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]
    subprocess.run(cmd, cwd=target_dir, check=True)
    subprocess.run(cmd, cwd=target_dir, check=True)


def main() -> int:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    template_path = script_dir.parent / "assets" / "summary_template.tex"
    if not template_path.is_file():
        raise FileNotFoundError(f"Template not found: {template_path}")

    today = dt.date.today().strftime("%Y%m%d")
    slug = args.slug or slugify(args.title)
    target_dir = Path(args.output_root).expanduser().resolve() / f"{today}-{slug}"
    target_dir.mkdir(parents=True, exist_ok=True)

    template = template_path.read_text(encoding="utf-8")
    filled = (
        template.replace("{{PAPER_TITLE}}", args.title)
        .replace("{{REPORT_DATE}}", dt.date.today().isoformat())
        .replace("{{AUTHORS}}", "待补充")
        .replace("{{YEAR_VENUE}}", "待补充")
        .replace("{{ITEM_KEY}}", "待补充")
        .replace("{{PDF_PATH}}", "待补充")
        .replace("{{PROBLEM}}", "待补充")
        .replace("{{GAP}}", "待补充")
        .replace("{{REASONING}}", "待补充")
        .replace("{{INNOVATION_SUMMARY}}", "待补充")
        .replace("{{INNOVATION1_NAME}}", "待补充")
        .replace("{{INNOVATION1_PRINCIPLE}}", "待补充")
        .replace("{{INNOVATION1_IMPLEMENTATION}}", "待补充")
        .replace("{{INNOVATION1_EFFECT}}", "待补充")
        .replace("{{INNOVATION2_NAME}}", "待补充")
        .replace("{{INNOVATION2_PRINCIPLE}}", "待补充")
        .replace("{{INNOVATION2_IMPLEMENTATION}}", "待补充")
        .replace("{{INNOVATION2_EFFECT}}", "待补充")
        .replace("{{EQUATION1}}", "\\mathcal{L}_{\\text{total}} = \\mathcal{L}_{\\text{task}} + \\lambda \\mathcal{L}_{\\text{reg}}")
        .replace("{{EQUATION1_EXPLAIN}}", "定义所有符号，并说明该目标函数为何是方法核心。")
        .replace("{{EQUATION2}}", "\\hat{y} = f_{\\theta}(x)")
        .replace("{{EQUATION2_EXPLAIN}}", "说明该映射在模型中的实现方式与评估作用。")
        .replace("{{OVERALL_COMPARISON}}", "待补充")
        .replace("{{ABLATION_EVIDENCE}}", "待补充")
        .replace("{{HYPOTHESIS_VALIDATION}}", "待补充")
        .replace("{{CAUSAL_CHECK}}", "待补充")
        .replace("{{ONE_SENTENCE_CONCLUSION}}", "待补充")
    )

    tex_path = target_dir / "main.tex"
    tex_path.write_text(filled, encoding="utf-8")

    if args.compile:
        compile_latex(target_dir)

    print(target_dir)
    print(tex_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
