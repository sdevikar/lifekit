"""LifeKit MCP server — real MCP (stdio) exposing the Step 5 coach tools.

Usage:
    python -m lifekit.mcp.server        # stdio transport for an MCP client
    LIFEKIT_DB=/path/to.db python -m lifekit.mcp.server

Tools: list_exercises, search_exercises, get_exercise, complete_exercise,
due_exercises, list_key_ideas, book_progress.
"""
import json
import os
import sqlite3
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from lifekit.coach.tools import (
    get_exercise as coach_get_exercise,
    list_exercises as coach_list_exercises,
    search_exercises as coach_search_exercises,
)
from lifekit.schedule.scheduler import (
    due_exercises as sched_due_exercises,
    review_exercise as sched_review_exercise,
)

DB_PATH = os.environ.get("LIFEKIT_DB", str(Path.home() / ".lifekit" / "lifekit.db"))

mcp = FastMCP("lifekit")


def _done_ids() -> set[int]:
    c = sqlite3.connect(DB_PATH)
    ids = {r[0] for r in c.execute("SELECT DISTINCT exercise_id FROM completions")}
    c.close()
    return ids


@mcp.tool()
def list_exercises(book_id: str = "dyl", chapter: str | None = None,
                   limit: int = 20, offset: int = 0) -> list[dict]:
    """List exercises in a book, optionally filtered by chapter title
    (substring match). Each entry has id, title, chapter_title, done."""
    done = _done_ids()
    if chapter:
        c = sqlite3.connect(DB_PATH)
        c.row_factory = sqlite3.Row
        rows = c.execute(
            """SELECT id, title, chapter_title FROM exercises
               WHERE book_id = ? AND chapter_title LIKE ?
               ORDER BY chapter_idx, id LIMIT ? OFFSET ?""",
            (book_id, f"%{chapter}%", limit, offset),
        ).fetchall()
        c.close()
        return [dict(r) | {"done": r["id"] in done} for r in rows]
    return [dict(e) | {"done": e["id"] in done}
            for e in coach_list_exercises(DB_PATH, book_id, limit, offset)]


@mcp.tool()
def search_exercises(query: str, book_id: str = "dyl") -> list[dict]:
    """Find exercises by natural-language query, e.g.
    "i want to do the mindmapping exercise". Returns id/title/chapter/done."""
    return coach_search_exercises(DB_PATH, query, book_id)


@mcp.tool()
def get_exercise(exercise_id: int) -> dict:
    """Full details of one exercise: purpose, steps, materials, source quote."""
    ex = coach_get_exercise(DB_PATH, exercise_id)
    if ex is None:
        return {"ok": False, "error": "exercise not found"}
    return {"ok": True, "exercise": ex}


@mcp.tool()
def complete_exercise(exercise_id: int, rating: str = "good",
                      notes: str | None = None) -> dict:
    """Log a completed exercise. Rating: again | hard | good | easy.
    Schedules the next FSRS review. Returns the next due date."""
    return sched_review_exercise(DB_PATH, exercise_id, rating=rating, notes=notes)


@mcp.tool()
def due_exercises(book_id: str = "dyl", limit: int = 10) -> list[dict]:
    """Exercises due for review now per the FSRS schedule, ordered by due date."""
    return sched_due_exercises(DB_PATH, book_id, limit)


@mcp.tool()
def list_key_ideas(book_id: str = "dyl", chapter: str | None = None,
                   limit: int = 50) -> list[str]:
    """Key ideas ("lessons") from the book, optionally filtered by chapter
    title (substring match)."""
    c = sqlite3.connect(DB_PATH)
    if chapter:
        rows = c.execute(
            """SELECT k.idea FROM key_ideas k JOIN chapters c
               ON c.book_id = k.book_id AND c.idx = k.chapter_idx
               WHERE k.book_id = ? AND c.title LIKE ? ORDER BY k.id LIMIT ?""",
            (book_id, f"%{chapter}%", limit),
        ).fetchall()
    else:
        rows = c.execute(
            "SELECT idea FROM key_ideas WHERE book_id = ? ORDER BY id LIMIT ?",
            (book_id, limit),
        ).fetchall()
    c.close()
    return [r[0] for r in rows]


@mcp.tool()
def book_progress(book_id: str = "dyl") -> dict:
    """Overall progress: total exercises, completed count, recent completions."""
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    total = c.execute(
        "SELECT COUNT(*) FROM exercises WHERE book_id = ?", (book_id,)).fetchone()[0]
    done = c.execute(
        """SELECT COUNT(DISTINCT c.exercise_id) FROM completions c
           JOIN exercises e ON e.id = c.exercise_id WHERE e.book_id = ?""",
        (book_id,)).fetchone()[0]
    recent = c.execute(
        """SELECT e.title, c.completed_at FROM completions c
           JOIN exercises e ON e.id = c.exercise_id
           WHERE e.book_id = ? ORDER BY c.completed_at DESC LIMIT 5""",
        (book_id,)).fetchall()
    c.close()
    return {"book_id": book_id, "total": total, "completed": done,
            "recent": [dict(r) for r in recent]}


if __name__ == "__main__":
    mcp.run()
