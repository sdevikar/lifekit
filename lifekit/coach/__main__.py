"""CLI: python -m lifekit.coach --db-path DB <list|get|log|next> ..."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lifekit.coach.tools import list_exercises, get_exercise, log_completion, next_exercise


def main():
    ap = argparse.ArgumentParser(description="Coach tools")
    ap.add_argument("--db-path", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("--book-id", required=True)
    p_list.add_argument("--limit", type=int, default=20)
    p_list.add_argument("--offset", type=int, default=0)

    p_get = sub.add_parser("get")
    p_get.add_argument("--exercise-id", type=int, required=True)

    p_log = sub.add_parser("log")
    p_log.add_argument("--exercise-id", type=int, required=True)
    p_log.add_argument("--notes", default=None)

    p_next = sub.add_parser("next")
    p_next.add_argument("--book-id", required=True)

    args = ap.parse_args()

    if args.cmd == "list":
        items = list_exercises(args.db_path, args.book_id, args.limit, args.offset)
        for it in items:
            print(f"{it['id']}: {it['title']} ({it['chapter_title']})")
    elif args.cmd == "get":
        ex = get_exercise(args.db_path, args.exercise_id)
        print(json.dumps(ex, indent=2) if ex else "not found")
    elif args.cmd == "log":
        print(json.dumps(log_completion(args.db_path, args.exercise_id, args.notes)))
    elif args.cmd == "next":
        nxt = next_exercise(args.db_path, args.book_id)
        print(json.dumps(nxt, indent=2) if nxt else "all done")


if __name__ == "__main__":
    main()
