"""CLI: split a PDF into chapters and print them.

Usage:
    python -m lifekit.store.split --pdf <path/to/book.pdf> [--db-path PATH]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lifekit.db.schema import init_db
from lifekit.store.chapter_splitter import split_chapters, EmptyPDFError


def main():
    parser = argparse.ArgumentParser(
        description="Split a PDF into chapters (TOC-first) and list them."
    )
    parser.add_argument("--pdf", required=True, help="Path to a PDF file")
    parser.add_argument(
        "--db-path", default=None,
        help="SQLite path; chapters are persisted when given "
             "(default: ~/.lifekit/lifekit.db)",
    )
    parser.add_argument(
        "--no-persist", action="store_true",
        help="Do not persist chapters, only print them",
    )
    args = parser.parse_args()

    db_path = None if args.no_persist else (args.db_path or str(Path.home() / ".lifekit" / "lifekit.db"))
    if db_path:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        init_db(db_path)

    try:
        chapters = split_chapters(args.pdf, db_path=db_path)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except EmptyPDFError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"{len(chapters)} chapters:")
    for c in chapters:
        print(f"  [{c.index}] {c.title}  (pp. {c.page_start}-{c.page_end}, "
              f"{len(c.text)} chars)")
    if db_path:
        print(f"Persisted to {db_path}")


if __name__ == "__main__":
    main()
