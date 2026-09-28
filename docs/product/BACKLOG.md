# LifeKit Known-Issues Backlog

Open defects, spec-vs-reality notes, and feature ideas for the extraction
pipeline and content model. IDs are stable — new findings append, never
renumber.

## Open defects

### D3 — Cross-chapter merged quotes can never validate — MEDIUM — OPEN
Dedupe merges a duplicate's `source_quote` into the kept exercise's
`extra_quotes`, but `validate_book` checks all quotes against the **kept**
chapter's text only. A quote merged from another chapter always fails as
"not verbatim", and it's unfixable from stored data: `dedupe_log` doesn't
record the quote's origin chapter. Ref: `../../lifekit/validate/validator.py`,
`../../lifekit/reduce/reducer.py` (dedupe_log insert).
Suggested disposition: add `merged_chapter_title` to `dedupe_log` and validate
extra quotes against their origin chapter text (Step 8 candidate).

### D4 — Spec says "overlapping sections"; implementation has none — LOW/MEDIUM — OPEN
The Step 2 proposal promises Chonkie `RecursiveChunker` *overlapping* sections
for oversized chapters; the installed chunker's constructor has no overlap
parameter, so sections are contiguous and an exercise spanning a boundary can be
missed or split. Ref: `../../openspec/archives/step-2-extraction-map/proposal.md`,
`../../lifekit/extract/extractor.py`.
Suggested disposition: implement manual overlap (e.g. 500-char sliding window)
or accept contiguous and note the deviation in A18.

### D5 — `search_exercises` crashes on an empty book-id list — LOW — OPEN
`search_exercises(db, q, book_ids=[])` builds `WHERE book_id IN ()` → SQLite
syntax error (`sqlite3.OperationalError`). Ref: `../../lifekit/books/search.py`
lines 26–35. Suggested disposition: return `[]` early when `book_ids` is empty;
add regression test.

### D6 — `review_exercise` on a nonexistent exercise creates orphan rows — LOW — OPEN
Unlike `log_completion`, `review_exercise` writes `fsrs_cards` + `completions`
rows for any integer id; `scheduler._conn()` never sets `PRAGMA foreign_keys =
ON` (per-connection pragma; `init_db`'s doesn't carry over), so no error is
raised. Ref: `../../lifekit/schedule/scheduler.py`.
Suggested disposition: verify the exercise exists (like `log_completion` does)
or enable the FK pragma on scheduler connections; add regression test.

### D7 — Step 3 proposal promised `page_start`/`page_end`; schema has neither — LOW — OPEN
Proposal describes the exercises table with `page_start, page_end`; implemented
schema has `chapter_idx`/`chapter_title` instead, never recorded as a
deviation. Ref: `../../openspec/archives/step-3-reduce-dedupe/proposal.md` line 14.
Suggested disposition: either add the columns (needs chapter→page mapping from
the splitter) or record the drift in `ASSUMPTIONS.md`. Matters if exercises ever
need to link back to pages.

### D8 — Chat was entirely broken end-to-end (model, retrieval, timeout) — HIGH — FIXED 2026-09-27
Sending any chat message returned `INTERNAL SERVER ERROR`. Four independent
defects stacked, each masking the next; all are fixed with regression tests
(`tests/test_feed_api.py::TestConversationMessages`).
1. **Default model does not exist.** `DEFAULT_OLLAMA_MODEL = "qwen3.6:latest"`
   (`lifekit/llm/config.py`) is not a real tag and was never installed; the
   provider's 404 propagated out of the route as an HTML 500 that the UI could
   only render as "INTERNAL SERVER ERROR". `.env.example` and every doc say
   `qwen3.8:27b-q8_0`. Local fix: `lifekit config set model qwen3.8:27b-q8_0`.
   **Still open:** the code default is unchanged — see D9.
2. **FTS retrieval never ran.** `_retrieve_passages` filtered on a `book_id`
   column that `book_chunks_fts` does not have (it indexes `content` only), so
   the query always raised and a blanket `except sqlite3.OperationalError`
   swallowed it, silently degrading to "first N chunks in insertion order" —
   the query was ignored entirely.
3. **No grounding data for the dogfood book.** `book_chunks` is empty for `dyl`
   (the eval ingest writes `chapters`, not chunks), so the coach had nothing
   and replied "I don't have any context from the book". Retrieval now falls
   back to the `chapters` text.
4. **Proxy timeout.** Next.js's rewrite proxy defaults to 30 s; a 27B local
   model needs 20–70 s per reply, so the proxy returned a bare 500. Set
   `experimental.proxyTimeout` in `frontend/next.config.ts`.

