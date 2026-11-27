# LifeKit Kanban

The single living tracker for the product: what exists, what's in flight, what's
broken, what's next. Whoever merges a change updates this file in the same
commit. The binding vision is [`.agents/intent.md`](../../.agents/intent.md).
The stages and the reason for each decision are in [`ROADMAP.md`](ROADMAP.md).
The assumption log (IDs + revisit triggers) is
[`ASSUMPTIONS.md`](ASSUMPTIONS.md).

## How to use this file

| Section | Put here |
|---------|----------|
| Current state | The capability view — one row per area, its status today (shipped / placeholder / proposed). No history. |
| Now / In progress | Work actively being done this cycle. |
| Upcoming | Approved or awaiting-approval proposals, ordered by dependency then value. |
| Superseded | Old proposals that the v1 slices replace. |
| Deferred / Future | Known but not scheduled. Parked stage items live in `ROADMAP.md`. |
| Known issues | Defects and spec-vs-reality notes, stable IDs (`D…`, `H…`, `P…`). |
| Future ideas | Unapproved feature ideas (`F…`). |
| Done | Shipped slices, newest first, with the archive link. |
| Open questions | Undecided design questions. |
| Locked assumptions | Step 0 canonical text (also summarised in `ASSUMPTIONS.md`). |

The human approves; Atlas never self-approves. Nothing is silently dropped —
retired items move to their section with a reason and date.

## Current state

Stage **v1** (`ROADMAP.md`): one book as a feed of cards, with a comment
thread under each card, coach replies, and reactions. The table below shows
what exists today, before any v1 slice lands. The feed is not useful yet: it
shows the same front-matter ideas every day, 875 ideas is too many, and the
exercises contain duplicates (see the v1 problem statement under Upcoming).
Slice 0 (`feed-only-ui`) removes the chat, the sidebar, and the journal
placeholder.

| Area | State |
|------|-------|
| Book pipeline (splitter → extraction → reduce → validation) | ✅ Shipped — 49/49 tests green |
| Coach tools (`list` / `get` / `log completion` / `next` + search, due, ideas, progress) | ✅ Shipped in `lifekit/coach.py`; not yet wired into `lifekit/mcp/server.py` (H1) |
| Multi-book registry | ✅ Shipped |
| FSRS scheduling | ✅ Shipped |
| LLM provider config (Ollama default + OpenRouter, `lifekit config` CLI) | ✅ Shipped |
| Feed API (`lifekit.serve.server`, Flask, localhost `:8765`) | ✅ Shipped — briefing, completions, idea-signals, conversations CRUD, grounded chat |
| Feed UI (Next.js, `frontend/`) | ✅ Shipped — feed cards + conversation view, `/api/*` rewrites, `experimental.proxyTimeout` raised for slow local models |
| Dark theme | ✅ Shipped 2026-09-29 — `light-dark()` tokens, `ThemeToggle`, pre-paint script |
| Sidebar (shell + refinements + nav model) | ✅ Shipped — single column, icon strip + panel, Chat/Journal destination rows, `localStorage` persistence |
| UI design language overhaul | ✅ Shipped 2026-09-30 — every component on the `--lk-*` tokens, no colour literals |
| Chat Surface | ✅ Shipped 2026-10-15 — `/chat` single-column, sidebar "Recent" (rename/delete), no new-chat button (start by typing), deep links, coach replies rendered as Markdown |
| Chat pending feedback | ✅ Shipped 2026-10-01 — optimistic user message + dashed "Thinking…" row |
| Chat placeholder title | ✅ Shipped 2026-10-15 — sentinel "New conversation", replaced by the first 60 chars of the first user message |
| Journal Surface | 📋 Placeholder — `/journal` route only; functionality pending the journal slices |
| Settings tab | 📋 Placeholder — gear row opens a "Coming soon." page |
| `lifekit ui` serve command | ✅ Shipped — boots feed API + Next.js production, localhost only; always rebuilds the frontend |
| Full-book extraction eval (20-exercise ground truth) | ✅ Done — `qwen3.8:27b-q8_0` on home Ollama, 17/17 chapters, recall 19/20 (95%), conditional pass; `evals/step2-recall-qwen3.8-27b-q8_0/` |
| DYL product ingest (dogfood data) | ✅ Done — book `dyl`: 144 exercises, 875 key ideas, 142/144 grounded, 0 hallucinations |
| Phone access (workstation) | 📋 Updating — `uv sync`, copy `dogfood/lifekit.db` → `~/.lifekit/lifekit.db`, then `lifekit ui`; phone opens the workstation's tailnet IP on port **3783** |
| Test suite | ✅ 117 tests, 1 pre-existing fail (`test_split_dyl_pdf`); see [`../arch/testing.md`](../arch/testing.md) |

