# Step 2: Extraction map — tasks

- [ ] 2.1 Write `tests/test_extractor.py`: schema validation, retry-on-`ValidationError` with stubbed client, grounding-instruction prompt check
- [ ] 2.2 Implement `lifekit/extract/extractor.py`: `Exercise` / `ChapterExtraction` schemas + `extract_chapter()` via Ollama `format=<schema>` at temperature 0.1
- [ ] 2.3 Retry up to 3 attempts on Pydantic `ValidationError`
- [ ] 2.4 Oversized-chapter path: Chonkie `RecursiveChunker` split → per-section extraction → concatenate
- [ ] 2.5 CLI `python -m lifekit.extract --db-path DB --book-id ID` (map over a book's chapters, print summary)
- [ ] 2.6 Integration test: 2 DYL chapters via real model; all `source_quote`s verified as exact substrings
- [ ] 2.7 Full-book DYL extraction run; recall vs. 20-exercise ground truth recorded below
- [ ] 2.8 py_compile clean on all new/changed files

## Test results

### Unit tests (2026-09-15)
- `tests/test_extractor.py`: 8/8 passed (schema validation, stub-client
  parse, retry on validation error, max-attempts raise, grounding prompt
  check, oversized-chapter Chonkie split, **chapter_title backfill**).
- `tests/test_split_cli.py`: 1/1 passed (nested DB parent auto-created).
- `tests/test_chapter_splitter.py`: 6/6 passed.
- Full suite: 15/15 passed.

### Real-model integration (2026-09-15) — BLOCKED on model capability
- Runner: llama.cpp (Ollama binary not downloadable — registry TLS blocked;
  see A17) + Qwen3-4B-Q4_K_M GGUF via dev-only Ollama-interface shim.
  Product code stays Ollama-native (`ollama.Client`, `format=<schema>`).
- Chapters 0 (Dedication), 1 (Contents): ok=True, 0 exercises each (correct —
  no exercises in front matter).
- **BLOCKER**: Qwen3-4B systematically fails Pydantic validation on ALL
  exercise-bearing chapters tested (Introduction, ch.3, ch.4, ch.7/Design
  Your Lives). It returns exercises missing required `title`/`purpose`/`steps`
  (e.g. bare `{'source_quote': ...}`). 3 retries do not recover. Tested:
  thinking-enabled (too slow, 13+ min/req), one-shot example prompt (no
  improvement), structured vs discursive chapters (both fail).
- **8B attempt**: Qwen3-8B-Q4_K_M (5GB) OOMs on this 7.9GB RAM machine
  during load. Deleted to free disk.
- **Result**: The 15/20 recall criterion cannot be measured with available
  models. The pipeline (schemas, retries, chunking, grounding checks) is
  unit-tested and correct; the blocker is model capability, not code.
  Requires: real Ollama + a capable model (qwen3.6 or larger) to re-run.

### Bug found & fixed during integration
- Model omitted required `chapter_title` on front-matter chapters →
  `extract_chapter` now backfills it from the known `Chapter.title`
  (new unit test). Strict schema unchanged for the model.
- `lifekit/store/split.py`: auto-create nested DB parent dirs (new CLI test).

### Dependency
- Chonkie added to `pyproject.toml` (was installed but undeclared).