### D9 — Default model slug is still wrong — MEDIUM — OPEN
`DEFAULT_OLLAMA_MODEL` remains `qwen3.6:latest`, a tag that does not exist
anywhere; `.env.example`, `ASSUMPTIONS.md` A5/A21, and `ARCHITECTURE.md` all
say `qwen3.8:27b-q8_0`. Left unchanged here because the right default is a
product decision (which model, which machine, which hardware budget) and
`tests/test_llm_config.py` pins the current value. Ref: `lifekit/llm/config.py`
line 26. Suggested disposition: pick the default, update
`test_defaults_ollama` in the same commit.

### D10 — `book_chunks_fts` DELETE trigger is malformed — LOW — OPEN (blocked)
`book_chunks_ad` (schema creation) inserts `('delete', old.id)` into a
three-column FTS5 delete, but supplies only two values, so every
`DELETE FROM book_chunks` raises `OperationalError: 2 values for 3 columns`.
The obvious fix (`VALUES('delete', old.id, old.content)`) could not be
verified: this machine's SQLite (3.50.4 and 3.53.1) fails the FTS5 `delete`
command with "SQL logic error" even on a bare in-memory table, with or without
the content argument. Not fixed rather than shipping an unverified schema
migration. Ref: `lifekit/db/schema.py` line 46.
Suggested disposition: reproduce on a normal SQLite build, then fix the trigger
and add a `CREATE TRIGGER IF NOT EXISTS` migration to replace the broken
trigger on existing databases.

## Spec-vs-reality notes (honesty, not defects)

- **H3 — `validate_exercise` ignores `extra_quotes`.** The Step 4 proposal says
  it checks them; only the `validate_book` path does. The code comment admits
  it (`../../lifekit/validate/validator.py` line 26). Status: OPEN. Suggested
  disposition: align the proposal text with reality, or thread extra_quotes
  through `validate_exercise`.
