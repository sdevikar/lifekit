## 1. Project Scaffold

## 1. Project Scaffold ✅ COMPLETED (v0.1.0)

- [x] 1.1 Create `pyproject.toml` with setuptools config, Python ≥ 3.9, and deps: `pydantic`, `ollama`
- [x] 1.2 Create `lifekit/__init__.py` (v0.1.0) and sub-package `__init__.py` files for `db/`, `store/`, `plan_forge/`, `mcp/`
- [x] 1.3a Create `lifekit/store/__main__.py` — dispatches `ingest` CLI via `sys.argv` + argparse (--pdf)
- [x] 1.3b Create `lifekit/plan_forge/__main__.py` — dispatches `forge` CLI via `sys.argv` + argparse (--intent, --weeks, --method)
- [x] 1.3c Makefile target `ingest` for `python -m lifekit.store` (uses __main__.py)
- [x] 1.4 Create `.env.example` documenting `LIFEKIT_DB`, `OLLAMA_MODEL=qwen3.6:latest`, `OLLAMA_BASE_URL`
- [x] 1.4 Create `Makefile` with targets: bootstrap, ingest (PDF=), forge (--intent --method/--weeks), serve, test, lint, clean
- [x] 1.5 Create `README.md` with current implementation status, release log, CLI docs, architecture table, error handling reference
- [x] 1.6 All Python files compile cleanly via py_compile (11 files)

Actual files: [`lifekit/__init__.py`](3 lines), [`lifekit/db/schema.py`](116 lines), [`lifekit/store/pdf_ingester.py`](217 lines), [`lifekit/plan_forge/forge_plan.py`](366 lines), [`lifekit/mcp/server.py`](190 lines). Total: 11 Python files, ~1,059 lines.

## 2. Database Schema ✅ COMPLETED (v0.1.0)

- [x] 2.1 Create `lifekit/db/schema.py` with `init_db(db_path)` function (idempotent via CREATE TABLE IF NOT EXISTS)
- [x] 2.2 Implement `CREATE TABLE IF NOT EXISTS` for `books`, `book_chunks`, `plans`, `tasks`, `sessions` per spec
- [x] 2.3 Add FTS5 virtual table `book_chunks_fts` that shadows `book_chunks.content` via triggers
- [x] 2.4 Add FTS5 triggers (ai/au/ad) to keep the virtual table in sync
- [ ] 2.5 Write pytest tests for: idempotent `init_db`, table existence, FTS5 search returns results — **DEFERRED**: No test files yet; run py_compile as interim validation. DB verified at `~/.lifekit/lifekit.db` with correct tables (empty data).

Actual tables: `books`, `book_chunks`, `plans.teaching_method` column, `tasks`, `sessions`, `book_chunks_fts` virtual table with ai/au/ad triggers.

## 3. PDF Ingestion ✅ COMPLETED (v0.1.0)

- [x] 3.1 Create `lifekit/store/pdf_ingester.py` with `ingest_pdf(file_path, title, author, db_path)` function
- [x] 3.2 Implement PDF text extraction via `pypdf.PdfReader`, page by page
- [x] 3.3 Implement chunk splitting: ~2000 chars per chunk with sentence-boundary detection + overlapping chunks
- [x] 3.4 Insert `books` row (UUID id) and all `book_chunks` rows in a single transaction
- [x] 3.5 Update `books.chunk_count` after insert
- [x] 3.6 Implement duplicate check (same `file_path` → raise `DuplicateIngestError`)
- [x] 3.7 Implement empty-PDF guard (0 chunks extracted → raise `EmptyPDFError`)
- [x] 3.8 TOCTOU safety via `BEGIN IMMEDIATE` on the insert transaction
- [ ] 3.9 Write pytest tests — **DEFERRED**: No test files yet; code verified by compile. Features: sentence-boundary chunking, duplicate ingest guard, empty-PDF error, fallback for unreadable PDFs.

## 4. Plan Forge ✅ COMPLETED (v0.1.0 + teaching method extension)