## Now / In progress

The intent rewrite, `ROADMAP.md`, and the seven v1 proposals (slices 0–6) are
merged to `main` as drafts. They wait for the human's approval. Slice 0 comes
first.

## Upcoming

### v1 — card feed for one book

**Problem.** The dogfood feed for `dyl` is not useful:

- `_resurfaced_idea` and `_fading_ideas` select `ORDER BY id LIMIT …`, so the
  feed always shows the Dedication and Contents ideas.
- Front matter and back matter are extracted like chapters (Dedication 3
  ideas, Contents 2, Notes 12, Acknowledgments 10).
- 875 key ideas and 144 exercises exist for one book. Many exercises repeat
  (Odyssey Plans about 8 times, Good Time Journal about 10 times), because
  sectioned extraction (A22) splits a chapter into 3000-char sections and
  dedupe compares titles only.
- Some "exercises" come from anecdotes, not from instructions.

**v1 goal.** One book. Every card in the feed is useful and has a type. The
user responds to a card with a comment or a reaction. The coach replies to
every comment. The reasons are in `ROADMAP.md` (D1–D15).

Build order. Each slice can be tested on its own:

| # | Slice | Proposal | Depends on | Status |
|---|-------|----------|------------|--------|
| 0 | Feed-only UI: remove the sidebar, the chat pages, the journal page, and the free-chat API | `feed-only-ui/` | — | Proposed (do first) |
| 1 | Card types: five types, their fields, the comment hint and coach instruction per type | `card-types-v1/` | 0 | Proposed |
| 2 | Book model: PDF and EPUB become sections (front, body, back) and passages with offsets; `lifekit ingest` | `book-model-v1/` | 0 | Proposed |
| 3 | Item extraction: typed items with stance, per-chapter consolidation, passage anchors, usefulness check, golden set | `item-extraction-v2/` | 1, 2 | Proposed |
| 4 | Card generation: one card per item; code builds the OpenUI program; stable ids; question cards | `card-generation/` | 1, 3 | Proposed |
| 5 | Feed: cards in reading order, like and dislike, start where you left off | `feed-v1/` | 4 | Proposed |
| 6 | Card comments: a thread per card, a coach reply to every comment, reactions on replies | `card-comments/` | 5 | Proposed |

Slice 0 comes first. Slices 1 and 2 can then run in parallel. From slice 0
until slice 6, the app has no way to talk to the coach.

## Superseded

The v1 slices replace these proposals. The folders stay for history. Do not
apply them.

| Proposal | Replaced by | Reason |
|----------|-------------|--------|
| `exercise-type-system/` | `card-types-v1/` | Typed cards cover exercises and ideas together. OpenUI replaces A2UI. |
| `exercise-surface-routing/` | `feed-v1/` | One screen, the feed (ROADMAP D1). |
| `exercise-surface-journal/`, `exercise-surface-tracking/`, `exercise-surface-questionnaire/`, `exercise-surface-concept-check/`, `exercise-surface-worksheet/` | `card-comments/` | A comment is the only way to act on a card (ROADMAP D2). Worksheet waits for v2 (D7). |
| `openui-exercise-surfaces/` | `card-generation/` | No per-type surfaces. Code builds card programs offline (D6). |
| `openui-hybrid-chat/`, `openui-system-prompt/` | `card-comments/`, `feed-only-ui/` | Shipped in part (commit `6c61732`). Coach replies keep the OpenUI renderer; the free chat goes away (D10). |
| `chat-surface/`, `chat-surface-b-composer-open/`, `chat-surface-c-entry-points/` | `feed-only-ui/` | Free chat is retired (D10). |
| `journal-tab/`, `journal-tab-a-storage-api/`, `journal-tab-b-editor/`, `journal-tab-c-toc-navigation/`, `journal-tile-layout/` | `card-comments/` | A journal entry is a comment on a reflect card (D2). Posts without a card are v2 (D13). |
| `combine-product-tracking-docs/` | — | Done: KANBAN is the one tracker. `ROADMAP.md` now holds stages and decision reasons only. |
| `card-activity-drawer/` (renamed) | `card-comments/` | The drawer is dropped (D1). |
| `card-associated-activity/`, `card-discovery/` (on `feat/card-first-feed`) | `feed-v1/`, `card-comments/` | The branch is abandoned, not merged. |

