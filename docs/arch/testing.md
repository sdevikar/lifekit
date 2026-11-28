# Test map

How the test suite maps onto the code. The suite proves the pipeline is
*plumbed*, not that it *extracts* — the real-model eval (`qwen3.8:27b-q8_0` on
home Ollama, ≥90% recall) is the quality gate (results in `evals/`).

123 test functions (2026-11-27), 1 pre-existing failure (`test_split_dyl_pdf`, hardcoded VM path —
`KANBAN.md` P2). There is **no `conftest.py`**; tests skip gracefully when
fixtures are absent. Zero tests hit a real LLM — all model calls are
stubbed/mocked.

| Suite | Tests | Covers |
|-------|-------|--------|
| `test_chapter_splitter` | 6 | TOC-first → heading-heuristic → fixed-size fallback order; image-only PDFs refused; chapters persistence idempotent. Builds synthetic PDFs with PyMuPDF; one test runs against the real *Designing Your Life* PDF (hardcodes a VM-absolute path — portability caveat, `KANBAN.md` P2). Does NOT cover corrupt PDFs (raw `fitz.FileDataError` escapes). |
| `test_split_cli` | 1 | Split CLI end-to-end on a synthetic PDF. Does NOT surface the `book_id` it persists under. |
| `test_extractor` | 9 | Ollama `chat` with `format=<json_schema>`, temperature 0.1, 3-attempt Pydantic retry loop, `chapter_title` backfill, oversized-chapter section path via Chonkie `RecursiveChunker`. All via stub Ollama clients. Sections are **contiguous, not overlapping** (`KANBAN.md` D4). |
| `test_reducer` | 7 | Deterministic dedupe (normalized-title keying, fuller record wins, ties keep first-seen); `dedupe_log` records every merge with a reason; re-runs don't duplicate rows. D1 regression: reduce → log completion + FSRS card → reduce again keeps identical IDs with downstream rows intact (FK enforced). |
| `test_validator` | 18 | Quote grounding is exact-substring (no fuzzy gaming); zero-extraction flag fires; judge sampling is seeded/deterministic. D2 regressions: validating without chapter text logs *skipped* (`passed` NULL), never failed; schema migration preserves old-format `validation_log` rows; CLI warns loudly when `--chapters` is omitted. |
| `test_coach` | 6 | Pure coach functions match spec: `list_exercises` pagination, `get_exercise` details, `log_completion`, `next_exercise` = first incomplete. |
| `test_mcp_server` | 5 | The coach functions as registered MCP tools: list, natural-language search, get, complete + progress, due + key ideas. |
| `test_multibook` | 4 | Registry idempotent with stable IDs; search isolates by book; cross-book grouping only when asked. Empty `book_ids` list still crashes (`KANBAN.md` D5). |
| `test_scheduler` | 6 | Real `fsrs` library used properly (`Scheduler`, `review_card`, `Card` to/from dict, `Rating` map) — no hand-rolled math; card state persists as JSON; due list ordered; default rating Good per spec. `review_exercise` on a bad ID still writes orphans (`KANBAN.md` D6). |
| `test_llm_config` | 9 | Provider/model resolution order (CLI flags > env vars > `~/.lifekit/config.json` > defaults); config never stores keys; invalid values rejected. |
| `test_llm_providers` | 6 | **Mocked transport, no network.** Ollama provider passes JSON schema + temperature 0.1; OpenRouter request shape (model, messages, Authorization header from env); missing key raises; factory defaults to Ollama; both satisfy the provider protocol. Does NOT prove a real API call succeeds. |
| `test_config_cli` | 5 | `lifekit config` get/set/show round-trips; secrets rejected from config file. |
| `test_feed_api` | 13 | Feed API: schema migration (conversations/messages tables, idempotent), briefing endpoint, completions + idea-signals persistence, localhost-only binding. LLM provider mocked. |