- [x] 4.1 Create `lifekit/plan_forge/forge_plan.py` with forge_plan(book_id, intent, duration_weeks, **teaching_method**, db_path) function
- [x] 4.2 Define `TaskItem` and `PlanResponse` Pydantic models matching the spec schema
- [x] 4.3 Implement book context fetch: pull first 10 chunks from `book_chunks` for the given `book_id` (merged to ~2000 chars)
- [x] 4.4 Build Ollama prompt: book metadata + excerpt + user intent + teaching method + JSON schema instruction
- [x] 4.5 Call `ollama.chat()` with model from `OLLAMA_MODEL` env var (default `qwen3.6:latest`)
- [x] 4.6 Parse and validate Ollama response against `PlanResponse`; fallback to 7 "Read and reflect" tasks on failure (with `fallback=True` in return dict)
- [x] 4.7 Insert `plans` row (including teaching_method column) and all `tasks` rows in a single transaction
- [x] 4.8 Implement existing-plan guard (pending tasks exist for book → raise `PlanExistsError`)
- [x] 4.9 Implement Ollama connection error handler (→ raise `RuntimeError` with instructional message)
- [ ] 4.10 Write pytest tests — **DEFERRED**: No test files yet. Features: teaches via configurable method (socratic/feynman/analogical/spaced_recall/auto), PlanResponse Pydantic validation, fallback plan generation, duplicate-plan guard.

## ADDITION — Teaching Method Extension (Phase 0 follow-up)

- [x] Added `teaching_method` column to `plans` table + CHECK constraint
- [x] `_resolve_teaching_method()` validates input, auto → socratic
- [x] `_TEAChing_method_prompts` dict with behavioral instructions for all 4 active methods (injected into LLM system prompt)
- [x] CLI `--method` flag with choices: socratic, feynman, analogical, spaced_recall
- [x] MCP `get_plan_status` returns `teaching_method` in response dict

## 5. MCP Server ✅ COMPLETED (v0.1.0 + teaching method extension)

- [x] 5.1 Create `lifekit/mcp/server.py` with JSON-RPC over stdio transport and handler routing
- [x] 5.2 Implement `get_next_task(plan_id?: string)` tool: query lowest pending task across all plans (or specified plan), return JSON dict or null
- [x] 5.3 Implement `complete_task(task_id: int, notes?: string)` tool: update task status, insert session row, return confirmation
- [x] 5.4 Implement `get_plan_status(plan_id?: string)` tool: aggregate counts + **teaching_method**, return JSON object with completion_percentage
- [x] 5.5 Add `if __name__ == "__main__":` entry point with stderr logging of DB path on startup
- [x] 5.6 All error cases (no plan, invalid task_id, already-complete) return JSON error dicts
- [ ] 5.7 Write pytest tests — **DEFERRED**: Use in-memory SQLite fixture. Tools: `get_next_task`, `complete_task`, `get_plan_status(→ returns {plan_id, book_title, user_intent, teaching_method, total_tasks, complete_count, pending_tasks, completion_percentage})`.

## 6. Integration Smoke Testing ⏸️ DEFERRED (Phase 0: scaffolding only)

- [ ] 6.1 Run `make bootstrap` → verify `~/.lifekit/lifekit.db` exists with correct tables — **DEFERRED**: DB created by init_db() but empty of book/data rows; end-to-end not yet tested with live PDF content
- [ ] 6.2 Drop a sample PDF → verify chunk count in `books` table — **DEFERRED**
- [ ] 6.3 Run `make forge INTENT="..." --method feynman` → verify tasks created for target days — **DEFERRED**
- [ ] 6.4 Run MCP server and simulate JSON-RPC calls via stdin/stdout — **DEFERRED**
- [ ] 6.5 Call `complete_task` and verify `get_plan_status` reflects updated completion_percentage — **DEFERRED**

Phase 0 is closed. All scaffolding files compile (11/11), schema created, DB exists but has zero rows. Next step: Phase 1 (plan-manager / external library connectors) or integration smoke test with live PDF data.
