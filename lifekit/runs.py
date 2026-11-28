"""Run records for pipeline stages."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def record_run(db_path, book_id, stage, status="ok", model=None, prompt_hash=None,
               params=None, counts=None) -> int:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.execute(
            """INSERT INTO runs (book_id, stage, model, prompt_hash, params, status, counts)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (book_id, stage, model, prompt_hash,
             json.dumps(params) if params is not None else None,
             status, json.dumps(counts) if counts is not None else None),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()