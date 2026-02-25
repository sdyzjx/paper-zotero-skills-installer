#!/usr/bin/env python3
"""Read-only Zotero SQLite query helper for browse/search/read workflows."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import quote


def default_db_candidates() -> list[Path]:
    home = Path.home()
    candidates: list[Path] = []
    env_val = None
    try:
        import os

        env_val = os.environ.get("ZOTERO_DB_PATH")
    except Exception:
        env_val = None
    if env_val:
        candidates.append(Path(env_val).expanduser())
    candidates.extend(
        [
            home / "Zotero" / "zotero.sqlite",
            home / "Library" / "Application Support" / "Zotero" / "zotero.sqlite",
        ]
    )
    # Keep stable order while removing duplicates.
    seen = set()
    deduped: list[Path] = []
    for p in candidates:
        key = str(p)
        if key not in seen:
            seen.add(key)
            deduped.append(p)
    return deduped


def resolve_db_path(db_arg: str | None) -> Path:
    if db_arg:
        p = Path(db_arg).expanduser()
        if p.is_file():
            return p
        raise FileNotFoundError(f"Database not found: {p}")
    for p in default_db_candidates():
        if p.is_file():
            return p
    raise FileNotFoundError(
        "Could not find zotero.sqlite. Set --db or environment variable ZOTERO_DB_PATH."
    )


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{quote(str(db_path))}?mode=ro&immutable=1"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


BASE_SELECT = """
WITH field_values AS (
  SELECT
    d.itemID,
    MAX(CASE WHEN f.fieldName='title' THEN v.value END) AS title,
    MAX(CASE WHEN f.fieldName='date' THEN v.value END) AS date,
    MAX(CASE WHEN f.fieldName='publicationTitle' THEN v.value END) AS publicationTitle,
    MAX(CASE WHEN f.fieldName='abstractNote' THEN v.value END) AS abstractNote,
    MAX(CASE WHEN f.fieldName='DOI' THEN v.value END) AS doi,
    MAX(CASE WHEN f.fieldName='url' THEN v.value END) AS url
  FROM itemData d
  JOIN fieldsCombined f ON f.fieldID = d.fieldID
  JOIN itemDataValues v ON v.valueID = d.valueID
  GROUP BY d.itemID
),
author_rows AS (
  SELECT
    ic.itemID,
    ic.orderIndex,
    CASE
      WHEN c.fieldMode = 1 THEN COALESCE(c.lastName, '')
      ELSE TRIM(COALESCE(c.firstName, '') || ' ' || COALESCE(c.lastName, ''))
    END AS authorName
  FROM itemCreators ic
  JOIN creators c ON c.creatorID = ic.creatorID
),
authors AS (
  SELECT itemID, GROUP_CONCAT(authorName, ', ') AS authors
  FROM (
    SELECT itemID, authorName
    FROM author_rows
    WHERE authorName != ''
    ORDER BY itemID, orderIndex
  )
  GROUP BY itemID
),
tags_joined AS (
  SELECT it.itemID, GROUP_CONCAT(t.name, ', ') AS tags
  FROM itemTags it
  JOIN tags t ON t.tagID = it.tagID
  GROUP BY it.itemID
),
collections_joined AS (
  SELECT ci.itemID, GROUP_CONCAT(c.collectionName, ' | ') AS collections
  FROM collectionItems ci
  JOIN collections c ON c.collectionID = ci.collectionID
  GROUP BY ci.itemID
),
attachment_stats AS (
  SELECT
    parentItemID AS itemID,
    COUNT(*) AS attachment_count,
    SUM(CASE WHEN contentType LIKE 'application/pdf%%' THEN 1 ELSE 0 END) AS pdf_count
  FROM itemAttachments
  WHERE parentItemID IS NOT NULL
  GROUP BY parentItemID
)
SELECT
  i.itemID,
  i.key AS itemKey,
  itc.typeName AS itemType,
  i.dateAdded,
  i.dateModified,
  COALESCE(fv.title, '') AS title,
  COALESCE(fv.date, '') AS date,
  COALESCE(fv.publicationTitle, '') AS publicationTitle,
  COALESCE(fv.abstractNote, '') AS abstractNote,
  COALESCE(fv.doi, '') AS doi,
  COALESCE(fv.url, '') AS url,
  COALESCE(a.authors, '') AS authors,
  COALESCE(t.tags, '') AS tags,
  COALESCE(cj.collections, '') AS collections,
  COALESCE(ast.attachment_count, 0) AS attachmentCount,
  COALESCE(ast.pdf_count, 0) AS pdfCount
