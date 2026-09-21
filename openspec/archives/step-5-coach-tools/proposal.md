# Step 5: Coach MCP tools — proposal

## Why

Steps 1–4 build the exercise library. Step 5 exposes it through MCP tools
so a coach agent (or the user via CLI) can list exercises, get details,
log completions, and get the next recommended exercise.

## What Changes

- **New**: `../../../lifekit/coach/tools.py` — pure functions (no MCP framework yet,
  just the logic; MCP adapter is deferred as "explicitly later" if needed,
  but the functions are MCP-ready):
  - `list_exercises(db_path, book_id, limit=20, offset=0) -> list[dict]`:
    paginated exercise summaries (id, title, chapter_title).
  - `get_exercise(db_path, exercise_id) -> dict`: full details (purpose,
    steps, materials, quotes).
  - `log_completion(db_path, exercise_id, notes=None) -> dict`: insert
    into `completions` table; return confirmation.
  - `next_exercise(db_path, book_id) -> dict`: simplest policy — first
    incomplete exercise (ordered by id). (FSRS scheduling is Step 7;
    this is a placeholder policy.)
- Schema: `completions` table:
  `(id, exercise_id REFERENCES exercises(id), completed_at, notes)`.
- **New**: CLI `python -m lifekit.coach --db-path DB list --book-id ID`,
  `get --exercise-id N`, `log --exercise-id N [--notes ...]`,
  `next --book-id ID`.

## Capabilities

### New Capabilities

- `coach-tools`: list/get/log/next over the exercise library.

## Impact

- New package `../../../lifekit/coach/` (`tools.py`, `__main__.py`).
- Schema: `completions` table.
- No model calls (deterministic).

## Done criterion

1. `tests/test_coach.py` passes: list pagination, get details, log
   completion persists, next returns first incomplete, next skips completed.
2. Integration: run CLI against synthetic DB; list/get/log/next all work.
3. Record; archive; ROADMAP ✅; commit + push.
