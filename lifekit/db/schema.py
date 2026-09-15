"""Database schema initialization — all CREATE TABLE IF NOT EXISTS + FTS5 triggers.

Usage:
    from lifekit.db import init_db, get_connection

    db = init_db(db_path)          # creates tables if missing (idempotent)
    conn = get_connection(db_path)  # returns live sqlite3 connection
"""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    file_path TEXT NOT NULL UNIQUE,
    chunk_count INTEGER DEFAULT 0,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS book_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL REFERENCES books(id),
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    UNIQUE(book_id, chunk_index)
);

CREATE VIRTUAL TABLE IF NOT EXISTS book_chunks_fts USING fts5(
    content,
    content_rowid=id
);

CREATE TRIGGER IF NOT EXISTS book_chunks_ai AFTER INSERT ON book_chunks BEGIN
    INSERT INTO book_chunks_fts(rowid, content) VALUES (new.id, new.content);
END;

CREATE TRIGGER IF NOT EXISTS book_chunks_au AFTER UPDATE ON book_chunks BEGIN
    INSERT INTO book_chunks_fts(book_chunks_fts, rowid, content) VALUES('delete', old.id);
    INSERT INTO book_chunks_fts(rowid, content) VALUES (new.id, new.content);
END;

CREATE TRIGGER IF NOT EXISTS book_chunks_ad AFTER DELETE ON book_chunks BEGIN
    INSERT INTO book_chunks_fts(book_chunks_fts, rowid, content) VALUES('delete', old.id);
END;

CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL,
    idx INTEGER NOT NULL,
    title TEXT NOT NULL,
    page_start INTEGER NOT NULL,
    page_end INTEGER NOT NULL,
    content TEXT NOT NULL,
    UNIQUE(book_id, idx)
);

CREATE TABLE IF NOT EXISTS plans (
    id TEXT PRIMARY KEY,
    book_id TEXT NOT NULL REFERENCES books(id),
    user_intent TEXT NOT NULL,
    teaching_method TEXT NOT NULL DEFAULT 'socratic'
        CHECK(teaching_method IN ('auto', 'socratic', 'feynman', 'analogical', 'spaced_recall')),
    duration_weeks INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id TEXT NOT NULL REFERENCES plans(id),
    day_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    estimated_minutes INTEGER,
    exercise_type TEXT,
    context_source TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'complete', 'skipped')),
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks(id),
    notes TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def init_db(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Create database and apply schema. Idempotent — safe to call multiple times."""
    if db_path is None:
        db_dir = Path.home() / ".lifekit"
        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = db_dir / "lifekit.db"
    else:
        db_path = Path(db_path)
    
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


# Module-level singleton for convenience
_db_conn = None

def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Return a live connection, initializing if needed."""
    global _db_conn
    if _db_conn is None:
        _db_conn = init_db(db_path)
    return _db_conn


if __name__ == "__main__":
    db = init_db()
    print(f"Database initialized at {db_path}")
    
    # Verify tables
    cur = db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    for row in cur.fetchall():
        print(f"  Table: {row[0]}")
