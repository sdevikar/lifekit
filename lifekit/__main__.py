"""Top-level CLI entry point for `lifekit`.

Subcommands:
  lifekit ui   — start the feed API + Next.js app (localhost only)
  lifekit config — view/set LLM provider config

Other modules use `python -m lifekit.<submodule>` directly (store, mcp, etc).
"""

import sys


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(
            "LifeKit — usage:\n"
            "  lifekit ui        Start the feed API + web UI\n"
            "  lifekit config    View or set LLM provider config\n"
            "  python -m lifekit.store    Extract book chapters\n"
            "  python -m lifekit.mcp.server   Run the MCP server\n"
        )
        return 0

    cmd = args[0]

    if cmd == "ui":
        from lifekit.ui.serve import run as run_ui

        return run_ui()

    if cmd == "config":
        from lifekit.config.__main__ import main as run_config

        sys.argv = ["lifekit config"] + args[1:]
        return run_config()

    if cmd == "ingest":
        from lifekit.ingest import main as run_ingest
        sys.argv = ["lifekit ingest"] + args[1:]
        return run_ingest() or 0

    if cmd == "book":
        sub = args[1] if len(args) > 1 else ""
        if sub == "sections":
            bid = args[2]
            import sqlite3
            from pathlib import Path
            db = str(Path.home() / ".lifekit" / "lifekit.db")
            conn = sqlite3.connect(db)
            for r in conn.execute(
                "SELECT idx, parent_idx, depth, title, kind, page_start, page_end FROM sections WHERE book_id=? ORDER BY idx",
                (bid,),
            ):
                print(r)
            return 0
        if sub == "set-kind":
            bid, idx, kind = args[2], int(args[3]), args[4]
            import sqlite3
            from pathlib import Path
            db = str(Path.home() / ".lifekit" / "lifekit.db")
            conn = sqlite3.connect(db)
            conn.execute(
                "INSERT INTO section_kind_overrides (book_id, section_idx, kind) VALUES (?,?,?) "
                "ON CONFLICT(book_id, section_idx) DO UPDATE SET kind=excluded.kind",
                (bid, idx, kind),
            )
            conn.commit()
            print(f"set {bid} section {idx} -> {kind}")
            return 0
        print("Usage: lifekit book {sections|set-kind}", file=sys.stderr)
        return 1

    print(f"Unknown command: {cmd}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())