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

- [ ] All `tests/test_reducer.py` pass.
- [ ] Integration: reduce the 17 real DYL chapter extractions → `exercises`
      table; count is sane against the 20-exercise ground truth (no mass
      duplication, no mass loss); `dedupe_log` reviewed for correctness.
- [ ] Record results here; archive change; ROADMAP ✅; ASSUMPTIONS.md;
      commit + push.
