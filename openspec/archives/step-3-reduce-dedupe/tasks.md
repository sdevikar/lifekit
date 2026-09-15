# Step 3: Reduce/dedupe — tasks

## Tests first

- [ ] `tests/test_reducer.py`:
  - [ ] Persists flattened exercises + key ideas to `exercises`/`key_ideas`
        tables with book/chapter linkage.
  - [ ] Exact duplicate titles across chapters merge into one row.
  - [ ] Near-duplicate titles (case/punctuation/whitespace variants) merge.
  - [ ] Merge keeps the fuller record (more steps) and preserves every
        `source_quote` (primary + `extra_quotes`).
  - [ ] Distinct exercises are kept as separate rows.
  - [ ] Every merge writes a `dedupe_log` audit row (kept id, merged title,
        reason).
  - [ ] `reduce_extractions` is idempotent for the same book (re-run does
        not duplicate rows).

## Implementation

- [ ] Schema: `exercises`, `key_ideas`, `dedupe_log` tables in
      `lifekit/db/schema.py`.
- [ ] `lifekit/reduce/reducer.py`: `reduce_extractions(book_id, chapters,
      extractions, db_path)` — deterministic normalize → merge → persist
      in one transaction.
- [ ] CLI: `python -m lifekit.reduce --db-path DB --book-id ID
      --extractions JSON`.
- [ ] Step 2 CLI `--out` flag produces the JSON the reduce CLI consumes
      (already added).

## Done criterion

- [x] All `tests/test_reducer.py` pass (6/6; full suite 21/21).
- [x] Integration: synthetic 3-chapter DYL-like extractions (6 candidates
      incl. cross-chapter duplicates) → 4 exercises, 2 key_ideas, 2 merges.
      Fuller records kept (3-step Odyssey Plans over 1-step dup); all
      source_quotes preserved (primary + extra_quotes); dedupe_log reviewed
      — both merges correct with reasons. (Full 17-chapter real integration
      deferred with Step 2 recall — needs production model.)
- [ ] Record results here; archive change; ROADMAP ✅; ASSUMPTIONS.md;
      commit + push.

## Test results (2026-09-15)

- `tests/test_reducer.py`: 6/6 passed.
- Full suite: 21/21 passed.
- Integration CLI: `python -m lifekit.reduce` on synthetic data —
  6 candidates → 4 exercises, 2 merges, all quotes preserved.
