"""Step 5: coach tools — list/get/log/next over the exercise library."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from lifekit.db.schema import init_db


def _conn(db_path):
    db_path = str(db_path)
    init_db(db_path)
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    return c


def list_exercises(db_path, book_id, limit=20, offset=0) -> list[dict]:
    """Paginated exercise summaries."""
    c = _conn(db_path)
    rows = c.execute(
        """SELECT id, title, chapter_title FROM exercises
           WHERE book_id = ? ORDER BY id LIMIT ? OFFSET ?""",
        (book_id, limit, offset),
    ).fetchall()
    c.close()
    return [dict(r) for r in rows]


def get_exercise(db_path, exercise_id) -> dict | None:
    """Full exercise details, or None if not found."""
    c = _conn(db_path)
    r = c.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,)).fetchone()
    c.close()
    if not r:
        return None
    d = dict(r)
    d["steps"] = json.loads(d["steps"])
    d["materials"] = json.loads(d["materials"])
    d["extra_quotes"] = json.loads(d["extra_quotes"])
    return d


def log_completion(db_path, exercise_id, notes=None) -> dict:
    """Record a completion. Returns {ok, completion_id}."""
    c = _conn(db_path)
    # Verify exercise exists
    if not c.execute("SELECT 1 FROM exercises WHERE id = ?", (exercise_id,)).fetchone():
        c.close()
        return {"ok": False, "error": "exercise not found"}
    cur = c.execute(
        "INSERT INTO completions (exercise_id, notes) VALUES (?, ?)",
        (exercise_id, notes),
    )
    cid = cur.lastrowid
    c.commit()
    c.close()
    return {"ok": True, "completion_id": cid}


def next_exercise(db_path, book_id) -> dict | None:
    """First incomplete exercise by id (placeholder; FSRS is Step 7)."""
    c = _conn(db_path)
    r = c.execute(
        """SELECT e.id, e.title, e.chapter_title FROM exercises e
           WHERE e.book_id = ?
           AND NOT EXISTS (
               SELECT 1 FROM completions c WHERE c.exercise_id = e.id
           )
           ORDER BY e.id LIMIT 1""",
        (book_id,),
    ).fetchone()
    c.close()
    return dict(r) if r else None


_SEARCH_STOPWORDS = frozenset(
    "i want to do the a an me my please show start begin with exercise "
    "practice give".split()
)


def search_exercises(db_path, query: str, book_id: str = "dyl", limit: int = 10) -> list[dict]:
    """Keyword search over exercise titles.

    Handles natural prompts like "i want to do the mindmapping exercise":
    stopwords are dropped and spaces ignored ("mindmapping" matches
    "Mind Mapping").
    """
    words = [
        w for w in "".join(ch if ch.isalnum() else " " for ch in query.lower()).split()
        if w not in _SEARCH_STOPWORDS and len(w) > 2
    ]
    if not words:
        return []
    c = _conn(db_path)
    rows = c.execute(
        "SELECT id, title, chapter_title FROM exercises WHERE book_id = ?",
        (book_id,),
    ).fetchall()
    done = {r[0] for r in c.execute("SELECT DISTINCT exercise_id FROM completions")}
    c.close()
    scored = []
    for r in rows:
        flat = "".join(r["title"].lower().split())
        hits = sum(1 for w in words if w in flat)
        if hits:
            scored.append((hits, dict(r) | {"done": r["id"] in done}))
    scored.sort(key=lambda x: (-x[0], x[1]["title"]))
    return [ex for _, ex in scored[:limit]]
