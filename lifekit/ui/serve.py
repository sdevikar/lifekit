"""lifekit.ui.serve — orchestrates the feed API + Next.js app.

Starts the 13a feed API (Flask, :8765) and the Next.js production server
(:3783) as subprocesses, bound to 127.0.0.1 only. Clean shutdown on exit
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
WEB_PORT = 3783

# Resolve directories relative to the repo root (parent of lifekit/)
_PACKAGE_DIR = Path(__file__).resolve().parent  # lifekit/ui/
_REPO_ROOT = _PACKAGE_DIR.parent.parent  # repo root
_FRONTEND_DIR = _REPO_ROOT / "frontend"
_NEXT_BIN = _FRONTEND_DIR / "node_modules" / "next" / "dist" / "bin" / "next"


def _kill_stale_port(port: int) -> None:
    """Kill any process listening on *port* so our subprocess can bind.

    Uses ``fuser -k`` (more reliable than ``lsof`` for finding processes
    by port on Linux).  Silently skips if ``fuser`` is unavailable.
    """
    try:
        subprocess.run(
            ["fuser", "-k", "%d/tcp" % port],
            capture_output=True,
        )
    except FileNotFoundError:
        pass  # fuser not available — skip


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
    """Build the Next.js production bundle.

    Always rebuilds. The build is incremental and costs ~2-4s, and skipping it
    when ``.next`` merely *exists* serves a stale bundle after a source change
    — or fails outright with "Could not find a production build" when the
    directory only holds ``next dev`` artifacts.
    """
    print("🔨 Building Next.js app...")
    subprocess.run(
        ["npx", "next", "build"],
        cwd=str(_FRONTEND_DIR),
        check=True,
    )


def _start_nextjs() -> subprocess.Popen:
    """Start the Next.js production server.

    Uses ``node`` to run the Next.js binary directly, not ``npx``.
    The ``npx`` wrapper spawns a detached ``node`` child and exits
    immediately, which makes ``Popen.poll()`` report a stale exit
    code (1) while the real server keeps running orphaned.
    """
    return subprocess.Popen(
        ["node", str(_NEXT_BIN), "start", "-p", str(WEB_PORT), "-H", WEB_HOST],
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


def _wait_for_port_with_proc(
    host: str, port: int, proc: subprocess.Popen, timeout: float = 15.0
) -> bool:
    """Wait for a port to open **and** the subprocess to still be alive.

    A stale process from a previous run can hold the port open even when
    our new subprocess failed to bind.  This function detects that by
    checking ``proc.poll()`` alongside the port check.
    """
    import socket

    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            return False  # process died before (or right after) opening the port
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

    # Clear stale processes from a previous run
    _kill_stale_port(FEED_PORT)
    _kill_stale_port(WEB_PORT)

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

        if not _wait_for_port_with_proc(FEED_HOST, FEED_PORT, api_proc):
            rc = api_proc.poll()
            if rc is not None:
                print(f"❌ Feed API exited with code {rc} (port :8765 may be in use)")
            else:
                print("❌ Feed API failed to start on :8765")
            return 1

        print("  → Starting Next.js app...")
        web_proc = _start_nextjs()
        procs.append(web_proc)

        if not _wait_for_port_with_proc(WEB_HOST, WEB_PORT, web_proc):
            rc = web_proc.poll()
            if rc is not None:
                print(f"❌ Next.js exited with code {rc} (port :{WEB_PORT} may be in use)")
            else:
                print(f"❌ Next.js failed to start on :{WEB_PORT}")
            return 1

        print(f"\n✅ UI ready — open http://{WEB_HOST}:{WEB_PORT}")
        print(f"   (Phone: workstation tailnet IP :{WEB_PORT})")
        print("   Ctrl-C to stop.\n")

        # Wait indefinitely until killed
        while True:
            for i, p in enumerate(procs):
                rc = p.poll()
                if rc is not None and rc != 0:
                    label = "feed API" if i == 0 else "Next.js"
                    print(f"⚠️  {label} process exited with code {rc}")
                    shutdown()
                    return rc
            time.sleep(1)

    finally:
        shutdown()

    return 0