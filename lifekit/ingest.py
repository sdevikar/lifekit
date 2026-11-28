"""Stage runner for `lifekit ingest`."""

from __future__ import annotations

import argparse

from lifekit.books.structure import ingest as structure_ingest


STAGES = ["structure"]  # items, cards added by later slices


def run_ingest(file_path, db_path=None, book_id=None, from_stage=None):
    db_path = db_path or str(__import__("pathlib").Path.home() / ".lifekit" / "lifekit.db")
    # only structure for now
    return structure_ingest(db_path, file_path, book_id)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="lifekit ingest")
    parser.add_argument("file")
    parser.add_argument("--db", dest="db_path", default=None)
    parser.add_argument("--book-id", dest="book_id", default=None)
    parser.add_argument("--from", dest="from_stage", default=None)
    args = parser.parse_args(argv)
    bid = run_ingest(args.file, db_path=args.db_path, book_id=args.book_id,
                     from_stage=args.from_stage)
    print(f"Ingested book: {bid}")


if __name__ == "__main__":
    main()