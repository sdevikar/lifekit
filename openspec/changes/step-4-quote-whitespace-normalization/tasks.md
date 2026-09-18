# Step 4 fix: whitespace-normalizing quote grounding — tasks

- [ ] W.1 Write failing tests in `tests/test_validator.py`: quote with altered
  whitespace (newlines/tabs doubled) passes; quote with one changed word fails;
  extra_quotes normalized too
- [ ] W.2 Implement `normalize_ws()` in `lifekit/validate/validator.py` and
  apply it in `validate_quotes` for `source_quote` and `extra_quotes`
- [ ] W.3 Run full suite — 70/70 plus new tests green
- [ ] W.4 Sanity-check: deterministic grounding over the 2026-09-17 eval
  extractions reaches ~87/156 (whitespace-normalized) instead of 16/156
- [ ] W.5 Update BACKLOG.md (E1 → fixed) and STATUS.md in the same commit
