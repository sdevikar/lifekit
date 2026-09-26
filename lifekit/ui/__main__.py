"""CLI entry point: `python -m lifekit.ui` starts the feed API + Next.js app."""

import sys

from lifekit.ui.serve import run

if __name__ == "__main__":
    sys.exit(run())