## Deferred / Future

Stage items that wait for dogfood (spaced repetition, search, memory, multi-book,
the program layer `step-8…step-11`, and more) are in `ROADMAP.md` → Parked.

| Item | Reason |
|------|--------|
| Books tab | Single-book dogfood, no switching need yet. Add when book #2 exists. |

## Known issues

Defects and spec-vs-reality notes, with stable IDs. Nothing here is closed
silently — a fixed item keeps its row and gets a date.

### Defects

- **D3 — Cross-chapter merged quotes can never validate — MEDIUM — OPEN.**
  Dedupe merges a duplicate's `source_quote` into the kept exercise's
  `extra_quotes`, but `validate_book` checks all quotes against the **kept**
  chapter's text only. A quote merged from another chapter always fails as
  "not verbatim", and it's unfixable from stored data: `dedupe_log` doesn't
  record the quote's origin chapter. Ref: `lifekit/validate/validator.py`,
  `lifekit/reduce/reducer.py` (dedupe_log insert). Suggested disposition: add
  `merged_chapter_title` to `dedupe_log` and validate extra quotes against their
  origin chapter text (Step 8 candidate).
- **D4 — Spec says "overlapping sections"; implementation has none — LOW/MEDIUM — OPEN.**
  The Step 2 proposal promises Chonkie `RecursiveChunker` *overlapping* sections
  for oversized chapters; the installed chunker's constructor has no overlap
  parameter, so sections are contiguous and an exercise spanning a boundary can
  be missed or split. Ref: `openspec/archives/step-2-extraction-map/proposal.md`,
  `lifekit/extract/extractor.py`. Suggested disposition: implement manual overlap
  (e.g. 500-char sliding window) or accept contiguous and note the deviation in
  `ASSUMPTIONS.md` A18.
- **D5 — `search_exercises` crashes on an empty book-id list — LOW — OPEN.**
  `search_exercises(db, q, book_ids=[])` builds `WHERE book_id IN ()` → SQLite
  syntax error (`sqlite3.OperationalError`). Ref: `lifekit/books/search.py`
  lines 26–35. Suggested disposition: return `[]` early when `book_ids` is
  empty; add a regression test.
- **D6 — `review_exercise` on a nonexistent exercise creates orphan rows — LOW — OPEN.**
  Unlike `log_completion`, `review_exercise` writes `fsrs_cards` + `completions`
  rows for any integer id; `scheduler._conn()` never sets `PRAGMA foreign_keys =
  ON` (per-connection pragma; `init_db`'s doesn't carry over), so no error is
  raised. Ref: `lifekit/schedule/scheduler.py`. Suggested disposition: verify
  the exercise exists (like `log_completion` does) or enable the FK pragma on
  scheduler connections; add regression test.
- **D7 — Step 3 proposal promised `page_start`/`page_end`; schema has neither — LOW — OPEN.**
  The proposal describes the exercises table with `page_start, page_end`; the
  implemented schema has `chapter_idx`/`chapter_title` instead, never recorded
  as a deviation. Ref: `openspec/archives/step-3-reduce-dedupe/proposal.md` line
  14. Suggested disposition: either add the columns (needs a chapter→page
  mapping from the splitter) or record the drift in `ASSUMPTIONS.md`. Matters if
  exercises ever need to link back to pages.
