# LifeKit Roadmap — live document

This file is the single source of truth for where the LifeKit build stands.
We work spec-first: each step below is one OpenSpec change under
`openspec/changes/<step-slug>/` (proposal → tasks → implement → archive).
Update the status column as steps move.
Assumptions are tracked separately in `ASSUMPTIONS.md` — check there before
challenging a design decision.

## Step 0 — Simplifying assumptions ✅ LOCKED (2026-09-14)

Locked. Not revisited during MVP.

- PDF only. No EPUB, audio, YouTube.
- Text-layer PDFs only — scanned/image PDFs are refused with a clear error, never silently ingested.
- **PDF quality assumption:** PDFs are well-formed and carry an embedded table of contents. The chapter splitter reads the TOC first and falls back to heuristics only when it's missing. Pathological PDFs (corrupt files, no TOC + undetectable headings, exotic layouts) are out of scope for MVP.
- English-language self-help books.
- Single user, local machine, Ollama running (`qwen3.6:latest` or configured model).
- Chapter-detectable books; fixed-size sections as fallback when detection fails.
- Extraction doesn't need to be perfect — misses are fine; systemic failures get flagged, not silently shipped.
- No frontend — CLI + MCP tools are the interface.
- No auth, no cloud, no sync.

## Build sequence

| Step | Feature | Status | OpenSpec change |
|------|---------|--------|-----------------|
| 0 | Simplifying assumptions | ✅ Locked | — |
| 1 | Chapter splitter (TOC-first, heuristic fallback) → `chapters` table | ✅ Done (2026-09-15) | `openspec/archives/step-1-chapter-splitter/` |
| 2 | Extraction map: per-chapter Ollama call → strict Pydantic schema (Exercise, KeyIdea) | ⬜ Queued | — |
| 3 | Reduce/dedupe: merge chapter outputs, embedding-dedupe exercises → `exercises`, `key_ideas` tables | ⬜ Queued | — |
| 4 | Validation harness: verbatim-quote grounding check, zero-extraction flags, 10% judge sample | ⬜ Queued | — |
| 5 | Coach MCP tools: `list_exercises`, `get_exercise`, `log_completion`, `next_exercise` | ⬜ Queued | — |
| 6 | Multi-book: registry, per-book pipelines, cross-book search | ⬜ Queued | — |
| 7 | Scheduling: FSRS-style spaced repetition over completion history | ⬜ Queued | — |

Each step ships with its test and done-criterion written before implementation.
Test one step at a time; don't start the next until the current one's done-criterion passes.

## Explicitly later (not MVP)

- RAG quality upgrade (semantic/hybrid search — deferred quality question)
- User interviewer
- Momentum decay engine
- Invite-to-coach UI
- EPUB / YouTube ingestion
- Agent Skills export

## Already shipped (Phase 0 / v0.1.0)

PDF ingestion (pypdf, sentence-boundary chunking, SQLite + FTS5) · Ollama SMART plan forge with Pydantic validation · MCP server (`get_next_task`, `complete_task`, `get_plan_status`). Archived spec: `openspec/archives/lifekit-mvp-core-loop/`.
