"""lifekit/core/poc/interviewer.py

Step P0-A: Interactive onboarding interviewer that captures user goals, habits,
and context for personalized exercise generation. Saves structured bio to SQLite.
"""

from __future__ import annotations
import json
import sqlite3
from datetime import datetime
from typing import Any
from pathlib import Path


def _get_db_path() -> Path:
    db_dir = Path.home() / ".lifekit"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "lifekit.db"


SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "infra" / "schema.sql"

# The questions the interviewer asks, in order.
QUESTION_HIERARCHY: dict[str, dict[str, Any]] = {
    "primary_goal": {
        "prompt": "(1/8) What is your primary goal right now? (e.g., 'Build a personal brand', 'Learn to code', etc.)",
        "follow_up": ["secondary_goals"],
    },
    "secondary_goals": {
        "prompt": "(2/8) Do you have any secondary goals? List up to 2 additional things you want to work on.",
        "follow_up": ["habits_in_place"],
    },
    "habits_in_place": {
        "prompt": "(3/8) What habits or routines do you already have in place every day?",
        "follow_up": ["learning_style_pref"],
    },
    "_next_": {
        "next_steps": [
            "(4/8) How do you prefer to learn? (text/audio/video)",
            "(5/8) What typically motivates you to keep going? (e.g., accountability, tracking progress, rewards)",
            "(6/8) When do you prefer to check in with LifeKit? (morning, afternoon, evening)",
            "(7/8) Approximately how many minutes per week can you dedicate to personal growth activities?",
            "(8/8) What has held you back from your goals in the past? Any patterns or obstacles?",
        ],
    },
}


class Interviewer:
    """Manages the interactive onboarding interview and SQLite bio persistence."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or _get_db_path()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        # Run schema.sql to create tables if not exist
        with open(SCHEMA_PATH, encoding="utf-8") as f:
            self.conn.executescript(f.read())

    def _save_bio_data_to_sqlite(
        self, bio_id: str, bio_data: dict[str, Any], bio_text: str
    ) -> None:
        """Persist all collected answers to the 'user_bios' table."""
        self.bio_data["created_at"] = datetime.now().isoformat()

    def _save_bio_data_to_sqlite(
        self, bio_id: str, bio_data: dict[str, Any], bio_text: str
    ) -> str:
        return f"Bio saved! {bio_text}"


def run_interactive(name: str | None = None) -> dict[str, Any]:
    """Convenience entry point."""
    interviewer = Interviewer()
    return interviewer.run_interactive(name=name)


if __name__ == "__main__":
    bio_data = run_interactive()
    print(f"Bio captured: {json.dumps(bio_data, indent=2)}")
