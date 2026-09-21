# Step 4: Validation harness — tasks

## Tests first

- [ ] `tests/test_validator.py`:
  - [ ] Verbatim `source_quote` (exact substring) → pass.
  - [ ] Non-verbatim quote (paraphrased) → fail with detail.
  - [ ] `extra_quotes` each checked; one bad → fail.
  - [ ] Zero-extraction flag: chapter >5000 chars, 0 exercises → flagged.
  - [ ] Zero-extraction flag: chapter <5000 chars, 0 exercises → not flagged.
  - [ ] Judge sampling: 10% of N exercises selected (min 1, deterministic seed).

## Implementation

- [ ] Schema: `validation_log`, `judge_log` tables.
- [ ] `../../../lifekit/validate/validator.py`: `validate_exercise()`,
      `validate_book()`, zero-extraction flags.
- [ ] `../../../lifekit/validate/judge.py`: `sample_for_judge()`, `judge_exercise()`.
- [ ] CLI: `python -m lifekit.validate --db-path DB --book-id ID`.

## Done criterion

- [x] All `tests/test_validator.py` pass (8/8; full suite 29/29).
- [x] Integration: synthetic exercises validated. 3/4 pass verbatim check.
      1 "failure" is correct behavior: an `extra_quote` merged from a
      different chapter (Ch5) is not verbatim in the kept chapter (Ch3).
      Known limitation: merged quotes are verbatim in their ORIGINAL chapter,
      not necessarily the kept one. Dedupe_log preserves the audit trail.
      Zero-flag logic verified via unit tests.
- [x] Record; archive; ROADMAP ✅; commit + push.

## Test results (2026-09-15)

- `tests/test_validator.py`: 8/8 passed.
- Full suite: 29/29 passed.
- Integration CLI: `python -m lifekit.validate` — 3 passed, 1 correctly
  flagged (cross-chapter merged quote).
