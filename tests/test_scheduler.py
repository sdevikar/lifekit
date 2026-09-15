"""Tests for lifekit.schedule.scheduler (Step 7: FSRS)."""

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.schedule.scheduler import get_card, review_exercise, due_exercises
from lifekit.db.schema import init_db
import sqlite3


@pytest.fixture
def db_path(tmp_path):
    p = str(tmp_path / "sched.db")
    init_db(p)
    c = sqlite3.connect(p)
    c.execute(
        """INSERT INTO exercises (book_id, chapter_title, title, purpose, steps, source_quote)
           VALUES ('b1','Ch1','Ex1','p','[]','q')"""
    )
    c.execute(
        """INSERT INTO exercises (book_id, chapter_title, title, purpose, steps, source_quote)
           VALUES ('b1','Ch1','Ex2','p','[]','q')"""
    )
    c.commit()
    c.close()
    return p


def test_get_card_creates(db_path):
    card = get_card(db_path, 1)
    assert card is not None
    # New card is due now (or very soon)
    assert card.due <= datetime.now(timezone.utc)


def test_get_card_persists(db_path):
    c1 = get_card(db_path, 1)
    # Review to change state
    review_exercise(db_path, 1, "good")
    c2 = get_card(db_path, 1)
    # Due date should have moved forward
    assert c2.due > c1.due


def test_review_good_pushes_due(db_path):
    before = get_card(db_path, 1).due
    review_exercise(db_path, 1, "good")
    after = get_card(db_path, 1).due
    assert after > before


def test_review_again_keeps_due_near(db_path):
    # Again should result in sooner due than Good
    review_exercise(db_path, 1, "again")
    due_again = get_card(db_path, 1).due
    # Reset by creating new DB state? Instead compare: Again due < Good due
    # (We can't easily reset, so just verify Again doesn't push far)
    # A new card reviewed with Good:
    review_exercise(db_path, 2, "good")
    due_good = get_card(db_path, 2).due
    # Good should push further than Again (for new cards, Good=10min, Again=1min)
    assert due_good > due_again


def test_review_logs_completion(db_path):
    review_exercise(db_path, 1, "good", notes="test")
    c = sqlite3.connect(db_path)
    n = c.execute("SELECT COUNT(*) FROM completions WHERE exercise_id=1").fetchone()[0]
    assert n == 1
    c.close()


def test_due_exercises(db_path):
    # Both new cards are due
    due = due_exercises(db_path, "b1")
    assert len(due) == 2
    # Review one with Good (pushes due to +10min, still due? No, 10min in future)
    # Actually new card + Good = due in 10 min, so not due NOW.
    # Let's check: due_exercises should return cards with due <= now.
    # After Good review, card 1 due is in future, so only card 2 should be due.
    review_exercise(db_path, 1, "good")
    due2 = due_exercises(db_path, "b1")
    assert len(due2) == 1
    assert due2[0]["id"] == 2
