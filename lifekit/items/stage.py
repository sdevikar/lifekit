"""Register the items stage in the ingest pipeline."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def run_items_stage(db_path, book_id, run_id=None) -> int:
    """Minimal stage: ensure items table exists; count body sections. Returns 0 items (placeholder)."""
    conn = sqlite3.connect(str(db_path))
    try:
        n = conn.execute(
            "SELECT COUNT(*) FROM sections WHERE book_id=? AND kind='body'", (book_id,)
        ).fetchone()[0]
        return n
    finally:
        conn.close()
EOF