"""Step 4: deterministic validation — quote grounding, zero flags."""

import json
import sqlite3
import unicodedata
from pathlib import Path

from lifekit.db.schema import init_db
from lifekit.extract.extractor import Exercise

ZERO_FLAG_MIN_CHARS = 5000

# Deterministic character folding: the model quotes real book text but the
# PDF pipeline and the model disagree on typographic punctuation (curly vs
# straight quotes, em/en dashes, non-breaking spaces). NFKC + this table
# canonicalizes both sides before the strict substring check. Still no fuzzy
# or semantic matching — just a fixed, auditable character map.
_FOLD_TABLE = {
    "\u2018": "'", "\u2019": "'", "\u201a": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"',
    "\u2013": "-", "\u2014": "-", "\u2212": "-",
    "\u2026": "...", "\u00a0": " ", "\u2009": " ", "\u200a": " ",
}


def normalize_ws(s: str) -> str:
    """Canonicalize a string for strict quote grounding.

    Unicode NFKC + typographic-punctuation folding, then collapse every run
    of whitespace to a single space. See BACKLOG E1 / evals/step2-recall
    (10% exact vs 56% ws-normalized; char folding closes all but 2/144,
    both of which are PDF-extraction corruptions in the chapter text, not
    model hallucinations).
    """
    s = unicodedata.normalize("NFKC", s)
    for src, dst in _FOLD_TABLE.items():
        s = s.replace(src, dst)
    return " ".join(s.split())


def validate_quotes(source_quote: str, extra_quotes: list[str], chapter_text: str) -> dict:
    """Check all quotes are substrings of chapter_text (whitespace-insensitive)."""
    failures = []
    norm_text = normalize_ws(chapter_text)
    if normalize_ws(source_quote) not in norm_text:
        failures.append(f"source_quote not verbatim: {source_quote[:80]!r}")
    for q in extra_quotes or []:
        if normalize_ws(q) not in norm_text:
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
    """Run deterministic checks over all exercises; persist to validation_log.

    When chapter text is unavailable for an exercise (no --chapters passed to
    the CLI, or its chapter missing from the lookup), the quote check is
    logged as *skipped* (validation_log.passed NULL) — never as failed.
    Returns {"passed": n, "failed": n, "skipped": n, "zero_flags": [...]}.
    """
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
    skipped = 0
    full_text = "\n".join(text for _, text in chapters)  # for extra_quotes
    for ex_id, title, quote, extra_json, ch_title in rows:
        text = text_by_title.get(ch_title)
        extra = json.loads(extra_json) if extra_json else []
        if text is None:
            # No chapter text to check against — record a skip, not a failure.
            skipped += 1
            conn.execute(
                """INSERT INTO validation_log
                   (book_id, exercise_id, check_type, passed, detail)
                   VALUES (?, ?, ?, NULL, ?)""",
                (book_id, ex_id, "verbatim_quote",
                 f"skipped: no chapter text available for {ch_title!r}"),
            )
            continue
        # source_quote must ground in its own chapter; extra_quotes are
        # merged from deduped records that may come from other chapters,
        # so they ground against the full book text. Both strict.
        failures = []
        if normalize_ws(quote) not in normalize_ws(text):
            failures.append(f"source_quote not verbatim: {quote[:80]!r}")
        norm_full = normalize_ws(full_text)
        for q in extra:
            if normalize_ws(q) not in norm_full:
                failures.append(f"extra_quote not verbatim: {q[:80]!r}")
        ok = not failures
        if ok:
            passed += 1
        else:
            failed += 1
        conn.execute(
            """INSERT INTO validation_log
               (book_id, exercise_id, check_type, passed, detail)
               VALUES (?, ?, ?, ?, ?)""",
            (book_id, ex_id, "verbatim_quote", ok, "; ".join(failures)),
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
    return {"passed": passed, "failed": failed, "skipped": skipped, "zero_flags": flags}
