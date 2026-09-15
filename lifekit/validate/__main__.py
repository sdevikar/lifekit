"""CLI: python -m lifekit.validate --db-path DB --book-id ID [--chapters JSON] [--judge]."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lifekit.validate.validator import validate_book
from lifekit.validate.judge import run_judge_sample


def main():
    ap = argparse.ArgumentParser(description="Validate exercise grounding")
    ap.add_argument("--db-path", required=True)
    ap.add_argument("--book-id", required=True)
    ap.add_argument("--chapters", default=None,
                    help="JSON list of [title, text] for chapter lookup")
    ap.add_argument("--judge", action="store_true",
                    help="Run 10%% LLM judge sample")
    args = ap.parse_args()

    chapters = []
    if args.chapters:
        chapters = [tuple(x) for x in json.loads(Path(args.chapters).read_text())]

    result = validate_book(args.db_path, args.book_id, chapters)
    print(f"passed={result['passed']} failed={result['failed']}")
    if result["zero_flags"]:
        print(f"zero_flags: {result['zero_flags']}")

    if args.judge:
        # Judge needs a client; skip if ollama not available
        try:
            import ollama
            client = ollama.Client()
            jr = run_judge_sample(args.db_path, args.book_id, chapters, client=client)
            print(f"judged={jr['sampled']} scores={jr['scores']}")
        except Exception as e:
            print(f"judge skipped: {e}")


if __name__ == "__main__":
    main()
