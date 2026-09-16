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

- **H1 — Step 5 "Coach MCP tools" overpromises.** The Step 5 proposal itself
  says "MCP adapter is deferred" (`openspec/archives/step-5-coach-tools/
  proposal.md` lines 11–12); nothing is wired into `lifekit/mcp/server.py`
  (still the legacy Phase-0 plans/tasks API). Status: OPEN. Suggested
  disposition: rename the roadmap entry to "Coach tools (logic)" until the
  adapter lands, or build the adapter in Step 8.
- **H2 — Step 2 tasks.md checkboxes unchecked.** All 8 task boxes are `- [ ]`
  though the change is archived as done
  (`openspec/archives/step-2-extraction-map/tasks.md`). Status: OPEN.
  Suggested disposition: check the boxes that are done; leave 2.7 unchecked
  (deferred per A17/A20).
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

## Portability / hygiene

- **P1 — `scripts/eval_step2_recall.py` hardcodes sandbox paths** (5 spots,
  e.g. lines 32, 111, 135–136, 211). Will break on the user's local dev setup
  before the deferred eval (A20). Status: OPEN. Suggested disposition: add
  `--db`, `--out`, `--ground-truth` flags (db flag exists at line 111; wire
  the rest) before the local eval runs.
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
