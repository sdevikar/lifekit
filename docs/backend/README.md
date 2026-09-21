# Backend

How LifeKit turns a book PDF into a coaching surface. Built in Steps 1–7 (all done); see [the roadmap](../product/ROADMAP.md).

## Pipeline

| Stage | Code | Step |
|-------|------|------|
| Chapter splitter (TOC-first, heuristic fallback) | `lifekit/` extract/split | 1 |
| Extraction map: per-chapter Ollama call → strict Pydantic schema (Exercise, KeyIdea) | `lifekit/` | 2 |
| Reduce/dedupe: merge chapter outputs, embedding-dedupe | `lifekit/` reduce | 3 |
| Validation harness: verbatim-quote grounding check, zero-extraction flags | `lifekit/` validate | 4 |
| Coach MCP tools: `list_exercises`, `get_exercise`, `log_completion`, `next_exercise` (+ `search_exercises`, `due_exercises`, `list_key_ideas`, `book_progress`) | `lifekit/mcp/server.py` (FastMCP stdio) | 5 |
| Multi-book registry, per-book pipelines, cross-book search | `lifekit/` | 6 |
| Scheduling: FSRS-style spaced repetition over completion history | `lifekit/` schedule | 7 |

Supporting dirs: `core/`, `knowledge-store/` (SQLite + FTS5), `evals/`, `scripts/`, `infra/`.

## Key docs

- [`BOOK_MODEL.md`](BOOK_MODEL.md) — the book-model proposal: structure tree + typed items + relations + quote grounding, minimal v1 SQLite schema (awaiting review)
- [`../product/ASSUMPTIONS.md`](../product/ASSUMPTIONS.md) — every consequential assumption with ID, status, and revisit trigger
- [`../product/BACKLOG.md`](../product/BACKLOG.md) — known defects and spec-vs-reality notes
- Model backends: pluggable via `lifekit.llm` — Ollama default, OpenRouter via env key only (spec archived: `../../openspec/archives/llm-provider-config/`)

## Constraints

Single user, local machine, Ollama running. Text-layer PDFs only (scanned PDFs are refused, never silently ingested). No auth, no cloud, no sync.
