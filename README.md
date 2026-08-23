# LifeKit — Active AI Thought Partner

LifeKit bridges the gap between consuming knowledge (books, videos, PDFs) and living it (exercises, reflection, habit formation). It takes a local PDF book, chunks its content, generates a personalized SMART learning plan via Ollama (qwen3.6:latest), persists everything in SQLite with FTS5 full-text search, and exposes task management as MCP tools callable by any LLM client (Claude Desktop, OpenWebUI).

## Current Status — Release 0.1.0 (Phase 0 Complete)

### What's Built ✅

| Feature | Status | Files |
|---------|--------|-------|
| **Project scaffold** | ✅ Complete | `pyproject.toml`, `.env.example`, `Makefile`, package layout |
| **Database schema** | ✅ Complete | `lifekit/db/schema.py` — 5 tables + FTS5 triggers, `init_db()` |
| **PDF ingestion** | ✅ Complete | `lifekit/store/pdf_ingester.py` — sentence-boundary chunking (~2000 chars) with duplicate guard and empty-PDF safety |
| **Plan forge** | ✅ Complete | `lifekit/plan_forge/forge_plan.py` — Ollama integration + Pydantic validation; supports teaching methods: socratic, feynman, analogical, spaced_recall |
| **MCP server** | ✅ Complete | `lifekit/mcp/server.py` — JSON-RPC stdio transport with 3 tools: `get_next_task`, `complete_task`, `get_plan_status` (now includes teaching_method in status output) |

### Phase 0 Implementation Details

```
lifekit/                          [11 Python files, ~1,059 lines]
├── __init__.py                   [v0.1.0]
├── db/
│   ├── __init__.py              [db init + exports: init_db, get_connection]
│   └── schema.py                [CREATE TABLE × 5, FTS5 virtual table + triggers, init_db(), get_connection()]
├── store/
│   ├── __init__.py              [stores: ingest_pdf, EmptyPDFError, DuplicateIngestError]
│   ├── __main__.py              [CLI entry: python -m lifekit.store --pdf <path>]
│   └── pdf_ingester.py          [PDFChunker, sentence-boundary chunking, book+chunks insert with duplicate detection]
├── plan_forge/
│   ├── __init__.py              [exports: forge_plan, ALLOWED_TEACHING_METHODS, PlanExistsError, TaskParsingError]
│   ├── __main__.py              [CLI entry: python -m lifekit.plan_forge --intent <goal> --weeks <n>]
│   └── forge_plan.py            [_build_prompt(), Ollama chat + PlanResponse validation, atomic plan+tasks insert; fallback for invalid LLM responses]
└── mcp/
    ├── __init__.py              [exports: run_mcp_server]
    └── server.py                [handle_get_next_task, handle_complete_task, handle_get_plan_status, JSON-RPC stdio transport]
```

### Not Yet Built (Roadmap)

- User interviewer (onboarding interview pipeline)
- Momentum decay engine + spaced repetition tracker
- Invitation bubbles / external data pulls
- Exercise logging schema + context injector
- Production UI (React/Tailwind SPA; MVP uses OpenWebUI)
- Vector embeddings / semantic chunk similarity search

---

## Prerequisites

- **Python 3.11+** (tested with 3.12)
- **Ollama running locally** on `http://localhost:11434` with model `qwen3.6:latest` (or any compatible model)
- **A PDF book** ready to ingest (e.g., `~/Downloads/AtomicHabits.pdf`)

## Quick Start

### 1. Bootstrap the database

```bash
cd /home/swapnil/workspace/projects/lifekit
make bootstrap        # creates ~/.lifekit/lifekit.db with all tables
```

This establishes SQLite with five tables and FTS5 triggers for full-text search over book content. Idempotent — safe to re-run.

### 2. Ingest a PDF book

```bash
make ingest PDF=/path/to/book.pdf       # parses the PDF into searchable chunks
# or directly:
python -m lifekit.store --pdf /path/to/book.pdf
```

The book is split into ~2000-character overlapping chunks with sentence-boundary detection. Results go into `books` + `book_chunks` tables with FTS5 indexing for fast keyword retrieval.

**Safety features:** duplicate ingest guard (same file path → `DuplicateIngestError`), empty-PDF guard (`EmptyPDFError`), and TOCTOU safety via `BEGIN IMMEDIATE` transactions.

### 3. Generate a learning plan

```bash
make forge INTENT="Finish Atomic Habits in 4 weeks" --method socratic
# or directly:
python -m lifekit.plan_forge.forgbook_id> --intent="Your goal here" --weeks 4 --method feynman
```

LifeKit sends the book's first ~2000 characters of content plus your intent to Ollama, producing a SMART daily learning plan. The teaching method controls *how* tasks are framed:

