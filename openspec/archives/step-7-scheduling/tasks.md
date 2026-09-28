# Step 7: Scheduling (FSRS) — tasks

## Tests first

- [x] `tests/test_scheduler.py`:
  - [x] `get_card` creates new card for exercise (default state).
  - [x] `get_card` loads existing card (persistence).
  - [x] `review_exercise` with Good rating pushes due date forward.
  - [x] `review_exercise` with Again rating keeps due date near.
  - [x] `review_exercise` logs to `completions`.
  - [x] `due_exercises` returns only due items, ordered by due.

## Implementation

- [x] Dependency: `fsrs` in `pyproject.toml`.
- [x] Schema: `fsrs_cards` table.
- [x] `../../../lifekit/schedule/scheduler.py`.
- [x] CLI: `python -m lifekit.schedule`.

## Done criterion

- [x] All `tests/test_scheduler.py` pass (6/6; full suite 45/45).
- [x] Integration: 4 exercises due; review id=1 with Good → due moves
      +10min; due list now shows 3 (correct). Completion logged.
- [x] Record; archive; ROADMAP ✅; commit + push.

## Test results (2026-09-15)

- `tests/test_scheduler.py`: 6/6 passed.
- Full suite: 45/45 passed.
- Uses open-source `fsrs` PyPI package (v6.3.2); no custom scheduling math.
