"""Step 3: reduce/dedupe — merge chapter extractions into book-level tables."""

import json
import re
import sqlite3
from pathlib import Path

from lifekit.db.schema import init_db
from lifekit.extract.extractor import ChapterExtraction, Exercise


def normalize_title(title: str) -> str:
    """Deterministic title key: lowercase, strip punctuation, collapse whitespace."""
    t = title.lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def reduce_extractions(
    book_id: str,
    db_path: str | Path,
    extractions: list[ChapterExtraction],
) -> dict:
    """Flatten chapter extractions, deterministic-dedupe, persist.

    Returns summary dict with counts.
    Idempotent: re-running for the same book does not duplicate rows, and
    exercise ids are stable across re-runs (upsert on UNIQUE(book_id, title)).
    """
    db_path = str(db_path)
    # Ensure schema exists
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    # Clear per-run logs for this book (idempotency via replace).
    # NOTE: exercises are NOT deleted here. completions, fsrs_cards,
    # validation_log and dedupe_log reference exercises.id, so re-runs
    # upsert exercises in place (keyed on UNIQUE(book_id, title)) to keep
    # ids stable. Exercises that no longer appear in the extraction output
    # are left stale rather than deleted — deleting them would orphan
    # downstream user data.
    conn.execute("DELETE FROM dedupe_log WHERE book_id = ?", (book_id,))
    conn.execute("DELETE FROM key_ideas WHERE book_id = ?", (book_id,))

    # Flatten
    candidates: list[tuple[int, Exercise]] = []  # (chapter_idx, exercise)
    for idx, ext in enumerate(extractions):
        for ex in ext.exercises:
            candidates.append((idx, ex))
        for idea in ext.key_ideas:
            conn.execute(
                "INSERT OR IGNORE INTO key_ideas (book_id, chapter_idx, idea) VALUES (?, ?, ?)",
                (book_id, idx, idea),
            )

    # Dedupe by normalized title
    merged: dict[str, tuple[int, Exercise, list[str]]] = {}
    # key -> (chapter_idx, kept_exercise, extra_quotes)
    dedupe_entries = []

    for ch_idx, ex in candidates:
        key = normalize_title(ex.title)
        if key not in merged:
            merged[key] = (ch_idx, ex, [])
        else:
            kept_idx, kept_ex, extra_quotes = merged[key]
            # Keep the fuller record (more steps)
            if len(ex.steps) > len(kept_ex.steps):
                # Swap: new one is fuller, old becomes merged
                extra_quotes.append(kept_ex.source_quote)
                dedupe_entries.append((kept_ex, ex, "kept fuller record"))
                merged[key] = (ch_idx, ex, extra_quotes)
            else:
                extra_quotes.append(ex.source_quote)
                dedupe_entries.append((ex, kept_ex, "duplicate title"))
            # Update in place
            merged[key] = (merged[key][0], merged[key][1], extra_quotes)

    # Persist exercises via UPSERT keyed on UNIQUE(book_id, title), so ids
    # stay stable across re-runs (completions / fsrs_cards / validation_log /
    # dedupe_log all reference exercises.id).
    #
    # Why (book_id, title) is collision-free here: dedupe merges on
    # normalize_title(ex.title), and normalize_title is deterministic, so two
    # rows with identical raw titles always share one merge key and can never
    # become two distinct rows. ON CONFLICT is belt-and-braces: in the
    # impossible case it keeps the existing row's id and refreshes content.
    exercise_ids = {}
    for key, (ch_idx, ex, extra_quotes) in merged.items():
        # Dedupe extra_quotes, exclude the primary quote
        uniq_extra = []
        for q in extra_quotes:
            if q != ex.source_quote and q not in uniq_extra:
                uniq_extra.append(q)
        cur = conn.execute(
            """INSERT INTO exercises
               (book_id, chapter_idx, chapter_title, title, purpose, steps,
                materials, source_quote, extra_quotes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(book_id, title) DO UPDATE SET
                 chapter_idx=excluded.chapter_idx,
                 chapter_title=excluded.chapter_title,
                 purpose=excluded.purpose,
                 steps=excluded.steps,
                 materials=excluded.materials,
                 source_quote=excluded.source_quote,
                 extra_quotes=excluded.extra_quotes
               RETURNING id""",
            (
                book_id,
                ch_idx,
                ex.chapter,
                ex.title,
                ex.purpose,
                json.dumps(ex.steps),
                json.dumps(ex.materials),
                ex.source_quote,
                json.dumps(uniq_extra),
            ),
        )
        exercise_ids[key] = cur.fetchone()[0]

    # Persist dedupe log
    for merged_ex, kept_ex, reason in dedupe_entries:
        kept_key = normalize_title(kept_ex.title)
        conn.execute(
            """INSERT INTO dedupe_log
               (book_id, kept_exercise_id, merged_exercise_title,
                merged_source_quote, reason)
               VALUES (?, ?, ?, ?, ?)""",
            (
                book_id,
                exercise_ids[kept_key],
                merged_ex.title,
                merged_ex.source_quote,
                reason,
            ),
        )

    conn.commit()

    n_ex = conn.execute(
        "SELECT COUNT(*) FROM exercises WHERE book_id = ?", (book_id,)
    ).fetchone()[0]
    n_ideas = conn.execute(
        "SELECT COUNT(*) FROM key_ideas WHERE book_id = ?", (book_id,)
    ).fetchone()[0]
    n_merges = conn.execute(
        "SELECT COUNT(*) FROM dedupe_log WHERE book_id = ?", (book_id,)
    ).fetchone()[0]
    conn.close()

    return {
        "book_id": book_id,
        "exercises": n_ex,
        "key_ideas": n_ideas,
        "merges": n_merges,
        "candidates": len(candidates),
    }
