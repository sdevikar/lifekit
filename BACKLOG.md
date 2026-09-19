# LifeKit Known-Issues Backlog

Issues found in the 2026-09-15 code review of Steps 1–7. D1 and D2 were fixed
the same day (see commit history); everything below is **open** unless noted.
IDs are stable — new findings append, never renumber.

## Fixed (record)

- **D1 (HIGH)** — reducer re-ran delete+reinsert, changing exercise ids → fixed
  2026-09-15 by upserting on `UNIQUE(book_id, title)` (`lifekit/reduce/reducer.py`).
- **D2 (MEDIUM)** — validate without `--chapters` logged 100% false failures →
  fixed 2026-09-15: quote checks are logged as *skipped* (`validation_log.passed`
  NULL, schema migrated) and the CLI warns loudly (`lifekit/validate/`).
- **P1 (MEDIUM)** — `scripts/eval_step2_recall.py` hardcoded sandbox paths →
  fixed 2026-09-15: `--provider`/`--model`/`--results` flags added; the
  2026-09-17 full-book eval ran portably against home Ollama.

## Open defects

### D3 — Cross-chapter merged quotes can never validate — MEDIUM — OPEN
Dedupe merges a duplicate's `source_quote` into the kept exercise's
`extra_quotes`, but `validate_book` checks all quotes against the **kept**
chapter's text only. A quote merged from another chapter always fails as
"not verbatim", and it's unfixable from stored data: `dedupe_log` doesn't
record the quote's origin chapter. Ref: `lifekit/validate/validator.py`,
`lifekit/reduce/reducer.py` (dedupe_log insert).
Suggested disposition: add `merged_chapter_title` to `dedupe_log` and validate
extra quotes against their origin chapter text (Step 8 candidate).

### D4 — Spec says "overlapping sections"; implementation has none — LOW/MEDIUM — OPEN
The Step 2 proposal promises Chonkie `RecursiveChunker` *overlapping* sections
for oversized chapters; the installed chunker's constructor has no overlap
parameter, so sections are contiguous and an exercise spanning a boundary can be
missed or split. Ref: `openspec/archives/step-2-extraction-map/proposal.md`,
`lifekit/extract/extractor.py`.
Suggested disposition: implement manual overlap (e.g. 500-char sliding window)
or accept contiguous and note the deviation in A18.

### D5 — `search_exercises` crashes on an empty book-id list — LOW — OPEN
`search_exercises(db, q, book_ids=[])` builds `WHERE book_id IN ()` → SQLite
syntax error (`sqlite3.OperationalError`). Ref: `lifekit/books/search.py`
lines 26–35. Suggested disposition: return `[]` early when `book_ids` is empty;
add regression test.

### D6 — `review_exercise` on a nonexistent exercise creates orphan rows — LOW — OPEN
Unlike `log_completion`, `review_exercise` writes `fsrs_cards` + `completions`
rows for any integer id; `scheduler._conn()` never sets `PRAGMA foreign_keys =
ON` (per-connection pragma; `init_db`'s doesn't carry over), so no error is
raised. Ref: `lifekit/schedule/scheduler.py`.
Suggested disposition: verify the exercise exists (like `log_completion` does)
or enable the FK pragma on scheduler connections; add regression test.

### D7 — Step 3 proposal promised `page_start`/`page_end`; schema has neither — LOW — OPEN
Proposal describes the exercises table with `page_start, page_end`; implemented
schema has `chapter_idx`/`chapter_title` instead, never recorded as a
deviation. Ref: `openspec/archives/step-3-reduce-dedupe/proposal.md` line 14.
Suggested disposition: either add the columns (needs chapter→page mapping from
the splitter) or record the drift in `ASSUMPTIONS.md`. Matters if exercises ever
need to link back to pages.

## Spec-vs-reality notes (honesty, not defects)

- **H1 — Step 5 "Coach MCP tools" overpromises — FIXED 2026-09-18.**
  `lifekit/mcp/server.py` rewritten as a real MCP stdio server (FastMCP,
  `mcp<2`) exposing 7 tools: `list_exercises`, `search_exercises`
  (natural-language, e.g. "i want to do the mindmapping exercise"),
  `get_exercise`, `complete_exercise` (FSRS review + completion log),
  `due_exercises`, `list_key_ideas`, `book_progress`. Verified with a real
  MCP initialize/tools-list/tools-call handshake against the product DB.
  `tests/test_mcp_server.py` (5 tests); suite 82/82.
