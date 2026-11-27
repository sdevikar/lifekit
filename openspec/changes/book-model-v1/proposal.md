# Proposal — book-model-v1

## Why

LifeKit reads a book as a flat list of chapters. The splitter keeps only the top
TOC level (`_chapters_from_toc` in `lifekit/store/chapter_splitter.py`), so
"Dedication", "Contents", "Notes", and "Acknowledgments" become chapters and the
extractor mines them. In the dogfood DB they gave 27 ideas that no user needs.

The chapter text also has no stable positions. A quote can only be checked as
"somewhere in this chapter", so a card cannot point to the exact passage, and
chat grounding searches whole chapters with term counting (`_search_chapters`).

There is also no single ingest command. Ingest, split, extract, reduce, and
validate are separate `python -m` entry points, and the `dyl` dogfood book was
made by the eval harness (`books.file_path` = "eval:step2-recall-…").

This change gives every later slice a stable, deterministic model of the book.

## What Changes

- Accept **PDF and EPUB**. PyMuPDF opens both and `get_toc()` works on both
  (checked on a synthetic EPUB: `split_chapters()` returned two chapters
  unchanged). Audio, video, and scanned books stay out.
- Build a **sections tree** from every TOC level, not only the top one. Each
  section has a reading-order index, a parent, a depth, a page range, and a
  `kind`: `front`, `body`, or `back`.
- Classify `kind` with a title list in config (`lifekit/books/section_kinds.toml`),
  for example "dedication" → front, "notes" → back. Children take the kind of
  their top-level parent. The user can correct a kind with one command, and
  the correction survives re-ingest.
- Split each section into **passages** (about one paragraph each) with stable
  ids (`<book_id>:<section_idx>:<n>`) and character offsets. Drop running
  headers, footers, and page numbers.
- Index passages with SQLite FTS5 for grounding and later search.
- Record every pipeline run in a **`runs`** table (stage, model, prompt hash,
  parameters, status, counts), so every item and card can say which run made it.
- Make the **book id** the SHA-256 of the file bytes (first 16 hex chars), with
  a `--book-id` override for the dogfood book `dyl`. This fixes known issue P5
  (relative and absolute paths gave different ids).
- Add **`lifekit ingest <file>`**: one command that runs every pipeline stage in
  order. This change registers the first stage, `structure`. Later slices add
  `items` and `cards`. `--from <stage>` re-runs from a stage for a book that is
  already ingested.
- Add `lifekit book sections <book_id>` (print the tree) and
  `lifekit book set-kind <book_id> <section_idx> <kind>` (correct a kind).

## After this slice

What you will see in the app: nothing new. The app looks the same as after
slice 0.

What you can do on the command line:
- Run `lifekit ingest <file>` on a PDF or an EPUB. It runs only the first
  stage, `structure`: it stores the sections and the passages.
- Run `lifekit book sections <book_id>` to see the section tree, with each
  section marked front, body, or back.
- Run `lifekit book set-kind <book_id> <section_idx> <kind>` to fix a wrong
  kind.

What is not there yet (expected, not a bug):
- `lifekit ingest` makes no items or cards. Slices 3 and 4 add those stages.
- The old `python -m lifekit.store` ingest still exists. Slice 6 removes it.

## Capabilities

### New Capabilities

- `book-model`: how a book file becomes books, sections, and passages rows;
  section kinds; passage ids and offsets; run records; book identity.
- `book-ingest`: the `lifekit ingest` and `lifekit book` commands, stage order,
  re-runs, and error messages.

### Modified Capabilities

None. `openspec/specs/` holds no capabilities yet.

## Impact

- New modules: `lifekit/books/structure.py` (sections and passages),
  `lifekit/books/section_kinds.toml`, `lifekit/ingest.py` (stage runner and
  CLI), `lifekit/runs.py` (run records).
- Changed: `lifekit/__main__.py` (new `ingest` and `book` subcommands),
  `lifekit/db/schema.py` (new tables `sections`, `passages`, `passages_fts`,
  `runs`, `section_kind_overrides`; new `books` columns `format`,
  `content_hash`), `lifekit/store/chapter_splitter.py` (expose the page and
  TOC readers for reuse; delete the dead loop P3).
- Unchanged and frozen: `chapters`, `book_chunks`, and the old
  `python -m lifekit.store` path. card-comments moves coach grounding to
  passages and removes the old path.
- Docs: `docs/arch/README.md` data-flow diagram, `AGENTS.md` quick reference,
  `ASSUMPTIONS.md` A25 (already added by roadmap v2).
- No new dependencies (PyMuPDF and `tomllib` already present).
