# LifeKit — Testing Strategy

## Current State

| Suite | Count | Coverage |
|-------|-------|----------|
| `test_chapter_splitter` | 6 | TOC-first, heuristic, fallback; image-only PDF refusal |
| `test_split_cli` | 1 | CLI end-to-end |
| `test_extractor` | 9 | Ollama schema, retry loop, backfill, section path |
| `test_reducer` | 7 | Deterministic dedupe, re-run stability |
| `test_validator` | 11 | Quote grounding, zero-extraction, judge sampling |
| `test_coach` | 6 | Coach tool functions |
| `test_multibook` | 4 | Registry, search isolation |
| `test_scheduler` | 6 | FSRS library usage, card state |
| `test_llm_config` | 9 | Config resolution order |
| `test_llm_providers` | 6 | Mocked transport, request shape |
| `test_config_cli` | 5 | Config CLI round-trips |
| `test_feed_api` | 30 | Feed API endpoints, migration, conversation round-trip |
| **Total** | **112** | All green |

## Testing Principles

1. **Zero tests exercise a real LLM.** All model calls are stubbed/mocked.
2. **The suite proves the pipeline is plumbed, not that it extracts.** The real-model eval is the quality gate.
3. **Provider tests use a mocked transport** — they verify request shape/config resolution, not that a real API call succeeds.
4. **Portability:** tests skip gracefully when fixtures are absent (e.g., real PDF).

## Eval Strategy

| Eval | Model | Frequency | Gate |
|------|-------|-----------|------|
| Full-book extraction recall | Home Ollama (qwen3.8:27b-q8_0) | Per pipeline change | >= 90% recall |
| Dedupe-aware recall | Script (`eval_dedupe_recall.py`) | Per reduce change | No regression |
| Validation grounding | Per ingest | Per book | >= 95% grounded |

## Eval Results (2026-09-17)

- Full-book extraction recall: 95% (19/20), single miss Ask-for-Help Journal
- Dedupe: 156 raw -> 144 exercises (12 merges)
- Validation grounding: 142/144 (2 failures are PDF-text corruptions)
- Hallucinations: 0
