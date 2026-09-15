"""Tests for lifekit.coach.tools (Step 5)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.coach.tools import (
    list_exercises, get_exercise, log_completion, next_exercise,
)
from lifekit.db.schema import init_db
import sqlite3


@pytest.fixture
def db_path(tmp_path):
    p = str(tmp_path / "coach.db")
    init_db(p)
    c = sqlite3.connect(p)
    # Seed 3 exercises
    for i, title in enumerate(["Alpha", "Beta", "Gamma"], start=1):
        c.execute(
            """INSERT INTO exercises
               (book_id, chapter_title, title, purpose, steps, source_quote)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("b1", "Ch1", title, f"purpose {i}", '["s1"]', "quote"),
        )
    c.commit()
    c.close()
    return p


def test_list_pagination(db_path):
    items = list_exercises(db_path, "b1", limit=2, offset=0)
    assert len(items) == 2
    assert items[0]["title"] == "Alpha"
    items2 = list_exercises(db_path, "b1", limit=2, offset=2)
    assert len(items2) == 1
    assert items2[0]["title"] == "Gamma"


def test_get_details(db_path):
    ex = get_exercise(db_path, 1)
    assert ex["title"] == "Alpha"
    assert ex["purpose"] == "purpose 1"
    assert ex["steps"] == ["s1"]
    assert "source_quote" in ex


def test_get_bad_id(db_path):
    assert get_exercise(db_path, 999) is None


def test_log_completion(db_path):
    result = log_completion(db_path, 1, notes="did it")
    assert result["ok"] is True
    c = sqlite3.connect(db_path)
    n = c.execute("SELECT COUNT(*) FROM completions WHERE exercise_id=1").fetchone()[0]
    assert n == 1
    c.close()


def test_next_first_incomplete(db_path):
    nxt = next_exercise(db_path, "b1")
    assert nxt["id"] == 1
    assert nxt["title"] == "Alpha"


def test_next_skips_completed(db_path):
    log_completion(db_path, 1)
    log_completion(db_path, 2)
    nxt = next_exercise(db_path, "b1")
    assert nxt["id"] == 3
    # Complete all
    log_completion(db_path, 3)
    assert next_exercise(db_path, "b1") is None
