# Eval follow-up: dedupe-aware recall measurement — proposal

## Why

The 2026-09-17 full-book eval produced 156 exercise records with heavy
fragmentation: Good Time Journal ×4, Mind Mapping ×3, Life Design Interview
×2, the five mind-set questions as separate records, personal practices split
into single habits (ch 14 has 23 records for 3 ground-truth practices).
Substance recall is 19/20 (95%), but that number was measured on raw
extraction output — Step 3 dedupe has not run. Raw recall overstates real
coverage: what the coach consumes is the *deduped* exercise table, so recall
must be measured post-dedupe to mean anything (BACKLOG E2).

## What Changes

- **New**: `scripts/eval_dedupe_recall.py` — loads the eval's raw extractions
  (`evals/step2-recall-qwen3.8-27b-q8_0/extractions_qwen3.8-27b-q8_0.json`),
  runs the existing Step 3 reducer (`lifekit/reduce/reducer.py`) over them,
  then scores dedupe-aware recall: for each of the 20 ground-truth exercises,
  is its substance present in the deduped set (allowing many-to-one merges)?
  Reports: deduped record count, merge count, per-GT-exercise hit/miss, and
  the fragmentation patterns that survived dedupe.
- **Report**: append the dedupe-aware numbers to
  `evals/step2-recall-qwen3.8-27b-q8_0/README.md` and update the verdict line
  if the result changes it.
- **Harden if needed**: if same-title duplicates survive the deterministic
  dedupe (normalized-title keying), record the surviving patterns in
  BACKLOG.md as a Step 3 refinement candidate (the converged two-tier shape:
  cheap string-similarity within chapter → expensive LLM/embedding
  consolidation across chapters, per book2anki + flashcard-mcp). Do NOT
  implement the two-tier dedupe in this change — file it, don't build it.

## Capabilities

### New Capabilities

- `eval-dedupe-recall`: post-dedupe recall measurement script + report update.

## Impact

- New script `scripts/eval_dedupe_recall.py`; reuses `lifekit/reduce/` as-is.
- No product code changes unless a trivial reducer bug is found while
  running (then fix + regression test, per the defect protocol).

## Done criterion

1. Script runs against the committed eval extractions and prints dedupe-aware
   recall (e.g. X/20 GT exercises present in the deduped set).
2. README updated with the numbers; BACKLOG E2 marked fixed; surviving
   fragmentation patterns (if any) filed as a Step 3 refinement candidate.
3. Suite still 70/70.

## Non-goals

- Building the two-tier dedupe. This change measures; it does not redesign
  Step 3.
- Re-running the model extraction.
