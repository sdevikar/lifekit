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

    print(f"Unknown command: {cmd}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())