---
name: literature-summary-agent
description: Use when the user asks to summarize a paper from Zotero with requests like "帮我总结xxx文献", "总结xxx文献", "总结这篇论文", "按SOP精读这篇paper", or "把这篇文献整理成LaTeX报告". This skill must be the default trigger for Chinese intents containing “总结 + 文献/论文/paper + 题目关键词”. It finds the target item in local Zotero, locates the PDF attachment, analyzes the paper with a three-layer SOP (problem logic, innovation structure, validation logic), then creates a new folder and writes/compiles a LaTeX summary report with necessary formulas.
---

# Literature Summary Agent

## Workflow
1. Parse user intent and paper target.
- Treat requests like "帮我总结xxx文献" as direct trigger.
- Extract query constraints: title keywords, author, year, venue.

2. Search Zotero and locate the exact item.
- Run:
```bash
python3 /Users/doosam/.openclaw/workspace/skills/zotero-library/scripts/zotero_db_search.py search --query "<query>" --limit 20
```
- If multiple likely matches exist, ask one concise disambiguation question before continuing.
- After selecting one item, run:
```bash
python3 /Users/doosam/.openclaw/workspace/skills/zotero-library/scripts/zotero_db_search.py read --item-key <ITEM_KEY>
```

3. Resolve and verify PDF attachment.
- In `read` JSON output, prefer attachments where `contentType` contains `application/pdf`.
- Use `resolvedPath` as local PDF path and verify file exists.
- If no PDF is available, stop and report blocker clearly.

4. Read and summarize with the three-layer SOP (vision-first required).
- Follow the detailed checklist in `references/sop.md`.
- Prioritize reasoning chain over narration.
- Avoid generic summary. Reconstruct: why the method was proposed, how it is implemented, and whether evidence supports claims.
- Language rule: default to Chinese for all summary content and LaTeX report text unless the user explicitly requests another language.
- Mandatory PDF reading path:
  1) Render PDF to PNG with `/Users/doosam/.openclaw/workspace/skills/pdf/scripts/pdf_to_png.py`.
  2) Initialize transcript markdown with `/Users/doosam/.openclaw/workspace/skills/pdf/scripts/init_pdf_original_md.py`.
  3) Process pages one-by-one and append to `original.md` page sections (正文、公式原位、表格、图片描述), then continue next page.
  4) Use this transcript as the primary evidence source for SOP writing.

5. Create a LaTeX project folder and draft report.
- Use the bundled script:
```bash
python3 /Users/doosam/.openclaw/workspace/skills/literature-summary-agent/scripts/init_summary_project.py \
  --title "<paper title>" \
  --output-root "<target root>"
```
- This creates `<YYYYMMDD>-<slug>/main.tex` from `assets/summary_template.tex`.
- Fill all placeholders with paper-specific content.

6. Include necessary equations.
- Add only equations that are central to the paper's reasoning.
- For each equation, explain:
  - Variable definitions
  - Role in method/training/inference
  - How it links to claimed improvement

7. Run QA gate before compile (required).
- Use:
```bash
python3 /Users/doosam/.openclaw/workspace/skills/literature-summary-agent/scripts/qa_summary_tex.py <summary_dir>/main.tex
```
- Must pass all checks before compile:
  - no placeholders (`待补充`, `TBD`, `TODO`, `{{...}}`)
  - all three SOP layers exist and have non-trivial content
  - at least 2 equations exist

8. Compile LaTeX and verify output.
- Prefer one command (includes QA + compile):
```bash
/Users/doosam/.openclaw/workspace/skills/literature-summary-agent/scripts/compile_tex.sh <summary_dir>
```
- The script runs in login shell to load TeX PATH on macOS and uses `latexmk`/`pdflatex` fallback automatically.
- If first compile fails, inspect `main.log`, repair once, rerun compile.
- Do not deliver PDF unless compile succeeds.

9. Mandatory SOP refinement pass (required).
- After first draft is generated, re-open `deep_reading.md` and `main.tex` and run a second-pass SOP quality check.
- Required checks:
  - Logic layer is explicit: `Problem/Gap/Reasoning` all present and paper-specific.
  - Structure layer has at least 2 innovations, each with `Principle/Implementation/Effect`.
  - Evidence layer includes concrete experiment setup + numeric results + baseline/ablation evidence.
  - No template placeholders (`待补充`, `TBD`, `TODO`) and no generic-only wording.
- If any check fails, rewrite and recompile before finishing.
- Record the second-pass outcome in a short local QA note (e.g., `refine_pass.md` or equivalent log in the summary folder).

10. Return deliverables.
- Provide:
  - Selected Zotero item (title/authors/year)
  - PDF path used
  - Output folder path
  - `main.tex` path
  - Compiled PDF path (if compile succeeded)

## Output Standard
- Keep summary aligned with three layers:
  - Logic layer: Problem -> Gap -> Reasoning -> Innovation jump
  - Structure layer: Principle -> Implementation -> Effect for each innovation
  - Evidence layer: SOTA comparison, ablation validity, hypothesis validation
- For writing depth (mandatory):
  - `现有方法缺口` must be long-form and concrete (not bullet-only slogans). Include at least: task assumptions, failure modes, and why existing methods fail under target constraints.
  - `从问题到创新的推理链` must explicitly show the full causal chain: problem pressure -> requirement decomposition -> design choice -> expected mechanism -> testable hypothesis.
  - `创新点` must be rich and complete. For each innovation, include:
    1) what exact bottleneck it targets,
    2) why prior alternatives are insufficient,
    3) how the module/algorithm works step-by-step,
    4) what measurable effect is expected.
  - Avoid short generic prose; prioritize logically connected, paper-specific argumentation.
- Enforce second-pass refinement before output is considered complete.
- End with one-sentence conclusion:
  - "这篇论文成立/部分成立/证据不足，因为……"

## Known Issues & Fixes (from real runs)
- For detailed repair steps, read `references/troubleshooting.md`.
- Issue: Generated PDF looked empty/placeholder-only.
  - Root cause: template placeholders not fully replaced before compile.
  - Fix: run `qa_summary_tex.py` before every compile; fail hard on placeholders and low-content sections.
- Issue: `latexmk`/`xelatex` not found even though MacTeX is installed.
  - Root cause: non-login shell PATH missing `/Library/TeX/texbin`.
  - Fix: compile through `compile_tex.sh` (uses `zsh -lc` and PATH export).
- Issue: PDF was sent but content quality was generic.
  - Root cause: SOP refinement pass skipped or weak evidence layer.
  - Fix: enforce second-pass checks with numeric results + baseline/ablation evidence and record `refine_pass.md`.

## Failure Handling
- Zotero DB not found: request explicit `zotero.sqlite` path.
- Item ambiguous: show top candidates and ask user to pick one.
- PDF missing: report metadata found and attachment missing.
- Compile failure: return exact error location and provide a fixed `main.tex` draft.
