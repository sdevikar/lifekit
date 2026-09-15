"""Step 4: deterministic validation — verbatim quote grounding, zero flags."""

import json
import sqlite3
from pathlib import Path

from lifekit.db.schema import init_db
from lifekit.extract.extractor import Exercise

ZERO_FLAG_MIN_CHARS = 5000


def validate_quotes(source_quote: str, extra_quotes: list[str], chapter_text: str) -> dict:
    """Check all quotes are exact substrings of chapter_text."""
    failures = []
    if source_quote not in chapter_text:
        failures.append(f"source_quote not verbatim: {source_quote[:80]!r}")
    for q in extra_quotes or []:
        if q not in chapter_text:
            failures.append(f"extra_quote not verbatim: {q[:80]!r}")
    return {"ok": not failures, "failures": failures}


def validate_exercise(exercise: Exercise, chapter_text: str) -> dict:
    """Validate a single exercise's grounding."""
    # Exercise schema has source_quote; extra_quotes live in DB.
    return validate_quotes(exercise.source_quote, [], chapter_text)


def should_flag_zero(chapter_chars: int, exercise_count: int) -> bool:
    """Flag chapters with suspiciously zero extractions."""
    return exercise_count == 0 and chapter_chars >= ZERO_FLAG_MIN_CHARS


def validate_book(
    db_path: str | Path,
    book_id: str,
    chapters: list[tuple[str, str]],  # [(title, text)]
) -> dict:
    """Run deterministic checks over all exercises; persist to validation_log."""
    db_path = str(db_path)
    init_db(db_path)
    conn = sqlite3.connect(db_path)

    # Map chapter title -> text
    text_by_title = {t: txt for t, txt in chapters}

    rows = conn.execute(
        "SELECT id, title, source_quote, extra_quotes, chapter_title FROM exercises WHERE book_id = ?",
        (book_id,),
    ).fetchall()

    passed = 0
    failed = 0
    for ex_id, title, quote, extra_json, ch_title in rows:
        text = text_by_title.get(ch_title, "")
        extra = json.loads(extra_json) if extra_json else []
        result = validate_quotes(quote, extra, text)
        ok = result["ok"]
        if ok:
            passed += 1
        else:
            failed += 1
        conn.execute(
            """INSERT INTO validation_log
               (book_id, exercise_id, check_type, passed, detail)
               VALUES (?, ?, ?, ?, ?)""",
            (book_id, ex_id, "verbatim_quote", ok, "; ".join(result["failures"])),
        )

    # Zero-extraction flags (per chapter)
    flags = []
    for ch_title, text in chapters:
        n = conn.execute(
            "SELECT COUNT(*) FROM exercises WHERE book_id = ? AND chapter_title = ?",
            (book_id, ch_title),
        ).fetchone()[0]
        if should_flag_zero(len(text), n):
            flags.append(ch_title)
            conn.execute(
                """INSERT INTO validation_log
                   (book_id, exercise_id, check_type, passed, detail)
                   VALUES (?, ?, ?, ?, ?)""",
                (book_id, None, "zero_extraction", False,
                 f"chapter {ch_title!r} ({len(text)} chars) has 0 exercises"),
            )

    conn.commit()
    conn.close()
    return {"passed": passed, "failed": failed, "zero_flags": flags}
