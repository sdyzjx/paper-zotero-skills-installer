---
name: zotero-library
description: Use when the user asks to browse, read, or search a Zotero paper library by directly querying local zotero.sqlite in read-only SQL mode. Trigger on requests like "查看我的论文库", "阅读我论文库的某篇论文", "搜索我论文库里某个主题论文", "找某方向文献", and similar intents about Zotero collections/items/attachments.
---

# Zotero Library

## Overview
- Use direct local Zotero database access (`zotero.sqlite`) as the only data source in this skill.
- Keep responses in Chinese unless the user asks for another language.
- Keep access read-only and never modify Zotero data.

## Workflow
1. Detect intent from the user request.
   - Library browse intent: "查看我的论文库", "看看我有哪些论文", "列出我的文献库".
   - Paper read intent: "阅读某篇论文", "打开/查看这篇论文", "帮我读一下这篇文献".
   - Topic search intent: "搜索某主题论文", "找XX方向论文", "查和XX相关的文献".
2. Query local Zotero SQLite directly.
   - Prefer the bundled script: `/Users/doosam/.openclaw/workspace/skills/zotero-library/scripts/zotero_db_search.py`.
   - Default DB path detection order:
     - `$ZOTERO_DB_PATH`
     - `~/Zotero/zotero.sqlite`
     - `~/Library/Application Support/Zotero/zotero.sqlite`
   - Read with immutable/read-only mode to avoid lock conflicts when Zotero is running.
   - If multiple matches exist, ask one concise disambiguation question.
3. Return structured results.
   - For browse: show collection structure, item counts, and recent papers.
   - For read: show citation metadata, abstract, notes, tags, and attachment availability.
   - For topic search: show ranked matches with brief relevance reasons.
4. If database path is unavailable or unreadable, state the blocker clearly and provide the next actionable step.

## Intent Actions

### 1) Browse library
- Goal: provide a quick map of the user's library.
- Recommended command:
  - `python3 /Users/doosam/.openclaw/workspace/skills/zotero-library/scripts/zotero_db_search.py browse --limit 30`
- Minimum output:
  - Top-level collections/folders
  - Item counts per collection (if available)
  - Recently added or recently modified papers

### 2) Read a specific paper
- Goal: help user understand one target paper from the library.
- Steps:
  - Locate by title/author/year/keyword (`search` first when needed).
  - If ambiguous, present short candidate list.
  - Fetch and summarize available metadata, notes, and attachment fields.
- Recommended commands:
  - By key: `python3 /Users/doosam/.openclaw/workspace/skills/zotero-library/scripts/zotero_db_search.py read --item-key <ITEM_KEY>`
  - By ID: `python3 /Users/doosam/.openclaw/workspace/skills/zotero-library/scripts/zotero_db_search.py read --item-id <ITEM_ID>`
  - By approximate title: `python3 /Users/doosam/.openclaw/workspace/skills/zotero-library/scripts/zotero_db_search.py read --title "<title>"`
- Minimum output:
  - Standard citation (title, authors, year, venue)
  - Abstract or notes summary
  - Tags and collection location
  - Attachment status (PDF available or not)

### 3) Search papers by topic
- Goal: retrieve useful papers for a theme.
- Steps:
  - Search by topic keywords and synonyms.
  - Prefer title/abstract/tag matches.
  - If user gave constraints (year, author, venue), apply them.
- Recommended command:
  - `python3 /Users/doosam/.openclaw/workspace/skills/zotero-library/scripts/zotero_db_search.py search --query "<topic>" --limit 20`
- Minimum output:
  - Top results list
  - For each result: title, year, first author, short relevance note
  - Optional grouping by year or subtopic when result count is high

## Response Style
- Keep answers concise and scannable.
- When listing papers, use numbered lists.
- Never invent metadata; if a field is unavailable, mark it as unavailable.
- End with one suggested next action (for example: "要不要我继续精读第2篇？") when it is helpful.

## Failure Handling
- If the SQLite database file cannot be found, ask the user for the exact `zotero.sqlite` path.
- If the SQLite database is locked in normal mode, retry with read-only immutable mode.
- If `storage` files are missing, report that metadata is available but local attachment file is unavailable.
- If retrieval succeeds partially, state exactly which fields were found and which were missing.
- If the user requests write operations (add/edit/delete in Zotero), explain that this skill is read-only and cannot perform writes to `zotero.sqlite`.

## Local Query Tool
- Use the bundled script `/Users/doosam/.openclaw/workspace/skills/zotero-library/scripts/zotero_db_search.py` for deterministic queries.
- Output is JSON, suitable for downstream summarization.
- Keep raw SQL simple and avoid schema writes (`INSERT`, `UPDATE`, `DELETE`, `ALTER`, `DROP` are forbidden).
