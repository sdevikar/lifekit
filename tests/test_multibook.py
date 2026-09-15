"""Tests for lifekit.books (Step 6: multi-book)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.books.registry import register_book
from lifekit.books.search import search_exercises
from lifekit.coach.tools import list_exercises
from lifekit.db.schema import init_db
import sqlite3


@pytest.fixture
def db_path(tmp_path):
    p = str(tmp_path / "multi.db")
    init_db(p)
    c = sqlite3.connect(p)
    # Two books with exercises
    for book, title in [("aaa", "Alpha Exercise"), ("bbb", "Beta Exercise")]:
        c.execute(
            "INSERT INTO books (id, title, file_path) VALUES (?, ?, ?)",
            (book, f"Book {book}", f"/tmp/{book}.pdf"),
        )
        c.execute(
            """INSERT INTO exercises (book_id, chapter_title, title, purpose, steps, source_quote)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (book, "Ch1", title, "purpose", '["s1"]', "quote"),
        )
    c.commit()
    c.close()
    return p


def test_register_stable_id(tmp_path):
    p = str(tmp_path / "reg.db")
    init_db(p)
    pdf = "/tmp/mybook.pdf"
    id1 = register_book(p, pdf, title="My Book", author="Author")
    id2 = register_book(p, pdf, title="My Book", author="Author")
    assert id1 == id2
    # No duplicate
    c = sqlite3.connect(p)
    n = c.execute("SELECT COUNT(*) FROM books WHERE id=?", (id1,)).fetchone()[0]
    assert n == 1
    c.close()


def test_list_isolates_by_book(db_path):
    a_items = list_exercises(db_path, "aaa")
    b_items = list_exercises(db_path, "bbb")
    assert len(a_items) == 1 and a_items[0]["title"] == "Alpha Exercise"
    assert len(b_items) == 1 and b_items[0]["title"] == "Beta Exercise"


def test_search_filters_by_book_ids(db_path):
    results = search_exercises(db_path, "Exercise", book_ids=["aaa"])
    assert len(results) == 1
    assert results[0]["book_id"] == "aaa"


def test_search_groups_by_book(db_path):
    grouped = search_exercises(db_path, "Exercise", book_ids=None)
    # Returns dict: book_id -> list
    assert isinstance(grouped, dict)
    assert set(grouped.keys()) == {"aaa", "bbb"}
    assert grouped["aaa"][0]["title"] == "Alpha Exercise"
