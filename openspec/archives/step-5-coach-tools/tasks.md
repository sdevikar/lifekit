# Step 5: Coach MCP tools — tasks

## Tests first

- [x] `tests/test_coach.py`:
  - [x] `list_exercises` returns paginated summaries (id, title, chapter).
  - [x] `get_exercise` returns full details (purpose, steps, materials, quotes).
  - [x] `get_exercise` with bad id raises/returns None.
  - [x] `log_completion` persists to `completions` with timestamp.
  - [x] `next_exercise` returns first incomplete (by id).
  - [x] `next_exercise` skips completed; returns None when all done.

## Implementation

- [x] Schema: `completions` table.
- [x] `../../../lifekit/coach/tools.py`: 4 functions.
- [x] CLI: `python -m lifekit.coach`.

## Done criterion

- [x] All `tests/test_coach.py` pass (6/6; full suite 35/35).
- [x] Integration: CLI list/get/log/next against synthetic DB — all work.
      list shows 4 exercises; next returns id=1; log persists; next skips
      to id=2.
- [x] Record; archive; ROADMAP ✅; commit + push.

## Test results (2026-09-15)

- `tests/test_coach.py`: 6/6 passed.
- Full suite: 35/35 passed.
