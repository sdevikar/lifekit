"""CLI: python -m lifekit.books <register|search> ..."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lifekit.books.registry import register_book
from lifekit.books.search import search_exercises


def main():
    ap = argparse.ArgumentParser(description="Multi-book registry and search")
    ap.add_argument("--db-path", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_reg = sub.add_parser("register")
    p_reg.add_argument("--pdf", required=True)
    p_reg.add_argument("--title", default=None)
    p_reg.add_argument("--author", default=None)

    p_search = sub.add_parser("search")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--book-id", action="append", default=None)

    args = ap.parse_args()

    if args.cmd == "register":
        bid = register_book(args.db_path, args.pdf, args.title, args.author)
        print(f"book_id={bid}")
    elif args.cmd == "search":
        result = search_exercises(args.db_path, args.query, book_ids=args.book_id)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