| `--method` | Approach |
|------------|----------|
| `auto` (default) | Falls back to Socratic |
| `socratic` | Guided inquiry — questions over answers |
| `feynman` | Teach-to-a-beginner with simple analogies and metaphors |
| `analogical` | Cross-domain connections (music, sports, cooking, etc.) |
| `spaced_recall` | Active retrieval using the Leitner principle |

**Important:** The generated plan depends on how well your local Ollama model returns valid JSON matching the `PlanResponse` schema. If the response is invalid, LifeKit creates fallback tasks instead of failing.

### 4. Start the MCP server for LLM clients

```bash
make serve            # starts JSON-RPC over stdio transport
# or directly:
python -m lifekit.mcp.server
```

The MCP server exposes three tools via JSON-RPC that any LLM client (Claude Desktop, OpenWebUI) can call to retrieve the next task, mark it complete, and query plan status.

## MCP Tools

| Tool | Arguments | Returns |
|------|-----------|---------|
| `get_next_task` | `plan_id?: string` | Next pending task as JSON dict, or null if no tasks remain |
| `complete_task` | `task_id: int`, `notes?: string` | Confirmation with session row inserted |
| `get_plan_status` | `plan_id?: string` | `{book_title, user_intent, teaching_method, total_tasks, complete_count, pending_tasks, completion_percentage}` (or latest plan if no ID given) |

All responses use the envelope: `{ok: boolean, result: data|null, error: string|null}`.

## Environment Variables

Copy `.env.example` to `.env`:

```bash
LIFEKIT_DB=~/.lifekit/lifekit.db      # SQLite database path
OLLAMA_MODEL=qwen3.6:latest            # Local inference model (must be downloaded first)
OLLAMA_BASE_URL=http://127.0.0.1:11434  # Ollama endpoint
```

## Makefile Commands

| Command | Purpose |
|---------|---------|
| `make bootstrap` | Initialize SQLite with schema |
| `make ingest PDF=...` | Ingest a PDF into the knowledge store |
| `make forge INTENT=--method ...` | Generate a personalized learning plan (also accepts `--weeks`) |
| `make serve` | Start MCP server for LLM client integration |
| `make test` | Run pytest suite (add tests when ready) |
| `make lint` | Compile-check all Python files via py_compile |
| `make clean` | Remove `__pycache__` and `.pyc` files |

## Project Structure (Current Files)

```
lifekit/                              [11 Python files, ~1,059 lines total]
├── __init__.py                       Package root + version
├── db/                               Database layer
│   ├── __init__.py                  init_db(), get_connection(), SCHEMA string
│   └── schema.py                    CREATE TABLE × 5, FTS5 triggers, VIRTUAL TABLE
├── store/                            PDF ingestion pipeline
│   ├── __init__.py                  ingest_pdf, EmptyPDFError, DuplicateIngestError
│   ├── __main__.py                  CLI entry + argparse (--pdf)
│   └── pdf_ingester.py              PDFChunker (pypdf), sentence-boundary chunking
├── plan_forge/                       Plan generation engine
│   ├── __init__.py                  forge_plan, ALLOWED_TEACHING_METHODS, exceptions
│   ├── __main__.py                  CLI entry + argparse (--intent, --weeks, --method)
│   └── forge_plan.py                _build_prompt(), ollama.chat(), Pydantic validation, atomic insert
├── mcp/                              MCP server
│   ├── __init__.py                  handle_get_next_task, handle_complete_task, handle_get_plan_status
│   └── server.py                    JSON-RPC stdio transport + handler routing
pyproject.toml                         [build-system: setuptools; deps: pydantic, ollama]
.env.example                            3 env vars documented
Makefile                               bootstrap, ingest, forge, serve, test, lint, clean
```

## Error Handling Reference

| Scenario | Behavior | Exception / Result |
|----------|----------|-------------------|
| Empty PDF | Guarded before insertion | `EmptyPDFError(file_path)` |
| Duplicate ingest (same file path) | Rejected with informative message | `DuplicateIngestError(existing_record_info)` |
| Ollama not running / connection refused | Caught and re-raised with instructions | `RuntimeError("Ollama not reachable...")` |
| Invalid LLM response (non-JSON / schema mismatch) | Falls back to 7 generic "Read and reflect" tasks | Returns plan with `fallback: True` flag |
| Active plan already exists for book | Prevents overwriting | `PlanExistsError(book_id)` |
| TOCTOU race on ingest | `BEGIN IMMEDIATE` prevents duplicate inserts | Handled gracefully by SQLite; raises constraint violation |

## Release Log

| Version | Date | Summary |
|---------|------|---------|
| **0.1.0** | 2026-07-08 | Phase 0 complete: scaffolding, db schema, PDF ingestion, plan forge (with teaching method support), MCP server, docs. Full file tree and implementation details above. |
