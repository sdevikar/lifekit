# Step 4: Validation harness — proposal

## Why

Steps 2–3 produce exercises with `source_quote` grounding, but nothing
verifies the quotes are verbatim or flags suspicious outputs (e.g. chapters
that should have exercises but returned none). Step 4 adds a deterministic
validation pass plus a sampled LLM-as-judge for quality.

## What Changes

- **New**: `../../../lifekit/validate/validator.py`:
  - `validate_exercise(exercise, chapter_text) -> dict`: check
    `source_quote` is an exact substring of `chapter_text`; check
    `extra_quotes` too. Returns `{ok, failures[]}`.
  - `validate_book(db_path, book_id, chapters) -> dict`: run over all
    exercises in the `exercises` table; join against chapter text.
  - Zero-extraction flags: chapters with 0 exercises but >X chars
    (suspicious) get flagged for review. Threshold: 5000 chars.
  - Persist results to `validation_log` table:
    `(id, book_id, exercise_id, check_type, passed, detail, created_at)`.
- **New**: `../../../lifekit/validate/judge.py`:
  - `sample_for_judge(db_path, book_id, pct=0.10)`: select 10% of exercises
    (min 1) for LLM review.
  - `judge_exercise(exercise, chapter_text, client)`: ask model "Is this
    exercise faithfully grounded in the chapter? Rate 1-5 and explain."
    (Uses same Ollama client interface; dev shim if needed.)
  - Persist to `judge_log`: `(id, book_id, exercise_id, score, rationale)`.
- **New**: CLI `python -m lifekit.validate --db-path DB --book-id ID
  [--chapters JSON]` — runs deterministic checks; `--judge` runs the
  10% sample.
- Schema: `validation_log`, `judge_log` tables.

## Capabilities

### New Capabilities

- `validation-harness`: deterministic grounding checks + flags + judge sample.

## Impact

- New package `../../../lifekit/validate/` (`validator.py`, `judge.py`, `__main__.py`).
- Schema: `validation_log`, `judge_log`.
- Judge uses Ollama (optional; skipped if no client).

## Done criterion

1. `tests/test_validator.py` passes: verbatim quote ok, non-verbatim
   fails, extra_quotes checked, zero-extraction flag triggers, judge
   sampling selects 10%.
2. Integration: validate the synthetic Step 3 exercises; all quotes pass
   (they're synthetic but we control them); zero-flag logic verified.
3. Record; archive; ROADMAP ✅; commit + push.
