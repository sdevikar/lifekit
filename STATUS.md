# LifeKit Status — living document

> Update this file every time a change lands on `main` (new feature, defect
> fix, eval result). It is the quick-read companion to `ROADMAP.md` (what's
> planned), `ASSUMPTIONS.md` (what we believe), and `BACKLOG.md` (what's
> broken). Whoever merges a change updates this file in the same commit.

**Last updated:** 2026-09-15 — LLM provider config shipped (`d38f2c7`); suite
70/70; full-book eval unblocked, awaiting OpenRouter key.

## Current state

| Area | State |
|------|-------|
| MVP Steps 1–7 (splitter → extraction → reduce → validation → coach tools → multi-book → FSRS) | ✅ Done on `main`, 49/49 tests green |
| D1 (unstable exercise IDs on reduce re-run) | ✅ Fixed 2026-09-15 |
| D2 (validate without `--chapters` = 100% false failures) | ✅ Fixed 2026-09-15 |
| LLM provider config (Ollama default + OpenRouter, `lifekit config` CLI) | ✅ Shipped 2026-09-15 — spec archived at `openspec/archives/llm-provider-config/`, suite 70/70 |
| Full-book extraction eval vs 20-exercise ground truth | ▶️ Unblocked — awaiting OpenRouter API key; run `scripts/eval_step2_recall.py --provider openrouter --model <model>` |
| Known issues | See `BACKLOG.md` (D3–D7, H1–H4, P1–P6 open) |
| Coaching / momentum / interviewer / skills export | 📋 Planned, Steps 8–12 — see `workspace/self-help-exercises/lifekit-coaching-plan.md` |

## Test inventory — what the tests actually cover

Suite: **49 passed** (2026-09-15). Every model call is stubbed/mocked — **zero
tests exercise a real LLM**. The suite proves the pipeline is *plumbed*, not
that it *extracts*; the real-model eval is the quality gate.

| Test file | Count | What it actually covers |
|-----------|-------|-------------------------|
| `test_chapter_splitter` | 6 | TOC-first → heading-heuristic → fixed-size fallback order; image-only PDFs refused; chapters persistence idempotent. Builds synthetic PDFs with PyMuPDF; one test runs against the real *Designing Your Life* PDF (hardcodes a VM-absolute path — portability caveat, BACKLOG P2). Does NOT cover corrupt PDFs (raw `fitz.FileDataError` escapes). |
| `test_split_cli` | 1 | Split CLI end-to-end on a synthetic PDF. Does NOT surface the `book_id` it persists under. |
| `test_extractor` | 8 | Ollama `chat` with `format=<json_schema>`, temperature 0.1, 3-attempt Pydantic retry loop, `chapter_title` backfill, oversized-chapter section path via Chonkie `RecursiveChunker`. All via stub Ollama clients. Sections are **contiguous, not overlapping** (BACKLOG D4). |
| `test_reducer` | 7 | Deterministic dedupe (normalized-title keying, fuller record wins, ties keep first-seen); `dedupe_log` records every merge with a reason; re-runs don't duplicate rows. **D1 regression (new):** reduce → log completion + FSRS card → reduce again keeps identical IDs with downstream rows intact (FK enforced). |
| `test_validator` | 9 | Quote grounding is exact-substring (no fuzzy gaming); zero-extraction flag fires; judge sampling is seeded/deterministic. **D2 regressions (new):** validating without chapter text logs *skipped* (`passed` NULL), never failed; schema migration preserves old-format `validation_log` rows; CLI warns loudly when `--chapters` is omitted. |
| `test_coach` | 6 | Pure coach functions match spec: `list_exercises` pagination, `get_exercise` details, `log_completion`, `next_exercise` = first incomplete. NOT wired into `lifekit/mcp/server.py` (still legacy plans/tasks API — BACKLOG H1). |
| `test_multibook` | 4 | Registry idempotent with stable IDs; search isolates by book; cross-book grouping only when asked. Empty `book_ids` list still crashes (BACKLOG D5). |
| `test_scheduler` | 6 | Real `fsrs` library used properly (`Scheduler`, `review_card`, `Card` to/from dict, `Rating` map) — no hand-rolled math; card state persists as JSON; due list ordered; default rating Good per spec. `review_exercise` on a bad ID still writes orphans (BACKLOG D6). |

## Recent history

- **2026-09-15** — Steps 1–7 implemented spec-first (OpenSpec), pushed to `main`.
- **2026-09-15** — Independent code review: 45/45 green; found D1–D7; Step 2
  real-model criteria honestly deferred (A17/A20).
- **2026-09-15** — D1/D2 fixed + `BACKLOG.md` created (`59073b7`); suite now
  49/49.
- **2026-09-15** — Research: tutor-mcp landscape reviewed; coaching plan
  drafted (Steps 8–12 candidates).
- **2026-09-15** — LLM provider config shipped spec-first (proposal →
  implement → archive, commits `d38f2c7`/`c5bc8c9`/`f2e5dad`); eval script now
  portable (`--provider`/`--model`/`--results` flags, P1 fixed); suite 70/70.
