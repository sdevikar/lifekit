# Step 3: Reduce/dedupe — tasks

## Tests first

- [x] `tests/test_reducer.py`:
  - [x] Persists flattened exercises + key ideas to `exercises`/`key_ideas`
        tables with book/chapter linkage.
  - [x] Exact duplicate titles across chapters merge into one row.
  - [x] Near-duplicate titles (case/punctuation/whitespace variants) merge.
  - [x] Merge keeps the fuller record (more steps) and preserves every
        `source_quote` (primary + `extra_quotes`).
  - [x] Distinct exercises are kept as separate rows.
  - [x] Every merge writes a `dedupe_log` audit row (kept id, merged title,
        reason).
  - [x] `reduce_extractions` is idempotent for the same book (re-run does
        not duplicate rows).

## Implementation

- [x] Schema: `exercises`, `key_ideas`, `dedupe_log` tables in
      `../../../lifekit/db/schema.py`.
- [x] `../../../lifekit/reduce/reducer.py`: `reduce_extractions(book_id, chapters,
      extractions, db_path)` — deterministic normalize → merge → persist
      in one transaction.
- [x] CLI: `python -m lifekit.reduce --db-path DB --book-id ID
      --extractions JSON`.
- [x] Step 2 CLI `--out` flag produces the JSON the reduce CLI consumes
      (already added).

## Done criterion

- [x] All `tests/test_reducer.py` pass (6/6; full suite 21/21).
- [x] Integration: synthetic 3-chapter DYL-like extractions (6 candidates
      incl. cross-chapter duplicates) → 4 exercises, 2 key_ideas, 2 merges.
      Fuller records kept (3-step Odyssey Plans over 1-step dup); all
      source_quotes preserved (primary + extra_quotes); dedupe_log reviewed
      — both merges correct with reasons. (Full 17-chapter real integration
      deferred with Step 2 recall — needs production model.)
- [x] Record results here; archive change; ROADMAP ✅; ../../../docs/product/ASSUMPTIONS.md;
      commit + push.

## Test results (2026-09-15)

- `tests/test_reducer.py`: 6/6 passed.
- Full suite: 21/21 passed.
- Integration CLI: `python -m lifekit.reduce` on synthetic data —
  6 candidates → 4 exercises, 2 merges, all quotes preserved.
