# Step 7: Scheduling (FSRS) — proposal

## Why

Steps 1–6 build and expose the exercise library. Step 7 adds spaced
repetition scheduling so the coach can recommend *when* to revisit
exercises, using the established FSRS algorithm (not custom math).

## What Changes

- **Dependency**: `fsrs>=6.0` (PyPI) — the open-source FSRS implementation.
  No custom scheduling math.
- **New**: `../../../lifekit/schedule/scheduler.py`:
  - `get_card(db_path, exercise_id) -> Card`: load or create FSRS Card
    for an exercise. Persist card state in new `fsrs_cards` table:
    `(exercise_id PRIMARY KEY, stability, difficulty, due, reps, lapses,
     state, last_review)`.
  - `review_exercise(db_path, exercise_id, rating) -> dict`: apply FSRS
    `scheduler.review_card()` with Rating (Again/Hard/Good/Easy);
    update `fsrs_cards`; also log to `completions`.
  - `due_exercises(db_path, book_id, limit=10) -> list[dict]`: exercises
    with `due <= now`, ordered by due date.
  - Rating mapping: completion without notes → Good (3); user can pass
    explicit rating via CLI.
- **New**: CLI `python -m lifekit.schedule --db-path DB review
  --exercise-id N --rating good|hard|easy|again` and `due --book-id ID`.

## Capabilities

### New Capabilities

- `fsrs-scheduling`: spaced repetition over exercise completion history.

## Impact

- New package `../../../lifekit/schedule/` (`scheduler.py`, `__main__.py`).
- Schema: `fsrs_cards` table.
- New dependency: `fsrs` (PyPI).

## Done criterion

1. `tests/test_scheduler.py` passes: card creation, review updates due
   date, due list ordering, rating mapping.
2. Integration: review an exercise, verify due date moves; due list works.
3. Record; archive; ROADMAP ✅; commit + push.
