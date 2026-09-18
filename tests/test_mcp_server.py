"""Tests for lifekit.mcp.server — the Step 5 coach tools over real MCP (H1)."""

import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lifekit.mcp.server as srv
from lifekit.db.schema import init_db


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    p = str(tmp_path / "mcp.db")
    init_db(p)
    c = sqlite3.connect(p)
    c.execute(
        "INSERT INTO books (id, title, author, file_path) VALUES (?,?,?,?)",
        ("dyl", "Designing Your Life", "Burnett & Evans", "test"),
    )
    for i, title in enumerate(["Mind Mapping", "Good Time Journal"], start=1):
        c.execute(
            """INSERT INTO exercises
               (book_id, chapter_idx, chapter_title, title, purpose, steps,
                materials, source_quote, extra_quotes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("dyl", 0, "Ch1", title, f"purpose {i}", '["s1","s2"]',
             "[]", "a real quote here", "[]"),
        )
    c.execute(
        "INSERT INTO chapters (book_id, idx, title, content, page_start, page_end) "
        "VALUES (?,?,?,?,?,?)",
        ("dyl", 0, "Ch1", "content", 1, 2),
    )
    c.execute(
        "INSERT INTO key_ideas (book_id, chapter_idx, idea) VALUES (?,?,?)",
        ("dyl", 0, "an important idea"),
    )
    c.commit()
    c.close()
    monkeypatch.setattr(srv, "DB_PATH", p)
    return p


def test_list_exercises(db_path):
    items = srv.list_exercises.fn("dyl") if hasattr(srv.list_exercises, "fn") \
        else srv.list_exercises("dyl")
    assert len(items) == 2
    assert items[0]["title"] == "Mind Mapping"
    assert items[0]["done"] is False


def test_search_natural_prompt(db_path):
    call = srv.search_exercises.fn if hasattr(srv.search_exercises, "fn") \
        else srv.search_exercises
    hits = call("i want to do the mindmapping exercise", "dyl")
    assert hits and hits[0]["title"] == "Mind Mapping"


def test_get_exercise(db_path):
    call = srv.get_exercise.fn if hasattr(srv.get_exercise, "fn") else srv.get_exercise
    res = call(1)
    assert res["ok"] is True
    assert res["exercise"]["steps"] == ["s1", "s2"]
    bad = call(999)
    assert bad["ok"] is False


def test_complete_and_progress(db_path):
    call_c = srv.complete_exercise.fn if hasattr(srv.complete_exercise, "fn") \
        else srv.complete_exercise
    call_p = srv.book_progress.fn if hasattr(srv.book_progress, "fn") \
        else srv.book_progress
    before = call_p("dyl")
    assert before["completed"] == 0
    res = call_c(1, "good", "test notes")
    assert res["ok"] is True and "due" in res
    after = call_p("dyl")
    assert after["completed"] == 1
    assert after["recent"][0]["title"] == "Mind Mapping"


def test_due_and_key_ideas(db_path):
    call_d = srv.due_exercises.fn if hasattr(srv.due_exercises, "fn") \
        else srv.due_exercises
    call_k = srv.list_key_ideas.fn if hasattr(srv.list_key_ideas, "fn") \
        else srv.list_key_ideas
    due = call_d("dyl", 10)
    assert len(due) == 2  # fresh cards are due immediately
    assert call_k("dyl") == ["an important idea"]
    assert call_k("dyl", chapter="Nope") == []
