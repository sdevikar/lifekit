# Step 1: Chapter splitter — proposal

## Why

Every downstream step (extraction, dedupe, validation, coaching) operates
chapter-by-chapter: the chapter is the unit of mapping that keeps LLM calls
small enough to defeat lost-in-the-middle degradation. Before anything else,
LifeKit needs a reliable, reusable PDF chapter splitter. Per Step 0 (locked),
we assume well-formed PDFs with an embedded table of contents.

## What Changes

- **New**: `lifekit/store/chapter_splitter.py` — `split_chapters(pdf_path) -> list[Chapter]`,
  where `Chapter = (index, title, text, page_start, page_end)`.
- **Strategy** (in order):
  1. Read the embedded TOC via PyMuPDF (`get_toc()`) — primary path, zero heuristics.
  2. Heading heuristics (font size / style) only when the TOC is missing or empty.
  3. Fixed-size sections as final fallback.
  4. Image-only PDFs are refused with a clear error (reuse `EmptyPDFError` behavior).
- **New**: `chapters` table in SQLite — `(id, book_id, idx, title, page_start, page_end, content)`,
  migration in `lifekit/db/schema.py`.
- **New**: CLI `python -m lifekit.store.split --pdf <path>` printing detected chapters
  (title + page range) for inspection.
- **New dep**: PyMuPDF (for TOC + text extraction on this path; pypdf remains for ingest).
- **Deferred**: EPUB/YouTube parsing, semantic chapter boundaries, Step 2+ extraction.

## Capabilities

### New Capabilities

- `chapter-split`: PDF → ordered chapters with titles and page ranges, persisted to
  the `chapters` table; inspectable via CLI.

### Modified Capabilities

- `pdf-ingest`: unchanged behavior; chapter splitting is a separate, subsequent stage.

## Impact

- New file: `lifekit/store/chapter_splitter.py`.
- Schema migration: adds `chapters` table (idempotent `CREATE TABLE IF NOT EXISTS`).
- New CLI entry: `lifekit/store/__main__.py` gains a `split` subcommand (or `split.py`).
- Dev dependency for testing: 2–3 real self-help PDFs on disk (never committed).

## Done criterion (test before building anything else)

Run the splitter on 2–3 real self-help PDFs: chapter boundaries match each book's
actual table of contents on inspection; a heuristic-fallback case is exercised at
least once; an image-only PDF is refused with a clear error. Results recorded in
`tasks.md`.
