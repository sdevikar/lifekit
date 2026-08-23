# LifeKit MVP: What We're Building

**MVP Scope:** Book ingestion → Ollama-powered SMART plan generation → SQLite persistence → MCP tools for task management. Everything beyond this is explicitly deferred with phase tags in [design.md](openspec/changes/lifekit-mvp-core-loop/design.md).

---

## The One-Liner

LifeKit MVP takes a local PDF book, slices it into chunks, generates a SMART learning plan via Ollama (qwen3.6:latest), persists everything in SQLite, and surfaces the next actionable task as an MCP tool callable by any LLM client (Claude Desktop, OpenWebUI).

**What this enables today:** Drop a PDF → get a structured 28-day reading/exercise plan → query progress via MCP tools at any time.

---

## In-Scope: Seven Components (Shipped)

### 1. Project Scaffold
- `pyproject.toml` with Poetry, Python ≥ 3.11
- Dependencies: `fastmcp`, `pypdf2`, `ollama`, `pydantic`, `python-dotenv`
- `lifekit/` package root with sub-packages: `db/`, `store/`, `plan_forge/`, `mcp/`
- `.env.example` documenting all env vars (defaults to qwen3.6:latest)
- `Makefile` targets: `bootstrap`, `ingest`, `forge`, `serve`, `test`
- `__main__.py` in `store/` and `plan_forge/` for CLI dispatch

### 2. Database Schema (SQLite + FTS5)
**Five tables — all created idempotently:**

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `books` | Book metadata | id (UUID), title, author, file_path, chunk_count |
| `book_chunks` | Text chunks for search | book_id, chunk_index, content, page_number |
| `book_chunks_fts` | FTS5 virtual table for full-text search | auto-populated via triggers |
| `plans` | Learning plans | id (UUID), book_id, user_intent, duration_weeks |
| `tasks` | Day-by-day exercises | plan_id, day_number, title, description, estimated_minutes, exercise_type, context_source, status, completed_at |
| `sessions` | Task completion logs | task_id, notes, started_at |

**Implementation notes:**
- All triggers use explicit INSERT/DELETE on FTS5 for correctness after writes.
- Duplicate file_path check uses `BEGIN IMMEDIATE` to prevent TOCTOU races.
- Schema migrates cleanly to PostgreSQL later (no SQLite-specific types).

### 3. PDF Ingestion (`lifekit/store/pdf_ingester.py`)
**What it does:**
1. Opens a local PDF via PyPDF2
2. Extracts text page by page
3. Chunks into ~2000 char (~500 token) segments with page_number + chunk_index
4. Inserts book metadata + chunks in a single transaction
5. Updates FTS5 index immediately

**Error handling:**
- `ValueError` on empty PDF (zero text extracted)
- `FileExistsError` on duplicate file_path (with BEGIN IMMEDIATE lock)

### 4. Plan Forge (`lifekit/plan_forge/forge_plan.py`)
**What it does:**
1. Pulls first 10 chunks from the book for the given book_id
2. Builds prompt: book title + author + excerpt + user intent + JSON schema instruction
3. Calls Ollama (qwen3.6:latest) with `ollama.chat()`
4. Validates response against Pydantic `PlanResponse` schema
5. Inserts plan + tasks in a single transaction

**Error handling:**
- Pydantic validation failure → fallback to single "Read and reflect" task
- Ollama connection failure → RuntimeError with instructional message
- Existing pending plan for book → PlanExistsError

### 5. MCP Server (`lifekit/mcp/server.py`)
**Three tools via FastMCP stdio transport:**

| Tool | Arguments | Returns | Error Cases |
|------|-----------|---------|-------------|
| `get_next_task` | `plan_id: str = ""` (optional) | Next pending task or null message `{"ok": true/false, "result": ..., "error": ...}` | No plans available |
| `complete_task` | `task_id: int`, `notes: str = ""` | Confirmation + inserted session row | task_not_found, task_already_completed |
| `get_plan_status` | `plan_id: str = ""` (optional) | Aggregated counts + completion_percentage | no_plan_found |

**Response envelope format:** All tools use consistent `{"ok": bool, "result": data | null, "error": string | null}` pattern.

