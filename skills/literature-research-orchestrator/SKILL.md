---
name: literature-research-orchestrator
description: End-to-end literature research orchestration for requests like “帮我调研xxx”, “帮我找xx方向文献”, or “做一个xx综述”. Use when users need multi-paper scoping, retrieval, ranking, PDF acquisition (arXiv/IEEE), Zotero filing, per-paper deep reading, and final comparative review outputs. Do NOT take single-paper intents like “总结xxx文献/论文”; route those to `literature-summary-agent`. Always trigger intake questions first when time window, source scope, topic constraints, goals, scoring method, Zotero destination, or local output directory are missing.
---

# Literature Research Orchestrator

## Overview
Execute a complete paper-research pipeline from scope clarification to deliverables.
Enforce mandatory intake first, then run retrieval, filing, summarization, and review generation.

## Mandatory Intake (Ask First)
Ask these items before retrieval when any field is missing:
1. Confirm time window.
2. Confirm source scope (arXiv/IEEE/etc.).
3. Confirm topic include/exclude keywords.
4. Confirm research goal (Top-N only, Top-N + deep reading, review report, etc.).
5. Confirm scoring method and weights (mandatory).
6. Confirm Zotero destination collection (name/key/id).
7. Confirm local output root directory.
8. Confirm language and output format (Markdown/LaTeX/PDF).

Use the intake prompt in `references/intake-template.md`.
Use score profiles in `references/ranking-profiles.md`.
Do not start downloads or Zotero writes until intake is complete.

## Workflow
1. Freeze scope:
- Write a compact execution contract from the intake.
- Include date range, sources, topic constraints, quantity, scoring rule, Zotero target, and output path.

2. Check Zotero state:
- Use `$zotero-library` to inspect existing items and duplicates.
- Prepare dedup rules by DOI/arXiv ID/title.

3. Build candidate pool:
- Retrieve candidates only from approved sources and dates.
- Record exclusion/replacement reasons.

4. Rank and select Top-N:
- Apply user-specified scoring.
- If user is unsure, ask user to choose one profile from `references/ranking-profiles.md` and confirm tie-break rule.
- Output `top_candidates.csv` and `top_final.csv`.

5. Acquire PDFs:
- Download arXiv PDFs directly.
- Use `$ieee-zotero-save` for IEEE papers (required).
- If IEEE flow fails, use `$chrome-osascript-ops` recovery and retry（仅使用本地 chrome-osascript 方案，不走 MCP）。

6. File into Zotero:
- Create/update items, attach PDFs, and place in user-specified collection.
- Reuse existing items when possible; avoid duplicates.

7. Verify filing:
- Confirm each item exists, has readable PDF attachment, and is in target collection.
- Generate a validation table.

8. Run deep reading:
- Use `$literature-summary-agent` per paper.
- Generate per-paper outputs with problem chain, method chain, experiment setup, numeric results, and evidence assessment.
- Compile LaTeX to PDF when requested.
- Enforce mandatory second-pass refinement for every paper summary:
  - first pass generation -> SOP QA -> rewrite if needed -> recompile.
  - treat summaries as incomplete until second pass passes.

9. Build final review:
- Produce comparative synthesis across all selected papers.
- Include taxonomy, evidence strength levels, key assumptions, and actionable directions.

## Skill Invocation Order
Use this order unless user overrides:
1. `$zotero-library`
2. Retrieval/ranking step
3. `$ieee-zotero-save` (for IEEE items)
4. `$zotero-library` verification
5. `$literature-summary-agent`
6. `$chrome-osascript-ops` only for IEEE/browser failure recovery（默认浏览器自动化实现）

## Input Contract
Require these fields:
- `time_range`: start/end date
- `sources`: allowed databases (e.g., arXiv, IEEE)
- `topic_include`: required keywords
- `topic_exclude`: optional excluded topics
- `goal`: expected deliverables and quantity
- `ranking_rule`: scoring method and weights (mandatory)
- `zotero_target`: collection name/key/id
- `output_root`: local save root path
- `language`: output language
- `formats`: requested formats (md/tex/pdf)

Optional fields:
- `coverage_constraints`
- `fallback_policy`

## Output Contract
Create these artifacts under one user-approved root:
- `01_selection/top_candidates.csv`
- `01_selection/top_final.csv`
- `02_pdfs/arxiv/`
- `02_pdfs/ieee/`
- `03_summaries/<paper-slug>/main.tex`
- `03_summaries/<paper-slug>/main.pdf`
- `03_summaries/<paper-slug>/deep_reading.md`
- `04_overview/TopN_Matrix.csv`
- `04_overview/TopN_Comparative_Report.md`
- `04_overview/<Full_Review>.tex`
- `04_overview/<Full_Review>.pdf`

Use the matrix schema in `references/output-contract.md`.

## Acceptance Checklist
Enforce all checks before completion:
1. Selected count equals target count.
2. All papers satisfy date and source constraints.
3. All items exist in target Zotero collection.
4. All items have readable PDF attachments.
5. Per-paper summaries are generated.
6. Every per-paper summary passes the mandatory second-pass SOP refinement.
7. Final comparative review is generated.

## Failure and Fallback Rules
1. If IEEE access/download fails:
- Run `$chrome-osascript-ops` recovery.
- Retry `$ieee-zotero-save`.
- Replace paper only if retry fails and user allows replacement policy.

2. If duplicate found in Zotero:
- Do not create a new item.
- Attach missing PDF or add missing collection linkage.

3. If PDF is corrupted or incomplete:
- Re-download once.
- Replace with next ranked candidate and log reason.

4. If summary generation fails for one paper:
- Record failure reason and replacement decision.

## Reporting Style
- Report progress in short milestones.
- Keep a clear “done / failed / replaced” ledger.
- Include absolute paths for every deliverable.
