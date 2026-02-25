#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 1 ]; then
  echo "Usage: $0 <summary_dir>"
  exit 1
fi
DIR="$1"
if [ ! -d "$DIR" ]; then
  echo "Directory not found: $DIR"
  exit 1
fi
python3 "/Users/doosam/.openclaw/workspace/skills/literature-summary-agent/scripts/qa_summary_tex.py" "$DIR/main.tex"
zsh -lc "export PATH='/Library/TeX/texbin:$PATH'; cd '$DIR'; if command -v latexmk >/dev/null 2>&1; then latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex; else pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex; fi"
