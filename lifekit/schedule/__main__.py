"""CLI: python -m lifekit.schedule --db-path DB <review|due> ..."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lifekit.schedule.scheduler import review_exercise, due_exercises


def main():
    ap = argparse.ArgumentParser(description="FSRS scheduling")
    ap.add_argument("--db-path", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_rev = sub.add_parser("review")
    p_rev.add_argument("--exercise-id", type=int, required=True)
    p_rev.add_argument("--rating", default="good",
                       choices=["again", "hard", "good", "easy"])
    p_rev.add_argument("--notes", default=None)

    p_due = sub.add_parser("due")
    p_due.add_argument("--book-id", required=True)
    p_due.add_argument("--limit", type=int, default=10)

    args = ap.parse_args()

    if args.cmd == "review":
        print(json.dumps(review_exercise(
            args.db_path, args.exercise_id, args.rating, args.notes), indent=2))
    elif args.cmd == "due":
        items = due_exercises(args.db_path, args.book_id, args.limit)
        for it in items:
            print(f"{it['id']}: {it['title']} (due {it['due'][:16]})")
        if not items:
            print("nothing due")


if __name__ == "__main__":
    main()
