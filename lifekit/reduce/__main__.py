"""CLI: python -m lifekit.reduce --db-path DB --book-id ID --extractions JSON."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lifekit.extract.extractor import ChapterExtraction
from lifekit.reduce.reducer import reduce_extractions


def main():
    ap = argparse.ArgumentParser(description="Reduce chapter extractions to exercises tables")
    ap.add_argument("--db-path", required=True)
    ap.add_argument("--book-id", required=True)
    ap.add_argument("--extractions", required=True,
                    help="Path to JSON array of ChapterExtraction dicts")
    args = ap.parse_args()

    data = json.loads(Path(args.extractions).read_text())
    extractions = [ChapterExtraction.model_validate(d) for d in data]

    summary = reduce_extractions(args.book_id, args.db_path, extractions)
    print(f"book_id={summary['book_id']}")
    print(f"candidates={summary['candidates']}")
    print(f"exercises={summary['exercises']}")
    print(f"key_ideas={summary['key_ideas']}")
    print(f"merges={summary['merges']}")


if __name__ == "__main__":
    main()
