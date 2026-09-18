# Eval follow-up: dedupe-aware recall measurement — tasks

- [x] R.1 Write `scripts/eval_dedupe_recall.py`: load eval extractions → run
  existing `lifekit/reduce/reducer.py` → score 20-GT-exercise presence in the
  deduped set → print deduped count, merge count, per-exercise hit/miss
- [x] R.2 Run it; append dedupe-aware recall numbers to
  `evals/step2-recall-qwen3.8-27b-q8_0/README.md` (update verdict line if it changes)
- [x] R.3 If same-title duplicates survive deterministic dedupe, file the
  surviving patterns in BACKLOG.md as a Step 3 two-tier-dedupe refinement
  candidate (do NOT implement it here)
- [x] R.4 Mark BACKLOG E2 fixed; update STATUS.md in the same commit
- [x] R.5 Suite still 70/70
