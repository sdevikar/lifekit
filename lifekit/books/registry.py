"""Step 6: book registry."""

import hashlib
import sqlite3
from pathlib import Path

from lifekit.db.schema import init_db


def book_id_for(file_path: str) -> str:
    """Stable ID: sha256(file_path)[:16] (matches Step 1 default)."""
    return hashlib.sha256(str(file_path).encode()).hexdigest()[:16]


def register_book(db_path: str | Path, file_path: str, title: str = None, author: str = None) -> str:
    """Register a book; idempotent. Returns book_id."""
    db_path = str(db_path)
    init_db(db_path)
    bid = book_id_for(file_path)
    if not title:
        title = Path(file_path).stem
    c = sqlite3.connect(db_path)
    c.execute(
        """INSERT OR IGNORE INTO books (id, title, author, file_path)
           VALUES (?, ?, ?, ?)""",
        (bid, title, author, str(file_path)),
    )
    c.commit()
    c.close()
    return bid
