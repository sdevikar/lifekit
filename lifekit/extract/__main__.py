"""CLI: run the extraction map over every chapter of a book.

Usage:
    python -m lifekit.extract --db-path <db> --book-id <id> [--model TAG]

Prints a per-chapter summary (key ideas, exercise counts). Persistence of
extractions is Step 3's job; this command only runs the map.
"""
import argparse
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lifekit.db.schema import init_db
from lifekit.extract.extractor import DEFAULT_MODEL, extract_chapter
from lifekit.store.chapter_splitter import Chapter


def _load_chapters(db_path: str, book_id: str) -> list[Chapter]:
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT idx, title, content, page_start, page_end FROM chapters "
        "WHERE book_id = ? ORDER BY idx",
        (book_id,),
    ).fetchall()
    return [
        Chapter(index=r[0], title=r[1], text=r[2], page_start=r[3], page_end=r[4])
        for r in rows
    ]


def main():
    parser = argparse.ArgumentParser(description="Extract exercises per chapter.")
    parser.add_argument("--db-path", default=None,
                        help="SQLite path (default: ~/.lifekit/lifekit.db)")
    parser.add_argument("--book-id", required=True, help="Book id in chapters table")
    parser.add_argument("--model", default=None, help=f"Ollama model (default: {DEFAULT_MODEL})")
    parser.add_argument("--chapters", default=None,
                        help="Comma-separated chapter indexes to extract (default: all)")
    parser.add_argument("--out", default=None,
                        help="Write full ChapterExtraction JSON array to this path")
    args = parser.parse_args()

    db_path = args.db_path or str(Path.home() / ".lifekit" / "lifekit.db")
    init_db(db_path)
    chapters = _load_chapters(db_path, args.book_id)
    if args.chapters:
        wanted = {int(x) for x in args.chapters.split(",")}
        chapters = [c for c in chapters if c.index in wanted]
    if not chapters:
        print(f"No chapters found for book_id={args.book_id}", file=sys.stderr)
        sys.exit(1)

    total_ex = 0
    all_results = []
    for ch in chapters:
        result = extract_chapter(ch, model=args.model)
        total_ex += len(result.exercises)
        all_results.append(result.model_dump())
        print(f"[{ch.index}] {result.chapter_title}: "
              f"{len(result.key_ideas)} key ideas, {len(result.exercises)} exercises")
        for ex in result.exercises:
            print(f"    - {ex.title}")
    print(f"Total: {total_ex} exercises across {len(chapters)} chapters")
    if args.out:
        import json

        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(all_results, indent=2))
        print(f"Wrote {len(all_results)} chapter extractions to {args.out}")


if __name__ == "__main__":
    main()
