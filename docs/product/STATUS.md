# LifeKit Status

> The quick-read companion to [`ROADMAP.md`](ROADMAP.md) (what's planned),
> [`ASSUMPTIONS.md`](ASSUMPTIONS.md) (what we believe), and
> [`BACKLOG.md`](BACKLOG.md) (what's broken). Whoever merges a change updates
> this file in the same commit.

## Current state

Stage 4 of 6 (dogfood & harden) — see [`.agents/intent.md`](../../.agents/intent.md)
for the stage table. The venue is shipped; now dogfooding the daily loop.

| Area | State |
|------|-------|
| Book pipeline (splitter → extraction → reduce → validation) | ✅ Shipped — 49/49 tests green |
| Coach tools (`list` / `get` / `log completion` / `next` + search, due, ideas, progress) | ✅ Shipped — `lifekit/mcp/server.py` (FastMCP stdio) |
| Multi-book registry | ✅ Shipped |
| FSRS scheduling | ✅ Shipped |
| LLM provider config (Ollama default + OpenRouter, `lifekit config` CLI) | ✅ Shipped — spec archived at `../../openspec/archives/llm-provider-config/` |
| Feed API (`lifekit.serve.server`, Flask, localhost `:8765`) | ✅ Shipped — briefing, completions, idea-signals, conversations CRUD, grounded chat. Chat was broken end-to-end (bad default model, dead FTS query, no chunk data, 30 s proxy timeout) — all four fixed 2026-09-27, see BACKLOG D8. |
| Feed UI (Next.js, `frontend/`) | ✅ Shipped — feed cards + conversation view, `/api/*` rewrites to feed API, `experimental.proxyTimeout` raised for slow local models |
| Dark theme | ✅ Shipped 2026-09-29 — theme tokens are `light-dark()` pairs, so the OS preference applies with no JS; a `ThemeToggle` in the feed and conversation headers pins the scheme per-app via `localStorage`, with a pre-paint script in `layout.tsx` to avoid a wrong-theme flash. Spec at `../../openspec/changes/dark-theme/`. |
| Sidebar layout shell | ✅ Shipped 2026-09-30 — left sidebar with icon strip (Feed/Journal/Chat) + collapsible panel (persisted to `localStorage`); feed renders in main area. Spec at `../../openspec/changes/sidebar-layout-shell/`. |
| Sidebar refinements | ✅ Shipped 2026-10-01 — collapse toggle moved from the bottom of the icon strip to the top-right of the panel (top of the icon strip when collapsed), using lucide `panel-left-open`/`panel-left-close` icons instead of arrows. `localStorage` persistence unchanged. |
| Settings tab | 📋 Placeholder 2026-10-01 — gear icon at the bottom of the icon strip, opens a "Coming soon." page like Journal/Chat. |
| Coach Markdown rendering | ✅ Shipped 2026-10-01 — coach replies render through `react-markdown` + `remark-gfm` (`MessageList.tsx`) styled by a hand-rolled `.lk-prose` in `globals.css`; the `_coach_reply` system prompt now asks for Markdown. User messages stay plain text — they are typed by the human and never interpreted. No `dangerouslySetInnerHTML`, so a reply containing `<script>` renders as visible text. Spec archived at `../../openspec/archives/chat-markdown-rendering/`. |
| Chat pending feedback | ✅ Shipped 2026-10-01 — `useConversation.sendMessage` appends the user message *before* the await, so pressing send shows your own message immediately instead of an input that clears itself over an unchanged screen for the length of a local 27B call. A dashed "Thinking…" status row sits in the transcript until the reply lands; the input placeholder explains the wait. A rejected POST rolls the optimistic message back off the transcript, which stays correct because the server still replies before it persists — that invariant did not move. Spec archived at `../../openspec/archives/chat-pending-feedback/`. |
| `lifekit ui` serve command | ✅ Shipped — boots feed API + Next.js production, localhost only. Always rebuilds the frontend (the old "skip if `.next` exists" guard served stale bundles and crashed on dev-only `.next`). |
| Full-book extraction eval (20-exercise ground truth) | ✅ Done — `qwen3.8:27b-q8_0` on home Ollama, 17/17 chapters, 156 records, recall 19/20 (95%), conditional pass. Results in `../../evals/step2-recall-qwen3.8-27b-q8_0/`. |
| DYL product ingest (dogfood data) | ✅ Done — `../../scripts/ingest_eval_book.py` → `~/.lifekit/lifekit.db` (book `dyl`): 144 exercises, 875 key ideas, validation 142/144 grounded, 0 hallucinations. |
| Known issues | See [`BACKLOG.md`](BACKLOG.md) (D3–D7, H3–H4, P2–P6 open) |
| Coaching / momentum / interviewer | 📋 Proposed, Steps 8–11 — program layer, not committed (see [`ROADMAP.md`](ROADMAP.md)) |
| Phone access (workstation) | 📋 Updating — `uv sync`, copy `dogfood/lifekit.db` → `~/.lifekit/lifekit.db`, then `lifekit ui` (builds the frontend automatically); phone opens the workstation's tailnet IP on port **3783**. Port moved off 3000 — the `hermes-gateway` systemd service holds 3000 and restarts if killed, so `lifekit ui` lost the bind race. |
| Book model proposal | 📋 Awaiting human review — [`../backend/BOOK_MODEL.md`](../backend/BOOK_MODEL.md) |
| Docs reorganization | ✅ Done — vision consolidated into [`.agents/intent.md`](../../.agents/intent.md); docs cleaned to be guidelines, not ledgers (historical accounts removed, cross-doc repetition eliminated) |

## Test inventory

Suite: **120 checks green** (82 + 37 feed API + 1 frontend hook regression); 1
pre-existing failure, `test_split_dyl_pdf` (hardcoded VM path, BACKLOG P2). Every
model call is stubbed/mocked — **zero tests exercise a real LLM**. The suite
proves the pipeline is *plumbed*, not that it *extracts*; the real-model eval is
the quality gate.

| Test file | Count | What it actually covers |
|-----------|-------|------------------------|
| `test_chapter_splitter` | 6 | TOC-first → heading-heuristic → fixed-size fallback order; image-only PDFs refused; chapters persistence idempotent. Builds synthetic PDFs with PyMuPDF; one test runs against the real *Designing Your Life* PDF (hardcodes a VM-absolute path — portability caveat, BACKLOG P2). Does NOT cover corrupt PDFs (raw `fitz.FileDataError` escapes). |
| `test_split_cli` | 1 | Split CLI end-to-end on a synthetic PDF. Does NOT surface the `book_id` it persists under. |
| `test_extractor` | 9 | Ollama `chat` with `format=<json_schema>`, temperature 0.1, 3-attempt Pydantic retry loop, `chapter_title` backfill, oversized-chapter section path via Chonkie `RecursiveChunker`. All via stub Ollama clients. Sections are **contiguous, not overlapping** (BACKLOG D4). |
| `test_reducer` | 7 | Deterministic dedupe (normalized-title keying, fuller record wins, ties keep first-seen); `dedupe_log` records every merge with a reason; re-runs don't duplicate rows. D1 regression: reduce → log completion + FSRS card → reduce again keeps identical IDs with downstream rows intact (FK enforced). |
| `test_validator` | 11 | Quote grounding is exact-substring (no fuzzy gaming); zero-extraction flag fires; judge sampling is seeded/deterministic. D2 regressions: validating without chapter text logs *skipped* (`passed` NULL), never failed; schema migration preserves old-format `validation_log` rows; CLI warns loudly when `--chapters` is omitted. |
| `test_coach` | 6 | Pure coach functions match spec: `list_exercises` pagination, `get_exercise` details, `log_completion`, `next_exercise` = first incomplete. NOT wired into `../../lifekit/mcp/server.py` (BACKLOG H1). |
| `test_multibook` | 4 | Registry idempotent with stable IDs; search isolates by book; cross-book grouping only when asked. Empty `book_ids` list still crashes (BACKLOG D5). |
| `test_scheduler` | 6 | Real `fsrs` library used properly (`Scheduler`, `review_card`, `Card` to/from dict, `Rating` map) — no hand-rolled math; card state persists as JSON; due list ordered; default rating Good per spec. `review_exercise` on a bad ID still writes orphans (BACKLOG D6). |
| `test_llm_config` | 9 | Provider/model resolution order (CLI flags > env vars > `~/.lifekit/config.json` > defaults); config never stores keys; invalid values rejected. |
| `test_llm_providers` | 6 | **Mocked transport, no network.** Ollama provider passes JSON schema + temperature 0.1; OpenRouter request shape (model, messages, Authorization header from env); missing key raises; factory defaults to Ollama; both satisfy the provider protocol. Does NOT prove a real API call succeeds. |
| `test_config_cli` | 5 | `lifekit config` get/set/show round-trips; secrets rejected from config file. |
| `test_useConversation` (frontend, `node --experimental-strip-types`) | 1 | Frontend hook regression: `useConversation` must not fetch while the route id is unresolved (it would hit the `/api/conversations/` collection, get an array, and crash `MessageList` on `messages.length`), and must expose a `messages` array for a real id. Drives the real hook with a React stub against the running `:3783` (override with `LIFEKIT_UI`). |
| `test_feed_api` | 37 | Feed API: schema migration (conversations/messages tables, idempotent), briefing endpoint, completions + idea-signals persistence, conversation CRUD, grounded chat message round-trip, localhost-only binding, `due_exercises` FSRS path. LLM provider mocked. Chat regressions (D8): provider failure returns a JSON 502 instead of an HTML 500 and leaves no orphan user message; FTS retrieval ranks by query and excludes other books; retrieval falls back to `chapters` when a book has no chunks; a punctuated natural-language query does not crash FTS5. |
