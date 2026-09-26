#!/usr/bin/env bash
# deploy_local.sh — Start the LifeKit feed API + web UI locally.
#
# Usage:
#   ./deploy_local.sh          # Start both services
#   ./deploy_local.sh --stop   # Stop both services
#   ./deploy_local.sh --dev    # Start Next.js in dev mode (hot reload)
#
# The feed API runs on 127.0.0.1:8765
# The web UI runs on 127.0.0.1:3000
set -euo pipefail

# Resolve the repo root (parent of the scripts/ or project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

FEED_API_PORT=8765
WEB_PORT=${NEXT_PORT:-3000}
FEED_API_LOG=/tmp/lifekit-feed-api.log
WEB_LOG=/tmp/lifekit-web.log
FEED_API_PID=""
WEB_PID=""

cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    for pid in "$FEED_API_PID" "$WEB_PID"; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done
    wait 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Disable exit-on-error for the main script body (we handle errors manually)
set +e

# --- Stop mode ---
if [[ "${1:-}" == "--stop" ]]; then
    echo "🛑 Stopping LifeKit services..."
    for port in "$FEED_API_PORT" "$WEB_PORT"; do
        local_pid=$(lsof -ti :"$port" 2>/dev/null) || true
        if [ -n "$local_pid" ]; then
            kill -9 "$local_pid" 2>/dev/null || true
            echo "  Killed process on port $port"
        fi
    done
    echo "✅ Services stopped."
    exit 0
fi

# --- Dev mode ---
DEV_MODE=false
if [[ "${1:-}" == "--dev" ]]; then
    DEV_MODE=true
fi

echo "🚀 LifeKit Local Deployment"
echo "  Feed API: http://127.0.0.1:$FEED_API_PORT"
echo "  Web UI:   http://127.0.0.1:$WEB_PORT"
echo ""

# Check prerequisites
if ! command -v uv &>/dev/null; then
    echo "❌ 'uv' is required. Install it: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Ensure dogfood database exists
if [ ! -f "$HOME/.lifekit/lifekit.db" ]; then
    echo "📦 Copying dogfood database..."
    mkdir -p "$HOME/.lifekit"
    if [ -f "$SCRIPT_DIR/dogfood/lifekit.db" ]; then
        cp "$SCRIPT_DIR/dogfood/lifekit.db" "$HOME/.lifekit/lifekit.db"
    else
        uv run python -c "from lifekit.db.schema import init_db; init_db('$HOME/.lifekit/lifekit.db')"
    fi
fi

# --- Start the Feed API (Flask on :8765) ---
echo "→ Starting feed API on :$FEED_API_PORT..."
lsof -ti :"$FEED_API_PORT" 2>/dev/null | xargs kill -9 2>/dev/null || true
uv run python -c "from lifekit.serve.server import FeedAPI; FeedAPI().run()" >"$FEED_API_LOG" 2>&1 &
FEED_API_PID=$!

# Wait for feed API to be ready
for i in $(seq 1 15); do
    if curl -s "http://127.0.0.1:$FEED_API_PORT/api/briefing/today" >/dev/null 2>&1; then
        echo "  ✓ Feed API is ready"
        break
    fi
    if [ "$i" -eq 15 ]; then
        echo "  ❌ Feed API failed to start. Check: $FEED_API_LOG"
        cat "$FEED_API_LOG" 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# --- Start the Web UI (Next.js on :3000) ---
echo "→ Starting web UI on :$WEB_PORT..."
lsof -ti :"$WEB_PORT" 2>/dev/null | xargs kill -9 2>/dev/null || true

if [ "$DEV_MODE" = true ]; then
    echo "  (dev mode: hot reload enabled)"
    (cd frontend && npx next dev -p "$WEB_PORT" -H 127.0.0.1) >"$WEB_LOG" 2>&1 &
else
    # Ensure the production build exists
    if [ ! -d "frontend/.next" ]; then
        echo "→ Building Next.js production bundle..."
        (cd frontend && npx next build)
    fi
    (cd frontend && npx next start -p "$WEB_PORT" -H 127.0.0.1) >"$WEB_LOG" 2>&1 &
fi
WEB_PID=$!

# Wait for web UI to be ready
for i in $(seq 1 15); do
    if curl -s "http://127.0.0.1:$WEB_PORT/api/briefing/today" >/dev/null 2>&1; then
        echo "  ✓ Web UI is ready (proxy working)"
        break
    fi
    if [ "$i" -eq 15 ]; then
        echo "  ⚠ Web UI may not be fully ready. Check: $WEB_LOG"
        echo "  (The feed API is running at http://127.0.0.1:$FEED_API_PORT)"
    fi
    sleep 1
done

echo ""
echo "=============================================="
echo " ✅ LifeKit is ready!"
echo "    Feed API: http://127.0.0.1:$FEED_API_PORT"
echo "    Web UI:   http://127.0.0.1:$WEB_PORT"
echo "    Feed UI:  http://127.0.0.1:$WEB_PORT/feed"
echo ""
echo "    Phone: open the workstation's tailnet IP on port $WEB_PORT"
echo "    Logs:  $FEED_API_LOG, $WEB_LOG"
echo "    Stop:  ./deploy_local.sh --stop  or  Ctrl-C"
echo "=============================================="
echo ""

# Wait for either process to exit
wait -n "$FEED_API_PID" "$WEB_PID" 2>/dev/null || true
cleanup