- **H4 — `validation_log` duplicates on re-run.** `validate_book` appends on
  every run (it's a log — acceptable, but consumers should query latest).
  Ref: `../../lifekit/validate/validator.py`. Status: OPEN / accepted. Suggested
  disposition: document "query latest per (book_id, exercise_id, check_type)"
  in USER_MANUAL if it ever confuses anyone.

## Portability / hygiene

- **P2 — `test_split_dyl_pdf` hardcodes an absolute VM path**
  (`tests/test_chapter_splitter.py` line 23). Passes here, errors on any other
  machine — real-PDF coverage evaporates outside this VM. Status: OPEN.
  Suggested disposition: skip when the PDF is absent (`pytest.mark.skipif`
  on `Path.exists`), or read the path from an env var.
- **P3 — Dead no-op loop** (`for c in chapters: c.title = c.title`) in
  `../../lifekit/store/chapter_splitter.py` line 241. Status: OPEN. Suggested
  disposition: delete (trivial cleanup).
- **P4 — Two `EmptyPDFError` classes** (`../../lifekit/store/pdf_ingester.py:37`,
  `../../lifekit/store/chapter_splitter.py:27`). Status: OPEN. Suggested disposition:
  consolidate to one shared exception.
- **P5 — `book_id_for` hashes the raw path** (`../../lifekit/books/registry.py`
  lines 10–12): relative vs absolute paths to the same file produce different
  book ids. Status: OPEN. Suggested disposition: `Path.resolve()` before
  hashing.
- **P6 — LIKE wildcards unescaped** in `../../lifekit/books/search.py` lines 26, 35:
  a query containing `%`/`_` matches more than intended. Status: OPEN.
  Suggested disposition: escape wildcards in the query before binding.

## Content & extraction roadmap (post-dogfood)

Feature ideas for the extraction pipeline and content model, to be built only
after the core Today loop proves itself in dogfooding. Informed by a
2026-09-19 review of `virgiliojr94/book-to-skill`, filtered to the product
vision: LifeKit is an off-the-shelf app, not an agent skill/harness add-on —
borrow backend, UX, and how-to-content ideas only, never vision-changing ones.

- **F1 — Decision-rule extraction.** New extraction type: conditional guidance
  ("when *situation*, do *action*"), e.g. DYL's "when stuck → mind-map, talk
  to people, or prototype" or "when it's a gravity problem → accept or
  reframe". More situational than a key idea, lighter than an exercise; feeds
  the daily "one idea to remember" slot and situational chat answers
  ("I'm stuck on X" → matching rule).
- **F2 — Anti-patterns as first-class extraction.** Named mistakes with why to
  avoid them, e.g. DYL's dysfunctional beliefs ("my degree determines my
  career" → reframe). Guardrails complementing exercises; strong "one idea to
  remember" candidates and a natural chat answer type ("am I doing X wrong?").
- **F3 — Per-book glossary with chapter refs.** Named vocabulary per book
  (DYL: Grok, AEIOU, Odyssey Planning, failure immunity...). Powers the chat
  ("what does X mean?") and the revisit-lessons vertical.
- **F4 — "Preserve the author's precision" in Step 3 dedupe.** Explicit rule +
  test: never merge distinct named frameworks on normalized titles
  ("The 5 Whys" ≠ "ask why repeatedly"). Current dedupe merges only identical
  normalized titles, but the rule should be stated and locked before any
  near-dupe merging is attempted.
- **F5 — Analyze-only mode + pre-flight cost estimate.** Before a long eval
  extraction, run analysis only and report what was found plus estimated
  token/time cost, then ask to proceed. Would have saved real pain on the
  multi-hour Ollama evals.
- **F6 — Per-book content-type profile.** What to extract depends on the book:
  DYL yields exercises + dysfunctional beliefs, Atomic Habits would yield laws
  + habit stacks, Deep Work rules + rituals. An analyze pass detects which
  content types a book actually contains (from a small catalog); extraction
  runs only the relevant extractors; everything is stored with a `kind` field
  so Today/Chat/Library surface all kinds uniformly. (Subsumes F5's analyze
  pass — one analyze step serves both cost estimation and extraction config.)
- **F7 — Update/fold-in for companion sources.** Merge a related source (e.g.
  the DYL workbook) into an existing book record instead of treating every
  ingest as a fresh book.
- **F8 — Fail-fast PDF probing.** Check the PDF up front: detect scanned /
  image-only PDFs and stop immediately with a helpful message (what to
  install, or "run OCR first") instead of grinding through to produce garbage.
  Overlaps the open corrupt-PDF concerns (E1's extraction corruptions).

## Retrieval roadmap (from Tencent/WeKnora review, 2026-09-19)

WeKnora is Tencent's open-source RAG platform (hybrid retrieval + rerank,
ReAct agent mode, auto-generated wiki). Borrowed items below are the retrieval
core only — knowledge graph (already rejected in the landscape review),
multi-workspace RBAC (Step 0: single-user local), agent sandboxes/skill
catalog, IM channels, and Langfuse observability were deliberately excluded.

- **F9 — Hybrid search + rerank pipeline.** Chat retrieval today is SQLite
  FTS5 keyword-only. The proven shape (WeKnora and the broader RAG
  literature): dense + sparse retrieval → rerank → answer, with passage
  cleaning before the rerank step. This is the concrete design for the
  explicitly-later "RAG quality upgrade (semantic/hybrid search)" roadmap
  item — upgrade that line from a deferred question to this plan when the
  time comes.
- **F10 — Parent-child chunking.** Retrieve small chunks, expand to the parent
  section for answer context. Strictly better than today's contiguous Chonkie
  sections, and the natural fix for D4 (no overlap; exercises spanning a
  boundary get split or missed).
- **F11 — Adaptive chunking granularity.** Different chunking per content type
  (WeKnora's 3-tier adaptive chunking) instead of one chunker setting per
  book. Pairs with F6 per-book content profiles: a "rules" book chunks
  differently than a narrative one.
- **F12 — FAQ-shaped storage for rules/anti-patterns.** WeKnora keeps FAQ KBs
  alongside document KBs. F1 decision rules ("when X → do Y") and F2
  anti-patterns are FAQ-shaped; store them as such rather than forcing them
  into the exercise/key-idea schema.
- **F13 — Citation popovers in Chat.** Surface the existing quote grounding in
  the Chat UI: every answer shows which exercise/chapter it came from, tap to
  inspect the source. (WeKnora's v0.6.3 chat overhaul: citation popovers, RAG
  pipeline progress.)
- **F14 — Auto-tag extracted items by theme.** WeKnora auto-tags documents on
  ingest; tag exercises/ideas/rules by theme to give the Library filters and
  feed F6 content profiles.
- **F15 — Interlinked concept pages for the Library.** Auto-generated,
  interlinked pages per concept/exercise/term (WeKnora's Wiki mode *minus*
  the knowledge graph, which stays rejected) to make the Library vertical
  genuinely browsable post-dogfood.