FROM items i
JOIN itemTypesCombined itc ON itc.itemTypeID = i.itemTypeID
LEFT JOIN field_values fv ON fv.itemID = i.itemID
LEFT JOIN authors a ON a.itemID = i.itemID
LEFT JOIN tags_joined t ON t.itemID = i.itemID
LEFT JOIN collections_joined cj ON cj.itemID = i.itemID
LEFT JOIN attachment_stats ast ON ast.itemID = i.itemID
WHERE itc.typeName NOT IN ('attachment', 'note', 'annotation')
"""


def fetch_rows(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
    cur = conn.execute(sql, params)
    return [dict(row) for row in cur.fetchall()]


def cmd_browse(conn: sqlite3.Connection, limit: int) -> dict[str, Any]:
    rows = fetch_rows(
        conn,
        f"""
        {BASE_SELECT}
        ORDER BY dateModified DESC
        LIMIT ?
        """,
        (limit,),
    )
    col_rows = fetch_rows(
        conn,
        """
        SELECT
          c.collectionID,
          c.collectionName,
          c.parentCollectionID,
          COUNT(ci.itemID) AS itemCount
        FROM collections c
        LEFT JOIN collectionItems ci ON ci.collectionID = c.collectionID
        GROUP BY c.collectionID, c.collectionName, c.parentCollectionID
        ORDER BY c.parentCollectionID IS NOT NULL, c.collectionName
        """,
        (),
    )
    return {"mode": "browse", "collections": col_rows, "recent_items": rows}


def cmd_search(
    conn: sqlite3.Connection,
    query: str,
    limit: int,
    year_from: int | None,
    year_to: int | None,
) -> dict[str, Any]:
    kw = f"%{query.lower()}%"
    year_filter = ""
    params: list[Any] = [kw, kw, kw, kw, kw]
    if year_from is not None:
        year_filter += (
            " AND (substr(date, 1, 4) GLOB '[0-9][0-9][0-9][0-9]' AND "
            "CAST(substr(date, 1, 4) AS INT) >= ?)"
        )
        params.append(year_from)
    if year_to is not None:
        year_filter += (
            " AND (substr(date, 1, 4) GLOB '[0-9][0-9][0-9][0-9]' AND "
            "CAST(substr(date, 1, 4) AS INT) <= ?)"
        )
        params.append(year_to)
    params.append(limit)
    rows = fetch_rows(
        conn,
        f"""
        SELECT *
        FROM (
          {BASE_SELECT}
        )
        WHERE
          lower(title) LIKE ?
          OR lower(abstractNote) LIKE ?
          OR lower(tags) LIKE ?
          OR lower(authors) LIKE ?
          OR lower(publicationTitle) LIKE ?
          {year_filter}
        ORDER BY dateModified DESC
        LIMIT ?
        """,
        tuple(params),
    )
    return {
        "mode": "search",
        "query": query,
        "year_from": year_from,
        "year_to": year_to,
        "results": rows,
    }


def clean_note(note: str, max_len: int = 1200) -> str:
    text = note.replace("\r", " ").replace("\n", " ").strip()
    if len(text) > max_len:
        return text[:max_len] + "...(truncated)"
    return text


def attachment_real_path(storage_root: Path, attachment_key: str, raw_path: str | None) -> str:
    if not raw_path:
        return ""
    if raw_path.startswith("storage:"):
        rel = raw_path.split("storage:", 1)[1]
        return str(storage_root / attachment_key / rel)
    return raw_path


def pick_target_item(
    conn: sqlite3.Connection,
    item_id: int | None,
    item_key: str | None,
    title: str | None,
) -> tuple[int | None, list[dict[str, Any]]]:
    if item_id is not None:
        rows = fetch_rows(conn, f"SELECT * FROM ({BASE_SELECT}) WHERE itemID = ? LIMIT 1", (item_id,))
        return (rows[0]["itemID"], rows) if rows else (None, [])
    if item_key:
        rows = fetch_rows(conn, f"SELECT * FROM ({BASE_SELECT}) WHERE itemKey = ? LIMIT 1", (item_key,))
        return (rows[0]["itemID"], rows) if rows else (None, [])
    if title:
        kw = f"%{title.lower()}%"
        candidates = fetch_rows(
            conn,
            f"""
            SELECT * FROM ({BASE_SELECT})
            WHERE lower(title) LIKE ?
            ORDER BY dateModified DESC
            LIMIT 5
            """,
            (kw,),
        )
        if len(candidates) == 1:
            return candidates[0]["itemID"], candidates
        return None, candidates
    raise ValueError("One of --item-id, --item-key, or --title is required for read.")


def cmd_read(
    conn: sqlite3.Connection,
    db_path: Path,
    item_id: int | None,
    item_key: str | None,
    title: str | None,
) -> dict[str, Any]:
    target_id, base_rows = pick_target_item(conn, item_id, item_key, title)
    if target_id is None:
        return {
            "mode": "read",
            "status": "ambiguous_or_not_found",
            "candidates": base_rows,
        }
    item = base_rows[0]
    notes = fetch_rows(
        conn,
        """
        SELECT note, title
        FROM itemNotes
        WHERE parentItemID = ?
        ORDER BY itemID DESC
        LIMIT 10
        """,
        (target_id,),
    )
    for n in notes:
        n["note"] = clean_note(n.get("note") or "")
    storage_root = db_path.parent / "storage"
    attachments = fetch_rows(
        conn,
        """
        SELECT
          ia.itemID AS attachmentItemID,
          i.key AS attachmentKey,
          ia.linkMode,
          ia.contentType,
          ia.path
        FROM itemAttachments ia
        JOIN items i ON i.itemID = ia.itemID
        WHERE ia.parentItemID = ?
        ORDER BY ia.itemID DESC
        """,
        (target_id,),
    )
    for a in attachments:
        a["resolvedPath"] = attachment_real_path(
            storage_root, a.get("attachmentKey") or "", a.get("path")
        )
    return {
        "mode": "read",
        "status": "ok",
        "item": item,
        "notes": notes,
        "attachments": attachments,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only Zotero DB helper")
    parser.add_argument("--db", help="Path to zotero.sqlite")
    sub = parser.add_subparsers(dest="command", required=True)

    browse = sub.add_parser("browse", help="List collections and recent items")
    browse.add_argument("--limit", type=int, default=20)

    search = sub.add_parser("search", help="Search papers by keyword")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--year-from", type=int, default=None)
    search.add_argument("--year-to", type=int, default=None)

    read = sub.add_parser("read", help="Read one target paper metadata/notes/attachments")
    read.add_argument("--item-id", type=int, default=None)
    read.add_argument("--item-key", default=None)
    read.add_argument("--title", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db_path = resolve_db_path(args.db)
    conn = connect_readonly(db_path)
    try:
        if args.command == "browse":
            result = cmd_browse(conn, args.limit)
        elif args.command == "search":
            result = cmd_search(conn, args.query, args.limit, args.year_from, args.year_to)
        elif args.command == "read":
            result = cmd_read(conn, db_path, args.item_id, args.item_key, args.title)
        else:
            raise ValueError(f"Unsupported command: {args.command}")
        result["db_path"] = str(db_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