### 6. Migration / Setup Flow
```bash
make bootstrap        # Creates DB, applies schema
make ingest PDF=path/to/book.pdf   # Parses & chunks the book
make forge INTENT="finish this book in 4 weeks"  # Generates plan via Ollama
make serve            # Starts MCP server via stdio
```

Configure MCP client (Claude Desktop / OpenWebUI) with: `python -m lifekit.mcp.server`

### 7. Integration Smoke Test Checklist
- `make bootstrap` → db exists, correct tables present
- Drop PDF + `make ingest` → chunk_count matches reality
- `make forge INTENT="..."` → tasks created for duration_weeks × 7 days
- `make serve` → MCP tools callable via JSON-RPC over stdio
- `get_next_task` → returns earliest pending task
- `complete_task` → status updates, plan_status reflects accurately

---

## Out of Scope (Explicitly Deferred)

| Feature | Phase | Why Not MVP |
|---------|-------|-------------|
| User bio / Interviewer | Phase 1 | Can seed manually for now; interview is a thin veneer |
| Momentum decay engine | Phase 1 | Core IP — build after validating core loop works |
| Context injection layer | Phase 1 | Needs knowledge store + exercise engine first |
| Invitation bubbles/cards | Phase 1 | UX layer on top of MCP tooling (already live) |
| Exercise taxonomy (Feynman/Journal) | Phase 1 | Requires evaluator module; adds scope creep |
| Content digestibility / chapters | Phase 2 | Archived as non-blocker for MVP core loop |
| Context-aware planning | Phase 2 | Mvp uses fixed excerpt window, not RAG |
| Multi-book support | Phase 1+ | Single book MVP proves the trunk first |
| Vector embeddings | Phase 2+ | FTS5 sufficient; adds unnecessary dependency |
| Authentication / multi-user | Phase 2+ | Not MVP scope; single-user for now |
| Kindle/Goodreads/Libby integration | Phase 2+ | Connector layer is a separate engineering effort |
| Live OpenWebUI pipe integration | Phase 1 | MCP tools are the integration surface; UI comes later |
| React dashboard + momentum viz | Phase 3 | Frontend production work; separate build pipeline |

**Key principle:** MVP is one book → plan → task → query. Everything else adds complexity to a path we can prove works first.

---

## Architecture Snapshot

```
knowledge-store/books/         ← Drop PDFs here (gitignored)
├── my_book.pdf
└── ...

lifekit/                       ← Python package
├── __init__.py
├── db/
│   ├── schema.py              ← init_db() + idempotent migrations
│   └── models.py              ← (Future: Pydantic models for API)
├── store/
│   ├── __init__.py
│   ├── __main__.py            ← make ingest entry point
│   └── pdf_ingester.py        ← chunk, insert, index FTS5
├── plan_forge/
│   ├── __init__.py
│   ├── __main__.py            ← make forge entry point
│   ├── forge_plan.py          ← Ollama call + Pydantic validation
│   └── pydantic_models.py     ← TaskItem, PlanResponse schemas
└── mcp/
    ├── __init__.py
    ├── server.py              ← FastMCP stdio: get_next_task, complete_task, get_plan_status
    └── models.py              ← MCP tool schema / response types

~/.lifekit/lifekit.db           ← SQLite DB (configurable via LIFEKIT_DB env)
```

---

## Model Config

**Model:** `qwen3.6:latest` (via Ollama, configurable with `OLLAMA_MODEL` env var).

All references across pitch.md, plan.md, prosal.md, design.md, tasks.md, and all specs are now consistent on this model name.

---

## How to Use This Document

- **Builders:** Follow steps 1–7 in order; each component is a self-contained module you can implement independently.
- **Reviewers:** The "Out of Scope" table tells you exactly what's NOT being built — no ambiguity about scope boundaries.
- **Future Phase Planning:** Defer feature column maps directly to openspec CRs for Phase 1+ work; each row is a future CR candidate.

---

*Last updated: after full MVP specification audit (Fixes #1 through Fix #10 applied). The MVP scope is now locked — any additions require a new openspec CR.*
