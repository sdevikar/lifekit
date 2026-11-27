# Tasks — book-model-v1

## 1. Schema and run records

- [ ] 1.1 Add `sections`, `passages`, `passages_fts`, `section_kind_overrides`, and `runs` to `SCHEMA` in `lifekit/db/schema.py`, and a migration that adds `books.format` and `books.content_hash` when missing (design.md D6); verify `init_db()` on a fresh DB and on a copy of `dogfood/lifekit.db` both succeed and run twice without error.
- [ ] 1.2 Write `lifekit/runs.py` with `start_run()`, `finish_run()`, and `fail_run()`; verify tests for "Structure run recorded" and "Failed stage recorded" pass in `tests/test_runs.py`.

## 2. Structure building

- [ ] 2.1 In `lifekit/store/chapter_splitter.py`, expose the TOC, heading, and fixed-size readers for reuse and delete the dead loop (P3); verify `uv run pytest tests/test_chapter_splitter.py -v` still passes.
- [ ] 2.2 Write a test fixture helper in `tests/test_book_structure.py` that builds a small PDF with PyMuPDF (`fitz.open()`, `insert_page`, `set_toc`) with a nested TOC, a running header, page numbers, a "Dedication", and a "Notes" section, and a small EPUB (zip with `mimetype`, `container.xml`, OPF, nav, two XHTML chapters); verify both open with `fitz.open()`.
- [ ] 2.3 Write `lifekit/books/structure.py`: block reading with hyphen joins (D1), section boundaries from all TOC levels with the fallbacks (D2), and the furniture filter (D5); verify tests for "Nested TOC", "No TOC", and "Running header removed" pass.
- [ ] 2.4 Add passage building and offsets (D4); verify tests for "Offsets point into the section" and "Short heading line joins the next paragraph" pass, and that joined passages equal the section text for every section of both fixtures.
- [ ] 2.5 Add `lifekit/books/section_kinds.toml` and kind classification with children inheriting and overrides applied (D3); verify the "Front and back matter detected" test passes.
- [ ] 2.6 Add book identity from file bytes with an explicit-id override (D7) and the format, encryption, and text-layer checks; verify tests for "Same file, different path", "Explicit id", "EPUB accepted", "Scanned PDF refused", and "Unsupported format refused" pass.
- [ ] 2.7 Persist books, sections, passages, and `passages_fts` in one transaction that first deletes the book's old rows; verify tests for "Re-ingest is stable" (byte-identical dumps) and "Search within one book" pass.

## 3. Commands

- [ ] 3.1 Write `lifekit/ingest.py` with the `Stage` protocol, `STAGES`, `Pipeline.run()`, and `StructureStage` (D8); verify tests for "Stop on first failure" (using a stage that raises) and "Unknown stage" pass in `tests/test_ingest.py`.
- [ ] 3.2 Add `ingest` and `book sections` / `book set-kind` subcommands to `lifekit/__main__.py`; verify tests for "Ingest a new book", "Title from metadata", "Re-run from a stage", "Print the tree", "Mark a preface as front matter", "Bad kind", and "Correction survives re-ingest" pass, using the fixture PDF.
- [ ] 3.3 Run `lifekit ingest <dyl.pdf> --book-id dyl` against a scratch DB (`LIFEKIT_DB=/tmp/lk_bm.db`) and `lifekit book sections dyl`; verify by reading the output that Dedication, Contents, Notes, and Acknowledgments are not body, and record the section and passage counts in the change's handoff.

## 4. Docs

- [ ] 4.1 Update `docs/arch/README.md` with the mermaid flow from design.md and the new tables, and add `lifekit ingest` and `lifekit book` rows to the `AGENTS.md` quick reference; verify both render and the commands match `lifekit --help`.
- [ ] 4.2 Mark known issues P3 and P5 fixed with today's date in `docs/product/KANBAN.md`, add the new test files to `docs/arch/testing.md`, and update the test count; verify `uv run pytest tests/ -q` shows only the known `test_split_dyl_pdf` failure.

## Workflow follow-up

- Move the KANBAN row for slice 2 to Done and archive this change after merge.