- **D8 — Chat was entirely broken end-to-end (model, retrieval, timeout) — HIGH — FIXED 2026-09-27.**
  Sending any chat message returned `INTERNAL SERVER ERROR`. Four independent
  defects stacked, each masking the next; all fixed with regression tests
  (`tests/test_feed_api.py::TestConversationMessages`).
  1. Default model did not exist (`qwen3.6:latest`) — the provider's 404
     propagated as an HTML 500. Local fix: `lifekit config set model
     qwen3.8:27b-q8_0`. Code default unchanged — see D9.
  2. FTS retrieval never ran — `_retrieve_passages` filtered on a `book_id`
     column `book_chunks_fts` doesn't have; a blanket `except
     sqlite3.OperationalError` swallowed it, silently degrading to "first N
     chunks in insertion order".
  3. No grounding data for the dogfood book — `book_chunks` is empty for `dyl`;
     retrieval now falls back to the `chapters` text.
  4. Proxy timeout — Next.js's rewrite proxy defaulted to 30 s; set
     `experimental.proxyTimeout` in `frontend/next.config.ts`.
- **D9 — Default model slug is still wrong — MEDIUM — OPEN.**
  `DEFAULT_OLLAMA_MODEL` remains `qwen3.6:latest`, a tag that does not exist
  anywhere; `.env.example` says `qwen3.8:27b-q8_0` (the model actually used for
  the eval), and `ASSUMPTIONS.md` A5/A21 repeat `qwen3.6:latest`. Left unchanged
  because the right default is a product decision (which model, which machine,
  which hardware budget) and `tests/test_llm_config.py` pins the current value.
  Ref: `lifekit/llm/config.py` line 26. Suggested disposition: pick the default,
  update `test_defaults_ollama` and A5/A21 in the same commit.
- **D10 — `book_chunks_fts` DELETE trigger is malformed — LOW — OPEN (blocked).**
  `book_chunks_ad` inserts `('delete', old.id)` into a three-column FTS5 delete,
  supplying only two values, so every `DELETE FROM book_chunks` raises
  `OperationalError: 2 values for 3 columns`. The obvious fix
  (`VALUES('delete', old.id, old.content)`) could not be verified: this
  machine's SQLite (3.50.4 / 3.53.1) fails the FTS5 `delete` command with "SQL
  logic error" even on a bare in-memory table. Not fixed rather than shipping an
  unverified migration. Ref: `lifekit/db/schema.py` line 46. Suggested
  disposition: reproduce on a normal SQLite build, then fix the trigger and add
  a `CREATE TRIGGER IF NOT EXISTS` migration.

### Spec-vs-reality notes (honesty, not defects)

- **H1 — Coach functions are not exposed via MCP — OPEN.** `lifekit/coach.py`
  implements `list_exercises`, `get_exercise`, `log_completion`, `next_exercise`
  (and search/due/ideas/progress) and `tests/test_coach.py` covers them, but
  `lifekit/mcp/server.py` does not register the tools. Resolved by Step 8 task
  8.4. Ref: `lifekit/mcp/server.py`, `../arch/testing.md`.
- **H3 — `validate_exercise` ignores `extra_quotes`.** The Step 4 proposal says
  it checks them; only the `validate_book` path does. The code comment admits it
  (`lifekit/validate/validator.py` line 26). Status: OPEN. Suggested
  disposition: align the proposal text with reality, or thread `extra_quotes`
  through `validate_exercise`.
- **H4 — `validation_log` duplicates on re-run.** `validate_book` appends on
  every run (it's a log — acceptable, but consumers should query the latest).
  Ref: `lifekit/validate/validator.py`. Status: OPEN / accepted. Suggested
  disposition: document "query latest per (book_id, exercise_id, check_type)"
  if it ever confuses anyone.

*Reconciled 2026-10-15:* `H2` and `P1` appeared in an older ROADMAP summary but
were never defined anywhere; dropped. `H1` was referenced (STATUS, Step 8) but
never defined in BACKLOG — written up above. D9's claim that A5/A21 said
`qwen3.8:27b-q8_0` was wrong (they say `qwen3.6:latest`) and is corrected here.

### Portability / hygiene

- **P2 — `test_split_dyl_pdf` hardcodes an absolute VM path**
  (`tests/test_chapter_splitter.py` line 23). Passes here, errors on any other
  machine — real-PDF coverage evaporates outside this VM. Status: OPEN.
  Suggested disposition: `Path.resolve()`/skip when absent, or read the path
  from an env var.
- **P3 — Dead no-op loop** (`for c in chapters: c.title = c.title`) in
  `lifekit/store/chapter_splitter.py` line 241. Status: OPEN. Suggested
  disposition: delete (trivial cleanup).
- **P4 — Two `EmptyPDFError` classes** (`lifekit/store/pdf_ingester.py:37`,
  `lifekit/store/chapter_splitter.py:27`). Status: OPEN. Suggested disposition:
  consolidate to one shared exception.
- **P5 — `book_id_for` hashes the raw path** (`lifekit/books/registry.py` lines
  10–12): relative vs absolute paths to the same file produce different book
  ids. Status: OPEN. Suggested disposition: `Path.resolve()` before hashing.
- **P6 — LIKE wildcards unescaped** in `lifekit/books/search.py` lines 26, 35: a
  query containing `%`/`_` matches more than intended. Status: OPEN. Suggested
  disposition: escape wildcards in the query before binding.

## Future ideas

Feature ideas for the extraction pipeline and content model, to build only
after the core Today loop proves itself in dogfooding. Informed by a 2026-09-19
review of `virgiliojr94/book-to-skill`, filtered to the product vision: LifeKit
is an off-the-shelf app, not an agent skill/harness add-on — borrow backend, UX,
and how-to-content ideas only, never vision-changing ones.

- **F1 — Decision-rule extraction.** New extraction type: conditional guidance
  ("when *situation*, do *action*"), e.g. DYL's "when stuck → mind-map, talk to
  people, or prototype". More situational than a key idea, lighter than an
  exercise; feeds the daily "one idea to remember" slot and situational chat
  answers.
- **F2 — Anti-patterns as first-class extraction.** Named mistakes with why to
  avoid them, e.g. DYL's dysfunctional beliefs. Guardrails complementing
  exercises; strong "one idea to remember" candidates.
- **F3 — Per-book glossary with chapter refs.** Named vocabulary per book (DYL:
  Grok, AEIOU, Odyssey Planning...). Powers chat ("what does X mean?") and the
  revisit-lessons vertical.
- **F4 — "Preserve the author's precision" in Step 3 dedupe.** Explicit rule +
  test: never merge distinct named frameworks on normalized titles ("The 5 Whys"
  ≠ "ask why repeatedly").
- **F5 — Analyze-only mode + pre-flight cost estimate.** Before a long eval
  extraction, run analysis only and report what was found plus estimated
  token/time cost, then ask to proceed.
- **F6 — Per-book content-type profile.** An analyze pass detects which content
  types a book actually contains; extraction runs only the relevant extractors;
  everything is stored with a `kind` field so Today/Chat/Library surface all
  kinds uniformly. (Subsumes F5's analyze pass.)
- **F7 — Update/fold-in for companion sources.** Merge a related source (e.g.
  the DYL workbook) into an existing book record instead of a fresh ingest.
- **F8 — Fail-fast PDF probing.** Detect scanned / image-only PDFs up front and
  stop with a helpful message (what to install, or "run OCR first").
- **F9 — Hybrid search + rerank pipeline.** Chat retrieval today is SQLite FTS5
  keyword-only. The proven shape: dense + sparse retrieval → rerank → answer,
  with passage cleaning before rerank. The concrete "RAG quality upgrade".
- **F10 — Parent-child chunking.** Retrieve small chunks, expand to the parent
  section for answer context. Strictly better than today's contiguous sections;
  the natural fix for D4.
- **F11 — Adaptive chunking granularity.** Different chunking per content type
  instead of one setting per book. Pairs with F6.
- **F12 — FAQ-shaped storage for rules/anti-patterns.** F1/F2 items are
  FAQ-shaped; store them as such rather than forcing them into the
  exercise/key-idea schema.
- **F13 — Citation popovers in Chat.** Surface quote grounding in the Chat UI:
  every answer shows which exercise/chapter it came from, tap to inspect.
- **F14 — Auto-tag extracted items by theme.** Tag exercises/ideas/rules by
  theme to give the Library filters and feed F6 content profiles.
- **F15 — Interlinked concept pages for the Library.** Auto-generated,
  interlinked pages per concept/exercise/term (WeKnora's Wiki mode *minus* the
  knowledge graph, which stays rejected).

Retrieval-roadmap items F9–F15 borrow the retrieval core only from
Tencent/WeKnora; its knowledge graph, multi-workspace RBAC, agent sandboxes, IM
channels, and Langfuse observability were deliberately excluded.

## Done

| Slice | Shipped | Notes |
|-------|---------|-------|
| Chat token streaming (SSE) | 2026-11-22 | Commit `072297a`. card-comments reuses the SSE events. |
| Chat layout — DeepTutor-style single-column + sidebar Recent | 2026-10-15 | `/chat` single-column, sidebar collapsible "Recent" with recency grouping, rename/delete, "New chat"; `/chat/<id>` deep links, `/c/<id>` redirects. Fixed `TabContext` route sync. Spec archived at `../../openspec/archives/chat-layout-deeptutor-recent/`. |
| Chat placeholder title | 2026-10-15 | Sentinel "New conversation"; replaced by the first 60 chars of the first user message (once). Spec at `../../openspec/changes/chat-placeholder-title/`. |
| Chat Surface **b** — open conversation + composer | 2026-10-07 | `ChatView` composes `MessageList` + `ChatInput` + title header; `MasterComposer` → `POST /api/conversations`. |
| Journal Surface — `/journal` route | 2026-10-07 | Placeholder page; sidebar row navigates via `router.push`. |
| Chat Surface **a** — `/chat` route + conversation list | 2026-10-07 | `useConversations` fetches `GET /api/conversations`; `ConversationsList` repurposed. |
| Chat markdown rendering | 2026-10-01 | `react-markdown` + `remark-gfm`; hand-rolled `.lk-prose`; prompt asks for Markdown. Spec archived at `../../openspec/archives/chat-markdown-rendering/`. |
| Chat pending feedback | 2026-10-01 | Optimistic user message + dashed "Thinking…" row; server replies before persisting. Spec archived at `../../openspec/archives/chat-pending-feedback/`. |
| Sidebar nav model | 2026-10-01 | Two columns → one; `IconTab` → `NavRow`. Spec archived at `../../openspec/archives/sidebar-nav-model/`. |
| Settings icon + lucide panel icons | 2026-10-01 | Gear tab at strip bottom; collapse/expand via `panel-left-open`/`panel-left-close`. |
| Sidebar refinements | 2026-10-01 | Collapse toggle moved to the panel's top-right. Spec archived at `../../openspec/archives/sidebar-refinements/`. |
| UI design language overhaul | 2026-09-30 | Every component on the `--lk-*` tokens; zero colour literals. Spec archived at `../../openspec/archives/ui-design-language-overhaul/`. |
| Sidebar layout shell | 2026-09-30 | Icon strip (Feed/Journal/Chat) + collapsible panel. Spec archived at `../../openspec/archives/sidebar-layout-shell/`. |
| Dark theme | 2026-09-29 | `light-dark()` tokens; `ThemeToggle` pins the scheme per-app. Spec archived at `../../openspec/archives/dark-theme/`. |
| Step 13 — UI: feed + conversations (4 slices) | 2026-09-24 | 13a feed API, 13b feed screen, 13c conversation view, 13d serve command. `lifekit ui` boots both. Archived at `../../openspec/archives/step-13-ui-feed-conversations/`. |
| Steps 1–7 — pipeline, coach tools, multi-book, scheduling | 2026-09-15 | Chapter splitter → extraction → reduce → validation harness; coach MCP tools; multi-book registry; FSRS-style scheduling. Archived under `../../openspec/archives/step-1…step-7*/`. |

**Design decisions (2026-10-07).** Chat is a *destination*, not a tab: the
sidebar Chat row navigates to `/chat`, a single-column surface with the
conversation (or composer) full-width; conversations live in a collapsible
"Recent" section; no `+` button — starting a chat means typing in the composer.
Journal follows the same pattern (`/journal`).

## Open questions

1. Learning runtime: evolve `lifekit/mcp/server.py` in place, or a second server
   beside it? (Parked with the program layer.)
2. Dogfood exit check (`ROADMAP.md` → Dogfood exit check). Proposed, needs the
   human's approval: use the feed on at least 10 of 14 days; at most 20% of
   reacted cards disliked; at most 20% of coach replies disliked.
3. Usefulness precision target for item extraction v2. Proposed: at least 80%
   of cards in the golden set labelled useful by the human
   (`item-extraction-v2/`).

## Locked assumptions

Step 0 (locked 2026-09-14) — canonical text. One-liners with IDs live in
[`ASSUMPTIONS.md`](ASSUMPTIONS.md).

- PDF and EPUB (EPUB added 2026-11-27 by `book-model-v1` — same PyMuPDF splitter).
  No audio, YouTube.
- Text-layer PDFs only: scanned/image PDFs refused with a clear error, never
  silently ingested.
- PDFs are well-formed with an embedded TOC; the splitter reads the TOC first,
  heuristics only as fallback. Pathological PDFs (corrupt files, no TOC +
  undetectable headings, exotic layouts) are out of scope for MVP.
- English-language self-help books.
- Single user, local machine, Ollama running (configured model; see D9).
- Books are chapter-detectable; fixed-size sections as fallback.
- Extraction need not be perfect — misses are fine; systemic failures get
  flagged, not silently shipped.
- No auth, no cloud, no sync.
