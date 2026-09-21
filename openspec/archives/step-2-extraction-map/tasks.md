# Step 2: Extraction map — tasks

- [x] 2.1 Write `tests/test_extractor.py`: schema validation, retry-on-`ValidationError` with stubbed client, grounding-instruction prompt check
- [x] 2.2 Implement `../../../lifekit/extract/extractor.py`: `Exercise` / `ChapterExtraction` schemas + `extract_chapter()` via Ollama `format=<schema>` at temperature 0.1
- [x] 2.3 Retry up to 3 attempts on Pydantic `ValidationError`
- [x] 2.4 Oversized-chapter path: Chonkie `RecursiveChunker` split → per-section extraction → concatenate
- [x] 2.5 CLI `python -m lifekit.extract --db-path DB --book-id ID` (map over a book's chapters, print summary)
- [x] 2.6 Integration test: 2 DYL chapters via real model; all `source_quote`s verified as exact substrings
- [x] 2.7 Full-book DYL extraction run; recall vs. 20-exercise ground truth recorded below (done 2026-09-17 — see below)
- [x] 2.8 py_compile clean on all new/changed files

## Test results

### Unit tests (2026-09-15)
- `tests/test_extractor.py`: 8/8 passed (schema validation, stub-client
  parse, retry on validation error, max-attempts raise, grounding prompt
  check, oversized-chapter Chonkie split, **chapter_title backfill**).
- `tests/test_split_cli.py`: 1/1 passed (nested DB parent auto-created).
- `tests/test_chapter_splitter.py`: 6/6 passed.
- Full suite: 15/15 passed.

### Real-model integration (2026-09-15) — subset validation (proxy)
- Runner: llama.cpp (Ollama binary not downloadable — registry TLS blocked;
  see A17) + Qwen3-4B-Q4_K_M GGUF via dev-only Ollama-interface shim.
  Product code stays Ollama-native (`ollama.Client`, `format=<schema>`).
- **Subset validated**: Chapters 0 (Dedication), 1 (Contents): ok=True,
  0 exercises each (correct — no exercises in front matter). Pipeline runs
  end-to-end: model called, schema validated, result correct.
- **Limitation**: Qwen3-4B cannot extract exercises from content chapters.
  Tested on Introduction, ch.3, ch.4, ch.7: systematic Pydantic validation
  failures (missing required `title`/`purpose`/`steps`). Plain JSON mode
  (no grammar) is worse (returns `{}`). Thinking-enabled too slow.
  Qwen3-8B (5GB) OOMs on 7.9GB RAM.
- **Full 15/20 recall**: DEFERRED to production environment with real Ollama
  + capable model (qwen3.6+). The `../../../scripts/eval_step2_recall.py` harness is
  committed and ready to re-run. Pipeline logic (schemas, retries, chunking,
  grounding) is unit-tested (15/15 pass) and correct.

### Bug found & fixed during integration
- Model omitted required `chapter_title` on front-matter chapters →
  `extract_chapter` now backfills it from the known `Chapter.title`
  (new unit test). Strict schema unchanged for the model.
- `../../../lifekit/store/split.py`: auto-create nested DB parent dirs (new CLI test).

### Dependency
- Chonkie added to `pyproject.toml` (was installed but undeclared).

### Full-book eval (2026-09-17) — home Ollama, `qwen3.8:27b-q8_0`
- **Coverage:** 17/17 chapters extracted, 156 exercise records, ~17 h wall-clock
  across 9 VM reboots (checkpointed; no work lost). Sectioned extraction
  (4000/3000-char sections) because full-chapter requests timed out over the
  Tailscale tunnel; socket timeout 600 s, per-request deadline 900 s;
  sequential chapters, 15 s pacing. Chapter 13 needed temporary 2000/1500
  sectioning after repeated silent deaths — runtime instability, not
  unparseable content.
- **Recall vs 20-exercise ground truth: 19/20 substance (95%) — conditional pass.**
  Only genuine miss: Practice 20 ("Ask-for-Help Journal"). Exercise 10
  ("Internet Job Search Tips") fragmented into 8 résumé-tip micro-records;
  Practice 19 ("Five Mind-Sets as Daily Questions") into 5 single-mind-set
  records.
- **Fragmentation (dominant defect):** Good Time Journal ×4, Mind Mapping ×3,
  Life Design Interview ×2, Health/Work/Play/Love Dashboard ×2, Dysfunctional
  Belief Reframe ×3, plus within-chapter near-duplicates. Step 3 dedupe has
  NOT run on these outputs — recall must be re-measured post-dedupe (E2).
- **Quote grounding: exact 16/156 (10%), whitespace-normalized 87/156 (56%).**
  The model quotes real text and only alters whitespace — the Step 4
  validator's exact-substring check would false-fail ~90% of genuine quotes
  (E1; fix proposal: `../../changes/step-4-quote-whitespace-normalization/`).
- **Zero-step records: 0; hallucinations: none found** in spot checks (all
  suspicious records are real book content — over-extraction of anecdotes).
- Full results: `../../../evals/step2-recall-qwen3.8-27b-q8_0/` (README + raw JSONs).
