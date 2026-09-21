# Step 3: Reduce/dedupe — proposal

## Why

The map (Step 2) emits one `ChapterExtraction` per chapter. The reduce step
merges these into a clean, book-level library: duplicate exercises (same
exercise described in two chapters, or re-emitted across Chonkie sections)
are merged, and everything is persisted to queryable tables for coaching.

## What Changes

- **New tables** (migration in `../../../lifekit/db/schema.py`):
  - `exercises`: `(id, book_id, chapter_idx, chapter_title, title, purpose,
    steps JSON, materials JSON, source_quote, page_start, page_end)`
  - `key_ideas`: `(id, book_id, chapter_idx, idea)`
  - `dedupe_log`: `(id, book_id, kept_exercise_id, merged_exercise_title,
    merged_source_quote, reason, created_at)` — audit trail of every merge.
- **New**: `../../../lifekit/reduce/reducer.py` — `reduce_extractions(book_id, chapters,
  extractions, db_path)`:
  1. Flatten all chapter extractions into candidate exercises.
  2. Deterministic dedupe: normalize titles (lowercase, strip punctuation/
     whitespace); candidates matching an existing exercise merge into it.
  3. Merge rule: keep the fuller record (more steps); preserve every
     `source_quote` (append to a `source_quotes` list — schema: keep primary
     `source_quote` + `extra_quotes JSON`).
  4. Write `exercises`, `key_ideas`, `dedupe_log` rows in one transaction.
  5. Embeddings only if deterministic dedupe proves insufficient (logged).
- **New**: CLI `python -m lifekit.reduce --db-path DB --book-id ID
  --extractions JSON` — reads a JSON array of `ChapterExtraction` dicts
  (as produced by the Step 2 map), reduces, prints summary.
- **Deferred**: validation harness (Step 4), MCP tools (Step 5).

## Capabilities

### New Capabilities

- `reduce-dedupe`: chapter extractions → deduplicated `exercises`/`key_ideas`
  tables + merge audit log.

## Impact

- New package `../../../lifekit/reduce/` (`reducer.py`, `__main__.py`, `__init__.py`).
- Schema migration: `exercises`, `key_ideas`, `dedupe_log` tables.
- No new model dependencies (deterministic first).

## Done criterion

1. `tests/test_reducer.py` passes: persistence, exact-duplicate merge (keeps
   fuller record), near-duplicate merge (case/punctuation variants), distinct
   exercises kept separate, audit log entries for every merge.
2. Integration: reduce the real DYL map outputs (17 chapters) → `exercises`
   table; exercise count sane vs. 20-exercise ground truth (no mass duplication,
   no mass loss); dedupe log reviewed.
