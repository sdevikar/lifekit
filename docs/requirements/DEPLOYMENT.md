# LifeKit — Deployment & Operations

## Startup

```bash
# Install dependencies
uv sync

# Build frontend
cd frontend && npx next build && cd ..

# Start the app (both services)
lifekit ui
```

## Process Management

`lifekit ui` starts two child processes:
1. Flask feed API on `127.0.0.1:8765`
2. Next.js production server on `127.0.0.1:3000`

Clean shutdown via SIGTERM/SIGINT.

## Configuration

| Config | Method | Location |
|--------|--------|----------|
| LLM provider | CLI / env / config file | `~/.lifekit/config.json` |
| LLM model | CLI / env / config file | `~/.lifekit/config.json` |
| DB path | Fixed | `~/.lifekit/lifekit.db` |

## Data Backup

- SQLite WAL mode = crash-safe.
- Backup = copy `~/.lifekit/lifekit.db` (+ WAL/SHM if active).
- No automated backup (local-first, user responsibility).

## Logging

- Flask: default request logging.
- Pipeline stages: stdout/stderr.
- No centralized logging (local-first).

## Phone Access

- Workstation's Tailnet IP on port 3000.
- No additional integration needed.
- Sandbox accepts no inbound connections.
