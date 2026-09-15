"""Test that the split CLI creates nested DB parent directories."""

import subprocess
import sys
from pathlib import Path


def test_split_cli_creates_nested_db_parent(tmp_path):
    """python -m lifekit.store.split with --db-path in a nonexistent nested
    dir must create the parents instead of failing with OperationalError."""
    # Use --no-persist? No — we need persistence to exercise the mkdir.
    # Use a tiny PDF? Instead, assert the mkdir happens before any PDF work
    # by pointing at a nonexistent PDF: the DB init (and mkdir) runs first.
    nested_db = tmp_path / "a" / "b" / "c" / "test.db"
    repo = Path(__file__).resolve().parent.parent
    proc = subprocess.run(
        [sys.executable, "-m", "lifekit.store.split",
         "--pdf", str(tmp_path / "nonexistent.pdf"),
         "--db-path", str(nested_db)],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # PDF is missing -> FileNotFoundError exit, but the DB parent must exist
    # (mkdir runs before split_chapters).
    assert nested_db.parent.is_dir(), (
        f"nested DB parent was not created; stderr={proc.stderr[:300]}"
    )