- **H2 — Step 2 tasks.md checkboxes unchecked.** All 8 task boxes are `- [ ]`
  though the change is archived as done
  (`openspec/archives/step-2-extraction-map/tasks.md`). Status: ✅ FIXED
  2026-09-17 — all boxes checked; 2.7 completed with the home-Ollama
  full-book eval results recorded in tasks.md.
- **H3 — `validate_exercise` ignores `extra_quotes`.** The Step 4 proposal says
  it checks them; only the `validate_book` path does. The code comment admits
  it (`lifekit/validate/validator.py` line 26). Status: OPEN. Suggested
  disposition: align the proposal text with reality, or thread extra_quotes
  through `validate_exercise`.
- **H4 — `validation_log` duplicates on re-run.** `validate_book` appends on
  every run (it's a log — acceptable, but consumers should query latest).
  Ref: `lifekit/validate/validator.py`. Status: OPEN / accepted. Suggested
  disposition: document "query latest per (book_id, exercise_id, check_type)"
  in USER_MANUAL if it ever confuses anyone.

## Eval findings (2026-09-17 full-book eval, qwen3.8:27b-q8_0, home Ollama)

- **E1 — Validator quote check false-fails on whitespace — MEDIUM — FIXED 2026-09-18**
  Fixed in `lifekit/validate/validator.py::normalize_ws`: NFKC + typographic
  punctuation folding (curly quotes, em/en dashes, NBSP) then whitespace
  collapse, still strict substring matching. Post-fix validation of the DYL
  ingest: 142/144 exercises grounded; the 2 failures are PDF-extraction
  corruptions in chapter text ("welldesigned", "designi ngyour.life") where
  the model quoted correctly. Also fixed: extra_quotes now ground against
  full book text (merged records come from other chapters); source_quote
  still requires its own chapter. 7 new tests.
- **E2 — Raw recall overstates coverage until Step 3 dedupe runs — MEDIUM — FIXED 2026-09-18**
  `scripts/eval_dedupe_recall.py` ran Step 3 reduce over the eval output:
  156 raw -> 144 exercises (12 merges), dedupe-aware recall 19/20 (95%),
  same single miss (Ask-for-Help Journal). Dedupe only merges identical
  normalized titles, so fragmentation survives (Good Time Journal ×4,
  Mind Mapping ×3, five mind-set questions separate). Near-dupe title
  merging is a future improvement, not required for MVP.
  Ref: `evals/step2-recall-qwen3.8-27b-q8_0/README.md`.
  Suggested disposition: run Step 3 reduce over the eval extractions, then
  re-score recall — OpenSpec proposal at
  `openspec/changes/eval-dedupe-aware-recall/`.

## Portability / hygiene

- **P1 — `scripts/eval_step2_recall.py` hardcodes sandbox paths** (5 spots,
  e.g. lines 32, 111, 135–136, 211). Will break on the user's local dev setup
  before the deferred eval (A20). Status: ✅ FIXED 2026-09-15 (flags added;
  used portably in the 2026-09-17 home-Ollama eval).
- **P2 — `test_split_dyl_pdf` hardcodes an absolute VM path**
  (`tests/test_chapter_splitter.py` line 23). Passes here, errors on any other
  machine — real-PDF coverage evaporates outside this VM. Status: OPEN.
  Suggested disposition: skip when the PDF is absent (`pytest.mark.skipif`
  on `Path.exists`), or read the path from an env var.
- **P3 — Dead no-op loop** (`for c in chapters: c.title = c.title`) in
  `lifekit/store/chapter_splitter.py` line 241. Status: OPEN. Suggested
  disposition: delete (trivial cleanup).
- **P4 — Two `EmptyPDFError` classes** (`lifekit/store/pdf_ingester.py:37`,
  `lifekit/store/chapter_splitter.py:27`). Status: OPEN. Suggested disposition:
  consolidate to one shared exception.
- **P5 — `book_id_for` hashes the raw path** (`lifekit/books/registry.py`
  lines 10–12): relative vs absolute paths to the same file produce different
  book ids. Status: OPEN. Suggested disposition: `Path.resolve()` before
  hashing.
- **P6 — LIKE wildcards unescaped** in `lifekit/books/search.py` lines 26, 35:
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
  near-dupe merging is attempted (see E2).
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
