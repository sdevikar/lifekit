# ARCHIVED 2026-07-08
## Why

LifeKit has a rich multi-phase roadmap but no shippable starting point. Before anything else works — momentum tracking, interviewing, invitation bubbles, OpenWebUI integration — we need a single runnable loop that reads a local PDF book, generates a SMART learning plan via Ollama, persists that plan in SQLite, and surfaces the next actionable task via an MCP tool. This is the trunk every other feature grafts onto.

## What Changes

- **New**: Project scaffold — `pyproject.toml` (Poetry), `../../../lifekit/` package root, `Makefile` dev targets
- **New**: SQLite schema bootstrap — `../../../lifekit/db/schema.py` with migrations for `books`, `plans`, `tasks`, `sessions`
- **New**: PDF ingestion — `../../../lifekit/store/pdf_ingester.py` that chunks a local PDF into the `books` table (no vector DB yet; plain FTS5 full-text search)
- **New**: Plan forge — `../../../lifekit/plan_forge/forge_plan.py` that sends book metadata + user intent to Ollama (`qwen3.6:latest`) and writes a SMART weekly plan to the `plans` / `tasks` tables
- **New**: MCP server — `../../../lifekit/mcp/server.py` (FastMCP) exposing `get_next_task`, `complete_task`, `get_plan_status` tools that OpenWebUI / Claude Desktop can call
- **Deferred**: User interviewer, momentum decay engine, invitation bubbles, exercise logging schema, context injector, OpenWebUI pipe — all retained in the roadmap but NOT implemented here

## Capabilities

### New Capabilities

- `project-scaffold`: Package layout, dependencies (Poetry), `Makefile`, `.env.example`, README quick-start
- `db-schema`: SQLite schema + migration runner for the four core tables: `books`, `plans`, `tasks`, `sessions`
- `pdf-ingest`: Local PDF → chunked text stored in `books` table with FTS5 index; single hardcoded book path to start
- `plan-forge`: Ollama-powered SMART plan generation from book content; writes structured `plans` + `tasks` rows
- `mcp-tools`: FastMCP server with three tools: `get_next_task`, `complete_task`, `get_plan_status`

### Modified Capabilities

*(none — greenfield)*

## Impact

- **New Python package**: `../../../lifekit/` under `pyproject.toml`; Python ≥ 3.11, Poetry for deps
- **Runtime dependency**: Ollama running locally with `qwen3.6:latest` (or configurable model)
- **Storage**: SQLite file at `~/.lifekit/lifekit.db` (path configurable via env)
- **MCP surface**: `../../../lifekit/mcp/server.py` run as `python -m lifekit.mcp.server`; connects to OpenWebUI or Claude Desktop via stdio transport
- **No external services**: fully local, no auth, no cloud — this is the offline-first foundation
