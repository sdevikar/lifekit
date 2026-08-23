## Why

Raw PDF ingestion produces uniform text chunks with no awareness of semantic structure (chapters, sections, exercises). This means the plan forge works with random page slices rather than coherent units of meaning. A digestibility pipeline that understands chapter boundaries will allow the LLM to generate per-chapter learning tasks — a far more natural learning cadence — and lays the groundwork for later features like per-chapter RAG retrieval, Feynman exercises per concept, and momentum tracking at the chapter level.

We know chapter splitting is solvable via `~/workspace/projects/chapter-splitter`, but that tool requires a DOI registered with Crossref/Thoth, which most local PDFs will not have. So the MVP approach uses a **heuristic chapter detector** built in-process, with the architectural decision of full-upfront-split vs. lazy RAG deferred until Phase 1.

## What Changes

- **New**: `lifekit/store/content_processor.py` — post-ingest pipeline step that runs on an already-ingested book and annotates chunks with detected chapter boundaries
- **New**: `chapter_id` and `chapter_title` columns added to `book_chunks` table (nullable, populated by the processor)
- **New**: `chapters` table storing detected chapter metadata (title, start_chunk, end_chunk, page_estimate)
- **Modified**: `pdf-ingest` spec — ingestion now optionally triggers the content processor after chunk storage (off by default, opt-in via `--process` flag)
- **Deferred decision**: whether to split the PDF into per-chapter PDFs upfront (using chapter-splitter when a DOI is available) or do lazy per-chapter RAG retrieval at plan-forge time — this decision is tracked as an open question in design, not implemented

## Capabilities

### New Capabilities

- `content-processor`: Heuristic chapter detector that scans `book_chunks` for chapter-heading patterns and annotates the `chapters` table and `book_chunks.chapter_id`; invokable standalone or as a post-ingest hook

### Modified Capabilities

- `pdf-ingest`: Post-ingest, optionally invoke `content_processor.detect_chapters(book_id)` via `--process` flag; `book_chunks` table gains `chapter_id` and `chapter_title` nullable columns
- `db-schema`: Adds `chapters` table and two nullable columns to `book_chunks`

## Impact

- **`lifekit/store/content_processor.py`**: New module, no external deps beyond `re` and `sqlite3`
- **`lifekit/db/schema.py`**: `book_chunks` gains two nullable columns; new `chapters` table — migrations must be idempotent
- **`lifekit/store/pdf_ingester.py`**: Optional `--process / process: bool` param added to `ingest_pdf()`
- **`Makefile`**: `make ingest PDF=... PROCESS=1` passes flag through
- **No external API calls**: heuristic detection is pure Python regex over chunk text
- **chapter-splitter integration**: Documented as a future path for DOI-registered books; not wired in MVP
