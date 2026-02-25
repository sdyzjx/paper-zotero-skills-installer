#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

BANNED = ["待补充", "TBD", "TODO"]
REQUIRED_HEADINGS = [
    r"\\section\{第一层：问题逻辑\}",
    r"\\section\{第二层：创新结构\}",
    r"\\section\{第三层：证据链验证\}",
    r"\\section\{一句话结论\}",
]
REQUIRED_PHRASES = [
    "问题定义",
    "现有方法缺口",
    "推理链",
    "创新点一",
    "创新点二",
    "消融",
]


def extract_section(text: str, title: str) -> str:
    pattern = rf"\\section\{{{re.escape(title)}\}}"
    m = re.search(pattern, text)
    if not m:
        return ""
    start = m.end()
    m2 = re.search(r"\\section\{", text[start:])
    end = start + m2.start() if m2 else len(text)
    return text[start:end].strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="QA gate for literature summary LaTeX")
    ap.add_argument("tex", help="Path to main.tex")
    args = ap.parse_args()

    p = Path(args.tex)
    if not p.is_file():
        print(f"FAIL: tex file not found: {p}")
        return 2

    text = p.read_text(encoding="utf-8", errors="ignore")
    errors: list[str] = []

    for b in BANNED:
        if b in text:
            errors.append(f"contains banned placeholder/token: {b}")

    if re.search(r"\{\{[^{}]+\}\}", text):
        errors.append("contains unresolved template placeholder: {{...}}")

    for h in REQUIRED_HEADINGS:
        if not re.search(h, text):
            errors.append(f"missing required heading: {h}")

    for pz in REQUIRED_PHRASES:
        if pz not in text:
            errors.append(f"missing required phrase: {pz}")

    # minimal density checks
    logic = extract_section(text, "第一层：问题逻辑")
    struct = extract_section(text, "第二层：创新结构")
    evidence = extract_section(text, "第三层：证据链验证")
    conclusion = extract_section(text, "一句话结论")

    if len(logic) < 220:
        errors.append("logic section too short (<220 chars)")
    if len(struct) < 220:
        errors.append("structure section too short (<220 chars)")
    if len(evidence) < 220:
        errors.append("evidence section too short (<220 chars)")
    if len(conclusion) < 20:
        errors.append("conclusion too short (<20 chars)")

    # equations gate
    if text.count("\\begin{equation}") < 2:
        errors.append("requires at least 2 equations")

    if errors:
        print("FAIL: summary QA not passed")
        for e in errors:
            print(f"- {e}")
        return 1

    print("PASS: summary QA passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
