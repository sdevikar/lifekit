## Context

LifeKit is a self-help AI assistant currently described only in a roadmap document. There is no runnable code. The plan describes a six-step PoC (P0-A through P0-F) plus a Phase 1, but many of those steps have coupled dependencies (e.g., context injection needs a knowledge store, invitations need momentum tracking). Building them all before anything runs creates a large integration risk.

The MVP strips LifeKit down to its single irreducible loop: **load a book → generate a plan → ask "what's next?"**. Everything else in the roadmap is additive to this trunk.

**Model**: `qwen3.6:latest`. Book source files live at `knowledge-store/books/` in the project root — gitignored, drop PDFs there manually. Model config is read from `.env` via env var `OLLAMA_MODEL`, defaulting to this name.

Reference model: `tutor-mcp` (Go, MCP server) achieves persistence + scheduling without a UI by letting the LLM call tools like `get_next_activity` / `record_interaction`. We adopt the same "durable state + tool surface" pattern in Python.

## Goals / Non-Goals

**Goals:**
- Ship a runnable Python package in < 1 week of focused work
- Ingest a single local PDF into SQLite (chunked, FTS5 indexed)
- Generate a SMART weekly plan via Ollama and persist it
- Expose `get_next_task` / `complete_task` / `get_plan_status` as MCP tools (stdio transport)
- Zero network dependencies at runtime (Ollama runs locally)

**Non-Goals:**
- User bio / interviewer (P0-A) — deferred
- Momentum decay engine (P0-C) — deferred  
- Context injection / invitation bubbles (P0-D, P0-E) — deferred
- OpenWebUI pipe integration (P0-F) — deferred
- Multiple books / knowledge sources — deferred
- Vector embeddings / semantic search — deferred (FTS5 is sufficient for MVP)
- Authentication, multi-user, cloud deployment — deferred

## User Story Mapping

This table maps every user story to its implementation status. **MVP items are green (shipped); others are explicitly deferred.**

| US # | Requirement | MVP Status | Phase | Notes |
|------|-------------|------------|-------|-------|
| US-01: New Interview | Bio/Goals | Deferred | 1 | Seeded manually in MVP |
| US-02: Upload Books | Ingest PDFs | Partial (`pdf-ingest`) | 1+ | EPUB/YouTube/Facebook → Phase 1+ |
| US-03: Context Injection | Opening card | Deferred | 1 | Requires injector module |
| US-04: Non-assumptive UX | Invitation-only | Deferred | 1 | Contract for future |
| US-05: Feynman Check | Concept eval | Deferred | 1 | Exercise engine → Phase 1 |
| US-06: Habit Log | Action tracking | Deferred | 1 | Momentum decay not in MVP |
| US-07: Guided Journal | Tone analysis | Deferred | 1 | Requires Ollama eval step |
| US-08: Unprompted Journal | Free-text log | Deferred | 1 | Not MVP scope |
| US-09: Content Digest | Chapter aware | Deferred | 2 | Archived (heuristic not needed for MVP) |
| US-10: Weekly Review | Aggregation UI | Deferred | 1 | Plan/status tools enable it |
| US-11/12: External Libs | Kindle/Goodreads | Deferred | 2+ | Connector layer; not MVP |
| US-14: OpenWebUI Surface | Invitations UI | Deferred | 1 | Tooling is live; UI not |
| US-15: React Dashboard + Momentum Viz | Charts/dash | Deferred | 3 | Frontend production phase |
| US-16: Revival Mode | Decay/Recovery | Deferred | 1 | Core IP — priority for Phase 1 |
| US-17: Error Handling & Fallbacks | Resilience | Implemented | MVP | Covered in spec error paths |

**MVP Scope (green):** Book ingestion → plan generation via Ollama → task management via MCP. Everything else is explicit deferred work mapped to its phase tag.

### Decision 1: Python + Poetry over Go
The full LifeKit roadmap is Python. Using Go (like tutor-mcp) would create a cross-language split. Python + FastMCP gives us MCP tooling with the same ecosystem as Ollama's Python client, PyPDF2, and the eventual FastAPI backend.

