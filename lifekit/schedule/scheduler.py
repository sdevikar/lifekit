"""Step 7: FSRS scheduling over exercise completions.

Uses the open-source `fsrs` PyPI package — no custom scheduling math.
Card state persisted as JSON via Card.to_dict()/from_dict().
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fsrs import Scheduler, Card, Rating

from lifekit.db.schema import init_db

_scheduler = Scheduler()

RATING_MAP = {
    "again": Rating.Again,
    "hard": Rating.Hard,
    "good": Rating.Good,
    "easy": Rating.Easy,
}


def _conn(db_path):
    db_path = str(db_path)
    init_db(db_path)
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    return c


def get_card(db_path: str | Path, exercise_id: int) -> Card:
    """Load FSRS card for exercise, creating if missing."""
    c = _conn(db_path)
    row = c.execute(
        "SELECT card_json FROM fsrs_cards WHERE exercise_id = ?", (exercise_id,)
    ).fetchone()
    if row:
        card = Card.from_dict(json.loads(row["card_json"]))
    else:
        card = Card()
        c.execute(
            "INSERT INTO fsrs_cards (exercise_id, card_json) VALUES (?, ?)",
            (exercise_id, json.dumps(card.to_dict())),
        )
        c.commit()
    c.close()
    return card


def review_exercise(
    db_path: str | Path, exercise_id: int, rating: str = "good", notes: str = None
) -> dict:
    """Apply FSRS review; update card; log completion. Returns {ok, due}."""
    if rating not in RATING_MAP:
        return {"ok": False, "error": f"rating must be one of {list(RATING_MAP)}"}
    card = get_card(db_path, exercise_id)
    new_card, _log = _scheduler.review_card(card, RATING_MAP[rating])

    c = _conn(db_path)
    c.execute(
        "UPDATE fsrs_cards SET card_json = ? WHERE exercise_id = ?",
        (json.dumps(new_card.to_dict()), exercise_id),
    )
    c.execute(
        "INSERT INTO completions (exercise_id, notes) VALUES (?, ?)",
        (exercise_id, notes or f"fsrs rating={rating}"),
    )
    c.commit()
    c.close()
    return {"ok": True, "due": new_card.due.isoformat()}


def due_exercises(db_path: str | Path, book_id: str, limit: int = 10) -> list[dict]:
    """Exercises with FSRS due <= now, ordered by due."""
    # Ensure cards exist for all exercises in the book
    c = _conn(db_path)
    ex_ids = c.execute(
        "SELECT id FROM exercises WHERE book_id = ?", (book_id,)
    ).fetchall()
    c.close()
    for r in ex_ids:
        get_card(db_path, r["id"])

    c = _conn(db_path)
    now = datetime.now(timezone.utc).isoformat()
    rows = c.execute(
        """SELECT e.id, e.title, e.chapter_title, f.card_json FROM exercises e
           JOIN fsrs_cards f ON f.exercise_id = e.id
           WHERE e.book_id = ? ORDER BY e.id""",
        (book_id,),
    ).fetchall()
    c.close()
    due = []
    for r in rows:
        card = Card.from_dict(json.loads(r["card_json"]))
        # Card.due may be naive or aware; compare carefully
        due_dt = card.due
        if due_dt.tzinfo is None:
            due_dt = due_dt.replace(tzinfo=timezone.utc)
        if due_dt <= datetime.now(timezone.utc):
            due.append({"id": r["id"], "title": r["title"],
                        "chapter_title": r["chapter_title"],
                        "due": card.due.isoformat()})
    due.sort(key=lambda x: x["due"])
    return due[:limit]
