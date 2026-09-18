#!/usr/bin/env python3
"""Ingest the Designing Your Life eval output into a product LifeKit DB.

Builds ~/.lifekit/lifekit.db (override with LIFEKIT_DB):
  1. book row for Designing Your Life
  2. chapters copied from the eval splitter DB (full text, kept for validation)
  3. Step 3 reduce over the committed qwen eval extractions -> exercises/key_ideas
  4. Step 4 validate_book with whitespace-normalized quote grounding

Eval records carry section labels ("... (part N)") from eval-time chunking;
those are stripped so chapter_title matches the chapters table.
Idempotent: re-running upserts exercises in place (stable ids).
"""
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from lifekit.db.schema import init_db  # noqa: E402
from lifekit.extract.extractor import ChapterExtraction  # noqa: E402
from lifekit.reduce.reducer import reduce_extractions  # noqa: E402
from lifekit.validate.validator import validate_book  # noqa: E402

EVAL_DIR = REPO / "evals" / "step2-recall-qwen3.8-27b-q8_0"
EXTRACTIONS = EVAL_DIR / "extractions_qwen3.8-27b-q8_0.json"
EVAL_CHAPTERS_DB = Path.home() / "workspace" / "eval-step2-work" / "lifekit.db"
EVAL_CHAPTERS_BOOK_ID = "dda6f8e4c178faf3"

BOOK_ID = "dyl"
BOOK_TITLE = "Designing Your Life"
BOOK_AUTHOR = "Bill Burnett & Dave Evans"


def clean_chapter(label: str) -> str:
    return re.sub(r"\s*\(part \d+\)$", "", label).strip()


def main() -> int:
    db_path = os.environ.get("LIFEKIT_DB", str(Path.home() / ".lifekit" / "lifekit.db"))
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    init_db(db_path)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """INSERT INTO books (id, title, author, file_path)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(id) DO UPDATE SET title=excluded.title, author=excluded.author""",
        (BOOK_ID, BOOK_TITLE, BOOK_AUTHOR,
         "eval:step2-recall-qwen3.8-27b-q8_0 (qwen3.8:27b-q8_0)"),
    )
    conn.execute("DELETE FROM chapters WHERE book_id = ?", (BOOK_ID,))
    src = sqlite3.connect(EVAL_CHAPTERS_DB)
    chapters = src.execute(
        "SELECT idx, title, content, page_start, page_end FROM chapters "
        "WHERE book_id = ? ORDER BY idx",
        (EVAL_CHAPTERS_BOOK_ID,),
    ).fetchall()
    src.close()
    conn.executemany(
        "INSERT INTO chapters (book_id, idx, title, content, page_start, page_end) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [(BOOK_ID, idx, title, content, ps, pe)
         for idx, title, content, ps, pe in chapters],
    )
    conn.commit()
    conn.close()
    print(f"chapters copied: {len(chapters)}")

    raw = json.loads(EXTRACTIONS.read_text())
    extractions = []
    for k in sorted(raw.keys(), key=int):
        ext = ChapterExtraction.model_validate(raw[k])
        for ex in ext.exercises:
            ex.chapter = clean_chapter(ex.chapter)
        extractions.append(ext)

    summary = reduce_extractions(BOOK_ID, db_path, extractions)
    print(f"reduce: {summary['candidates']} raw -> "
          f"{summary['exercises']} exercises, {summary['key_ideas']} key_ideas, "
          f"{summary['merges']} merges")

    # validation_log is append-only in validate_book; clear this book's rows
    # so re-ingest is idempotent.
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM validation_log WHERE book_id = ?", (BOOK_ID,))
    conn.commit()
    conn.close()

    text_by_idx = {idx: (title, content) for idx, title, content, _, _ in chapters}
    chapters_for_val = [(t, c) for _, (t, c) in sorted(text_by_idx.items())]
    result = validate_book(db_path, BOOK_ID, chapters_for_val)
    print(f"validate: {result['passed']} passed, {result['failed']} failed, "
          f"{result['skipped']} skipped, zero_flags={result['zero_flags']}")
    print(f"db: {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