**Alternatives considered**: Go (familiar for MCP), Node (JS fatigue). Python wins on roadmap alignment.

### Decision 2: Book files stored in knowledge-store/books/ (project-local)
Book PDFs live at `knowledge-store/books/<book>.pdf` — a project-local directory that is gitignored. The ingester accepts either an absolute path or a relative path from the project root. This keeps the workflow simple: drop a PDF in that folder, run `make ingest PDF=knowledge-store/books/my_book.pdf`.

**Alternatives considered**: `~/.lifekit/books/` (user home) — adds confusion for multi-project setups. Project-local is simpler for the MVP.

### Decision 3: SQLite with FTS5 over PostgreSQL or vector DB
MVP runs fully offline on developer hardware. SQLite requires zero setup, ships with Python, and FTS5 full-text search is adequate for a single book. The schema is designed so each table migrates cleanly to PostgreSQL later (no SQLite-specific types).

**Alternatives considered**: ChromaDB / FAISS for embeddings — adds a new dependency and complexity with no meaningful benefit for one book.

### Decision 4: FastMCP (stdio) over HTTP server
`fastmcp` gives us tool decoration (`@mcp.tool`) and automatic JSON schema generation. Stdio transport works directly with Claude Desktop and OpenWebUI without a running HTTP server or auth tokens. The MCP server can later be exposed over HTTP/SSE (one config flag in FastMCP).

**Alternatives considered**: Raw `mcp` SDK (more boilerplate), FastAPI + OpenAPI (heavier, not needed until Phase 1 REST layer).

### Decision 5: Ollama prompt (no RAG) for plan generation
For one book, the plan forge sends: book title + author + a 1000-token excerpt from the first few chapters + user intent string → Ollama `qwen3.6:latest`. The model returns a structured JSON plan. No retrieval pipeline needed yet.

**Alternatives considered**: Full RAG with embeddings — massive over-engineering for single book. Chunked FTS search into prompt is sufficient for MVP.

### Decision 6: File layout follows the roadmap module names
```
lifekit/
  db/          schema.py, migrations.py
  store/       pdf_ingester.py
  plan_forge/  forge_plan.py
  mcp/         server.py
```
This mirrors plan.md's module naming so Phase 1 additions drop in naturally.

## Risks / Trade-offs

- **Ollama model availability** → Mitigation: `.env.example` documents `OLLAMA_MODEL=qwen3.6:latest`; code falls back gracefully if model pull is needed. Run `ollama pull qwen3.6:latest` before first use.
- **PDF quality variance** → Mitigation: `pdf_ingester.py` strips headers/footers heuristically; user can inspect `books` table directly
- **Structured JSON from Ollama may hallucinate schema** → Mitigation: response validated against a Pydantic model; on parse failure, raw text is stored and surfaced as a single "read" task
- **SQLite write locking during MCP calls** → Not a concern for single-user stdio transport MVP
- **FTS5 search quality** → Acceptable for MVP; plan forge uses a fixed excerpt window, not search-driven retrieval

## Migration Plan

1. Run `make bootstrap` → creates `~/.lifekit/lifekit.db` and applies schema
2. Run `make ingest PDF=path/to/book.pdf` → chunks and indexes the book
3. Run `make forge INTENT="learn habit formation in 4 weeks"` → generates plan
4. Configure MCP client (Claude Desktop or OpenWebUI) to run `python -m lifekit.mcp.server`
5. Ask the LLM: "What should I work on today?" → tool calls `get_next_task`

No rollback required — all state is in `~/.lifekit/lifekit.db`; delete to reset.

## Open Questions

- Should `complete_task` accept a `notes` field now, or strictly boolean? (Recommendation: add `notes TEXT` to `sessions` now — cheap, useful immediately)
- Model config: hard-code `qwen3.6:latest` or read from `.env`? (Recommendation: env var with fallback default)
- Should the MCP server auto-run `ingest` on first launch if no books exist, or always require explicit CLI step? (Recommendation: explicit CLI — avoids surprises)
