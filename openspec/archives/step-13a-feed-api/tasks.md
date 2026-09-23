# Step 13a: Feed API — tasks (completed)

- [x] 13a.1 Write `tests/test_feed_api.py` first: migration applies cleanly; briefing returns the umbrella's shape; completions + idea-signals persist; conversation round-trip (create → message → reply → reload); malformed input rejected; binds localhost only
- [x] 13a.2 Implement the schema migration: `conversations`, `messages`, `idea_signals` column
- [x] 13a.3 Implement the HTTP API module reusing Step 5 coach tools + Step 7 scheduler (no new scheduling logic)
- [x] 13a.4 Implement the chat reply path: existing retrieval + `lifekit/llm` for prose; endpoint owns structure and persistence
- [x] 13a.5 Run the suite; verify all endpoints against the dogfood DB with curl
- [x] 13a.6 Update `docs/product/STATUS.md`; archive this slice on completion

## Test results (2026-09-22)

`uv run pytest tests/test_feed_api.py` — **30/30 passed** (was 27; added 3 tests
for `idea_signals` persistence + `due_exercises` FSRS path). Full suite
**112/112 passed** (82 pre-existing + 30 new).

- `test_schema_migration` (4): conversations/messages tables exist with correct
  columns; messages FK to conversations; migrations idempotent.
- `test_briefing` (3): briefing returns umbrella shape (book, day, stages,
  exercise, resurfaced_idea, fading_ideas); `due_exercises` FSRS path returns
  past-due exercise; fallback returns first incomplete exercise.
- `test_completions` (4): completion persists; bad/malformed/missing input → 400.
- `test_idea_signals` (4+1 new): signal persists in `idea_signals` table;
  malformed/bad-id input → 400.
- `test_conversations` (7): list/create/get; composer + card seeds; malformed → 400;
  not-found → 404; get-with-messages.
- `test_conversation_messages` (3): POST → grounded reply (LLM mocked); message
  + reply persist as user/coach roles; 404/400 handling; empty text → 400;
  full round-trip (create → message → reload).
- `test_localhost_binding` (2): host is `127.0.0.1`.

Verified against dogfood DB (`~/.lifekit/lifekit.db`, book `dyl`): briefing
returns exercise 28 + stages {seen:875, retained:1, lived:1}; completion persists
(completion_id 3); conversation round-trip works; `idea_signals` returns 200
with correct idea_id (1752).

New files: `../../../lifekit/serve/{__init__,server}.py`,
`../../../tests/test_feed_api.py`.
Changed: `../../../lifekit/db/schema.py` (conversations/messages tables +
`idea_signals` column), `../../../docs/product/STATUS.md`,
`../../../docs/product/ROADMAP.md`.