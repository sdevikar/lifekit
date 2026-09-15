# Step 2: Extraction map — proposal

## Why

Chapters are now the unit of work (Step 1). The map step turns each chapter
into structured data — exercises and key ideas — via one schema-constrained
LLM call per chapter. This is where LLM value enters the pipeline; dedupe
(Step 3), validation (Step 4), and coaching (Step 5) all depend on its output
quality.

## What Changes

- **New**: `lifekit/extract/extractor.py` — `extract_chapter(chapter, ...) -> ChapterExtraction`.
- **Schema** (Pydantic):
  - `Exercise`: `title, purpose, steps[list[str]], materials[list[str]], source_quote, chapter`
  - `ChapterExtraction`: `chapter_title, key_ideas[list[str]], exercises[list[Exercise]]`
- **LLM call**: Ollama `chat` with `format=ChapterExtraction.model_json_schema()`,
  temperature 0.1, max 3 attempts with retry on Pydantic `ValidationError`.
- **Prompt rules**: extract only what the supplied text supports; include every
  distinct exercise, practice, prompt, routine, challenge, or worksheet; empty
  exercise lists allowed; every exercise carries a verbatim `source_quote`.
- **Model**: `OLLAMA_MODEL` env var (repo default `qwen3.6:latest`); dev/test
  override documented in ASSUMPTIONS.md.
- **Oversized chapters**: chapters over `MAX_CHAPTER_CHARS` (48k) are split with
  Chonkie `RecursiveChunker` into overlapping sections, extracted per section,
  and concatenated (dedupe is Step 3's job).
- **New**: CLI `python -m lifekit.extract --db-path DB --book-id ID` runs the map
  over all chapters of a book and prints a summary (per-chapter exercise counts).
- **Deferred**: persistence of extractions (Step 3), validation harness (Step 4).

## Capabilities

### New Capabilities

- `extract-map`: chapter text → structured `ChapterExtraction` (exercises + key ideas).

### Modified Capabilities

*(none)*

## Impact

- New package `lifekit/extract/` (`extractor.py`, `__main__.py`, `__init__.py`).
- New dep: `chonkie` (only used on the oversized-chapter path).
- No schema changes.

## Done criterion

1. `tests/test_extractor.py` passes: schema validation, retry-on-validation-error
   with a stubbed client, prompt contains grounding instructions.
2. Integration: 2 DYL chapters extracted with the real model; every
   `source_quote` verified as an exact substring of its chapter text.
3. Full-book run on the DYL PDF; recall measured against the 20-exercise manual
   ground truth (`workspace/self-help-exercises/designing-your-life-exercises.md`);
   results recorded in `tasks.md` (target ≥15/20 titles recovered; misses listed,
   not hidden).
