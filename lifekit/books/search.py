"""Step 6: cross-book search (isolated by default, opt-in cross-book)."""

import sqlite3
from pathlib import Path

from lifekit.db.schema import init_db


def search_exercises(db_path: str | Path, query: str, book_ids: list[str] | None = None):
    """Search exercises by title/purpose.

    If book_ids given: return flat list filtered to those books.
    If None: return dict grouped by book_id (caller opts into cross-book).
    """
    db_path = str(db_path)
    init_db(db_path)
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row

    like = f"%{query}%"
    if book_ids is not None:
        placeholders = ",".join("?" for _ in book_ids)
        rows = c.execute(
            f"""SELECT id, book_id, title, chapter_title FROM exercises
                WHERE book_id IN ({placeholders})
                AND (title LIKE ? OR purpose LIKE ?)
                ORDER BY book_id, id""",
            (*book_ids, like, like),
        ).fetchall()
        c.close()
        return [dict(r) for r in rows]
    else:
        rows = c.execute(
            """SELECT id, book_id, title, chapter_title FROM exercises
               WHERE title LIKE ? OR purpose LIKE ?
               ORDER BY book_id, id""",
            (like, like),
        ).fetchall()
        c.close()
        grouped: dict[str, list[dict]] = {}
        for r in rows:
            d = dict(r)
            grouped.setdefault(d["book_id"], []).append(d)
        return grouped
