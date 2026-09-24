"""lifekit.ui.serve — orchestrates the feed API + Next.js app.

Starts the 13a feed API (Flask, :8765) and the Next.js production server
(:3000) as subprocesses, bound to 127.0.0.1 only. Clean shutdown on exit
(CTRL-C or SIGTERM).

Logs (if needed for debugging):
  /tmp/lifekit-api.log   — feed API stderr
  /tmp/lifekit-nextjs.log — Next.js stderr
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

FEED_HOST = "127.0.0.1"
FEED_PORT = 8765
WEB_HOST = "127.0.0.1"
WEB_PORT = 3000

# Resolve directories relative to the repo root (parent of lifekit/)
_PACKAGE_DIR = Path(__file__).resolve().parent  # lifekit/ui/
_REPO_ROOT = _PACKAGE_DIR.parent.parent  # repo root
_FRONTEND_DIR = _REPO_ROOT / "frontend"


def _start_feed_api() -> subprocess.Popen:
    """Start the Flask feed API as a subprocess."""
    cmd = [
        sys.executable,
        "-c",
        "from lifekit.serve.server import FeedAPI; FeedAPI().run()",
    ]
    return subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _build_nextjs() -> None:
    """Build the Next.js production bundle (no-op if already built)."""
    next_dir = _FRONTEND_DIR / ".next"
    if next_dir.exists():
        return
    print("🔨 Building Next.js app...")
    subprocess.run(
        ["npx", "next", "build"],
        cwd=str(_FRONTEND_DIR),
        check=True,
    )


def _start_nextjs() -> subprocess.Popen:
    """Start the Next.js production server."""
    return subprocess.Popen(
        ["npx", "next", "start", "-p", str(WEB_PORT), "-H", WEB_HOST],
        cwd=str(_FRONTEND_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _wait_for_port(host: str, port: int, timeout: float = 15.0) -> bool:
    """Wait for a TCP port to accept connections."""
    import socket

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def run() -> int:
    """Start both services; return when both have shut down."""
    print(
        f"🚀 LifeKit UI starting — "
        f"feed API on http://{FEED_HOST}:{FEED_PORT}, "
        f"web on http://{WEB_HOST}:{WEB_PORT}"
    )

    # Ensure the Next.js build exists
    _build_nextjs()

    procs: list[subprocess.Popen] = []

    def shutdown(signum=None, frame=None):
        for p in procs:
            if p.poll() is None:
                p.terminate()
        for p in procs:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    try:
        print("  → Starting feed API...")
        api_proc = _start_feed_api()
        procs.append(api_proc)

        if not _wait_for_port(FEED_HOST, FEED_PORT):
            print("❌ Feed API failed to start on :8765")
            return 1

        print("  → Starting Next.js app...")
        web_proc = _start_nextjs()
        procs.append(web_proc)

        if not _wait_for_port(WEB_HOST, WEB_PORT):
            print("❌ Next.js failed to start on :3000")
            return 1

        print(f"\n✅ UI ready — open http://{WEB_HOST}:{WEB_PORT}")
        print("   (Phone: workstation tailnet IP :3000)")
        print("   Ctrl-C to stop.\n")

        # Wait indefinitely until killed
        while True:
            for p in procs:
                if p.poll() is not None and p.returncode != 0:
                    print(f"⚠️  Process exited with code {p.returncode}")
                    shutdown()
                    return p.returncode
            time.sleep(1)

    finally:
        shutdown()

    return 0