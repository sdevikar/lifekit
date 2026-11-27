# LifeKit — Pipeline Design

## Book Ingestion Pipeline

```
PDF file
    |
    v
[1] Chapter Splitter
    |  PyMuPDF get_toc() -> TOC-first
    |  Fallback: heading/font heuristics
    |  Final fallback: fixed-size (15 pages)
    |
    v
[2] Extraction Map (per chapter)
    |  Ollama chat with JSON schema (Exercise, KeyIdea)
    |  temperature 0.1, 3-attempt Pydantic retry
    |  Oversized chapters: Chonkie RecursiveChunker -> per-section
    |
    v
[3] Reduce / Dedupe
    |  Normalized-title keying
    |  Fuller record wins; ties keep first-seen
    |  dedupe_log records every merge
    |
    v
[4] Validation Harness
    |  Verbatim-quote grounding (NFKC + whitespace normalize)
    |  Zero-extraction flags
    |  10% judge sample (seeded/deterministic)
    |
    v
SQLite store (exercises, key_ideas, chapters)
```

## Pipeline Characteristics

| Property | Value |
|----------|-------|
| Input | Single text-layer PDF |
| Output | Validated exercises + key ideas in SQLite |
| Model | Ollama (configurable); evals use home Ollama |
| Determinism | Temperature 0.1; seeded judge sampling |
| Failure handling | Zero-extraction flags; validation failures logged, not silent |
| Re-runnability | Idempotent; upsert on UNIQUE(book_id, title) |
| Eval | Full-book recall against 20-exercise ground truth (95% conditional pass) |

## Extraction Quality

| Metric | Value | Notes |
|--------|-------|-------|
| Full-book recall | 95% (19/20) | Single miss: Ask-for-Help Journal |
| Dedupe | 156 raw -> 144 exercises | 12 merges |
| Validation grounding | 142/144 | 2 failures are PDF-text corruptions |
| Hallucinations | 0 | All extractions quote-grounded |
