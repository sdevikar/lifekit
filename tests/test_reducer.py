"""Tests for lifekit.reduce.reducer (Step 3)."""

import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.extract.extractor import ChapterExtraction, Exercise
from lifekit.reduce.reducer import reduce_extractions, normalize_title
from lifekit.db.schema import init_db


def make_ex(title, chapter="Ch1", steps=None, quote="quote text here"):
    return Exercise(
        title=title,
        purpose="purpose",
        steps=steps or ["step one"],
        materials=[],
        source_quote=quote,
        chapter=chapter,
    )


def make_extraction(chapter_title, exercises, key_ideas=None):
    return ChapterExtraction(
        chapter_title=chapter_title,
        key_ideas=key_ideas or ["idea one"],
        exercises=exercises,
    )


@pytest.fixture
def db_path(tmp_path):
    p = str(tmp_path / "test.db")
    init_db(p)
    return p


def count(db_path, table):
    c = sqlite3.connect(db_path)
    n = c.execute(f"select count(*) from {table}").fetchone()[0]
    c.close()
    return n


def test_persists_exercises_and_key_ideas(db_path):
    ext = make_extraction("Ch1", [make_ex("Good Time Journal")], ["idea A", "idea B"])
    reduce_extractions("b1", db_path, [ext])
    assert count(db_path, "exercises") == 1
    assert count(db_path, "key_ideas") == 2
    c = sqlite3.connect(db_path)
    row = c.execute("select book_id, chapter_title, title from exercises").fetchone()
    assert row == ("b1", "Ch1", "Good Time Journal")
    c.close()


def test_exact_duplicates_merge(db_path):
    e1 = make_ex("Odyssey Plans", chapter="Ch5", steps=["a", "b"], quote="quote one")
    e2 = make_ex("Odyssey Plans", chapter="Ch6", steps=["a"], quote="quote two")
    reduce_extractions("b1", db_path, [
        make_extraction("Ch5", [e1]),
        make_extraction("Ch6", [e2]),
    ])
    assert count(db_path, "exercises") == 1
    c = sqlite3.connect(db_path)
    row = c.execute("select title, steps, source_quote, extra_quotes from exercises").fetchone()
    title, steps_json, quote, extra_json = row
    assert title == "Odyssey Plans"
    # Fuller record kept (2 steps)
    assert len(json.loads(steps_json)) == 2
    # Both quotes preserved
    assert "quote one" in quote or "quote one" in extra_json
    assert "quote two" in quote or "quote two" in extra_json
    # Audit log
    assert count(db_path, "dedupe_log") == 1
    c.close()


def test_near_duplicates_merge(db_path):
    e1 = make_ex("Good Time Journal")
    e2 = make_ex("good time journal!")  # case + punctuation variant
    e3 = make_ex("  Good   Time Journal  ")  # whitespace variant
    reduce_extractions("b1", db_path, [
        make_extraction("Ch1", [e1]),
        make_extraction("Ch2", [e2]),
        make_extraction("Ch3", [e3]),
    ])
    assert count(db_path, "exercises") == 1
    assert count(db_path, "dedupe_log") == 2


def test_distinct_exercises_kept_separate(db_path):
    reduce_extractions("b1", db_path, [
        make_extraction("Ch1", [make_ex("Exercise Alpha"), make_ex("Exercise Beta")]),
    ])
    assert count(db_path, "exercises") == 2
    assert count(db_path, "dedupe_log") == 0


def test_normalize_title():
    assert normalize_title("  Hello, World!  ") == "hello world"
    assert normalize_title("Good-Time_Journal") == "good time journal"


def test_idempotent_rerun(db_path):
    ext = make_extraction("Ch1", [make_ex("Good Time Journal")])
    reduce_extractions("b1", db_path, [ext])
    reduce_extractions("b1", db_path, [ext])
    assert count(db_path, "exercises") == 1
    assert count(db_path, "key_ideas") == 1


def test_rerun_keeps_exercise_ids_and_completions(db_path):
    """D1 regression: re-running reduce after user data exists must not
    raise IntegrityError and must not re-link completions to other exercises."""
    ext = make_extraction("Ch1", [make_ex("Good Time Journal"), make_ex("Odyssey Plans")])
    reduce_extractions("b1", db_path, [ext])

    c = sqlite3.connect(db_path)
    c.execute("PRAGMA foreign_keys = ON")
    ids_before = dict(
        c.execute("SELECT title, id FROM exercises WHERE book_id = 'b1'").fetchall()
    )
    # Log a completion against the first exercise (FK enforced).
    c.execute(
        "INSERT INTO completions (exercise_id, notes) VALUES (?, ?)",
        (ids_before["Good Time Journal"], "did it"),
    )
    # Log an FSRS review against the second exercise.
    c.execute(
        "INSERT INTO fsrs_cards (exercise_id, card_json) VALUES (?, ?)",
        (ids_before["Odyssey Plans"], '{"state": "learning"}'),
    )
    c.commit()
    c.close()

    # Re-run with identical extractions: must not raise.
    reduce_extractions("b1", db_path, [ext])

    c = sqlite3.connect(db_path)
    ids_after = dict(
        c.execute("SELECT title, id FROM exercises WHERE book_id = 'b1'").fetchall()
    )
    # Same ids for the same titles.
    assert ids_after == ids_before

    # Completion still points at the same exercise content.
    comp = c.execute("SELECT exercise_id, notes FROM completions").fetchall()
    assert len(comp) == 1
    assert comp[0][0] == ids_before["Good Time Journal"]
    title = c.execute(
        "SELECT title FROM exercises WHERE id = ?", (comp[0][0],)
    ).fetchone()[0]
    assert title == "Good Time Journal"

    # FSRS card still attached to its exercise.
    card = c.execute("SELECT exercise_id FROM fsrs_cards").fetchone()[0]
    assert card == ids_before["Odyssey Plans"]
    c.close()
