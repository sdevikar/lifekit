"""lifekit/plan_forge/__main__.py — CLI entry for forge_plan module.

Usage:
    python -m lifekit.plan_forge.forge --book-id <id> --intent "learn Python" --weeks 4
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lifekit.db.schema import init_db
from lifekit.plan_forge.forge_plan import forge_plan


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate a learning plan from an ingested book.")
    parser.add_argument("book_id", help="UUID of the ingested book")
    parser.add_argument("--intent", "-i", required=True, help="User's learning goal (e.g., 'Learn Python basics')")
    parser.add_argument("--weeks", "-w", type=int, default=4, help="Duration in weeks")
    parser.add_argument("--db-path", help="SQLite path (default: ~/.lifekit/lifekit.db)")
    
    args = parser.parse_args()
    
    try:
        result = forge_plan(
            book_id=args.book_id,
            intent=args.intent,
            duration_weeks=args.weeks,
            db_path=args.db_path,
        )
        print("Plan forged successfully!")
        print(f"  Plan ID: {result['plan_id']}")
        print(f"  Duration: {result['duration_weeks']} weeks ({result['task_count']} tasks)")
        if result.get('fallback'):
            print(f"  Warning: Fallback plan generated (Ollama response was invalid JSON)")
        else:
            print("  Tasks:")
            for task in result.get('tasks', [])[:5]:  # show first 5
                print(f"    Day {task['day_number']}: {task['title']}")
            if len(result.get('tasks', [])) > 5:
                remaining = len(result.get('tasks', [])) - 5
                print(f"    ... and {remaining} more")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
