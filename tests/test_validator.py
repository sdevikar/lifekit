"""Tests for lifekit.validate (Step 4)."""

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.db.schema import init_db
from lifekit.validate.validator import validate_book, validate_exercise, should_flag_zero
from lifekit.validate.judge import sample_for_judge
from lifekit.extract.extractor import Exercise


def make_ex(quote="exact quote here", extra=None):
    return Exercise(
        title="Test Exercise",
        purpose="p",
        steps=["s1"],
        materials=[],
        source_quote=quote,
        chapter="Ch1",
    )


def test_verbatim_quote_passes():
    ex = make_ex(quote="exact quote here")
    result = validate_exercise(ex, "some text exact quote here more text")
    assert result["ok"] is True
    assert result["failures"] == []


def test_nonverbatim_quote_fails():
    ex = make_ex(quote="paraphrased quote not in text")
    result = validate_exercise(ex, "some text exact quote here more text")
    assert result["ok"] is False
    assert len(result["failures"]) == 1
    assert "source_quote" in result["failures"][0]


def test_extra_quotes_checked():
    ex = make_ex(quote="exact quote here")
    # Manually set extra_quotes (not in Exercise schema, so test via dict)
    # Actually extra_quotes is stored in DB, not Exercise. Skip detailed test;
    # validator checks a list passed separately.
    from lifekit.validate.validator import validate_quotes
    result = validate_quotes(
        "exact quote here",
        ["good extra", "bad extra not in text"],
        "text with exact quote here and good extra",
    )
    assert result["ok"] is False
    assert len(result["failures"]) == 1


def test_zero_flag_triggers_on_long_chapter():
    assert should_flag_zero(chapter_chars=10000, exercise_count=0) is True


def test_zero_flag_not_on_short_chapter():
    assert should_flag_zero(chapter_chars=3000, exercise_count=0) is False


def test_zero_flag_not_when_exercises_exist():
    assert should_flag_zero(chapter_chars=10000, exercise_count=3) is False


def test_judge_sampling_ten_percent():
    # 20 exercises → 2 sampled (10%)
    ids = list(range(20))
    sampled = sample_for_judge(ids, pct=0.10, seed=42)
    assert len(sampled) == 2
    # Deterministic
    assert sample_for_judge(ids, pct=0.10, seed=42) == sampled


def test_judge_sampling_min_one():
    ids = [1, 2, 3]
    sampled = sample_for_judge(ids, pct=0.10, seed=42)
    assert len(sampled) == 1


def _insert_exercise(db, book_id="b1", ch_title="Ch1", title="Test Exercise",
                     quote="exact quote here"):
    c = sqlite3.connect(db)
    c.execute(
        """INSERT INTO exercises
           (book_id, chapter_idx, chapter_title, title, purpose, steps, source_quote)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (book_id, 0, ch_title, title, "p", '["s1"]', quote),
    )
    c.commit()
    c.close()


def test_validate_book_without_chapters_skips_not_fails(tmp_path):
    """D2 regression: with no chapter text available, quote checks must be
    logged as skipped — never as failures."""
    db = str(tmp_path / "v.db")
    init_db(db)
    _insert_exercise(db, quote="a quote with no chapter text")

    result = validate_book(db, "b1", chapters=[])

    assert result["failed"] == 0
    assert result["passed"] == 0
    assert result["skipped"] == 1

    c = sqlite3.connect(db)
    rows = c.execute(
        "SELECT check_type, passed, detail FROM validation_log WHERE book_id = 'b1'"
    ).fetchall()
    c.close()
    assert len(rows) == 1
    check_type, passed, detail = rows[0]
    assert check_type == "verbatim_quote"
    assert passed is None  # skipped, not failed
    assert "skip" in detail.lower()


def test_validate_book_with_chapters_still_fails_nonverbatim(tmp_path):
    """Sanity: with chapter text present, real failures are still recorded."""
    db = str(tmp_path / "v.db")
    init_db(db)
    _insert_exercise(db, ch_title="Ch1", quote="paraphrased not in text")

    result = validate_book(db, "b1", chapters=[("Ch1", "some chapter text")])

    assert result["failed"] == 1
    assert result["skipped"] == 0
    c = sqlite3.connect(db)
    passed = c.execute(
        "SELECT passed FROM validation_log WHERE book_id = 'b1' AND check_type = 'verbatim_quote'"
    ).fetchone()[0]
    c.close()
    assert passed == 0


def test_migrate_old_validation_log_notnull_passed(tmp_path):
    """DBs created before the nullable-passed change migrate cleanly."""
    db = str(tmp_path / "old.db")
    c = sqlite3.connect(db)
    c.executescript(
        """CREATE TABLE validation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT NOT NULL,
            exercise_id INTEGER REFERENCES exercises(id),
            check_type TEXT NOT NULL,
            passed BOOLEAN NOT NULL,
            detail TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO validation_log (book_id, exercise_id, check_type, passed, detail)
            VALUES ('b1', NULL, 'zero_extraction', 0, 'old row');"""
    )
    c.commit()
    c.close()

    init_db(db)  # triggers migration

    c = sqlite3.connect(db)
    rows = c.execute(
        "SELECT check_type, passed, detail FROM validation_log"
    ).fetchall()
    assert rows == [("zero_extraction", 0, "old row")]
    # passed is now nullable
    c.execute(
        "INSERT INTO validation_log (book_id, check_type, passed, detail)"
        " VALUES ('b1', 'verbatim_quote', NULL, 'skipped')"
    )
    c.commit()
    c.close()
