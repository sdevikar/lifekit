# Step 4 fix: whitespace-normalizing quote grounding — proposal

## Why

The 2026-09-17 full-book eval (`qwen3.8:27b-q8_0`, home Ollama, 156 records)
measured quote grounding at **16/156 (10%) exact-substring vs 87/156 (56%)
whitespace-normalized**. The model quotes real book text and only alters
whitespace (e.g. `\n` → `\n\n`, line-wrap differences from PDF text
extraction). `validate_quotes` (`lifekit/validate/validator.py`) uses
exact-substring comparison, so as written it would false-fail ~90% of genuine
quotes. The validator is supposed to catch fabricated quotes, not typographic
whitespace drift.

## What Changes

- **Change**: `lifekit/validate/validator.py` — add a `normalize_ws()` helper
  that collapses every run of whitespace (spaces, tabs, newlines) to a single
  space, then strips. `validate_quotes` compares the normalized quote against
  the normalized chapter text. The failure message keeps the original
  (unnormalized) quote prefix for debuggability.
- Normalization applies to `source_quote` and all `extra_quotes`.
- **Do NOT change**: the strictness principle (still substring-based, no fuzzy
  matching — BACKLOG E1 is about whitespace only). A quote that is not a
  whitespace-normalized substring still fails.

## Capabilities

### Changed Capabilities

- `validation-harness`: quote grounding check becomes whitespace-insensitive.

## Impact

- `lifekit/validate/validator.py` only. No schema changes, no new tables.
- `tests/test_validator.py`: add tests — quote differing only in whitespace
  passes; quote with altered words still fails; extra_quotes normalized too.

## Done criterion

1. New whitespace tests pass; all existing validator tests still pass.
2. Re-running the deterministic check over the 2026-09-17 eval extractions
   grounds ~87/156 (matching the eval's whitespace-normalized measurement)
   instead of 16/156.

## Non-goals

- Fuzzy/semantic quote matching. A paraphrased quote must still fail.
- Re-running the full-book eval itself.
