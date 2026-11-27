# Tasks — feed-v1

## 1. Backend

- [ ] 1.1 Add `card_state` and `card_events` (D1) to `lifekit/db/schema.py`; verify `init_db()` runs twice on a fresh DB and on a dogfood copy.
- [ ] 1.2 Write `lifekit/serve/feed.py` with `default_book`, `feed_page`, and `set_reaction` (D2, D3); verify tests for "Disliked and retired cards left out", "Start where you left off", "Furthest, not latest", "No responses yet", "Second page", "Earlier page", "Entry shape", "Dislike and undo", and "Reaction survives re-ingest" pass in `tests/test_card_feed.py` against a temp DB with hand-inserted cards.
- [ ] 1.3 Wire the two routes in `FeedAPI` and drop the `"dyl"` default; verify tests for "Unknown book", "Bad reaction value", the empty response, and a Flask test-client round trip pass.
- [ ] 1.4 Remove the briefing routes and helpers (D5) and their tests in `tests/test_feed_api.py`, `tests/test_coach.py`, and `tests/test_scheduler.py`; verify "Old endpoint" returns 404 and `uv run pytest tests/ -q` shows only the known `test_split_dyl_pdf` failure.

## 2. Frontend

- [ ] 2.1 Write `useFeed.ts`, `FeedCardView.tsx`, and `ReactionBar.tsx` (D4) and switch `feed/page.tsx` to them, without `MasterComposer`; verify `npx next build` and `npx eslint src` pass.
- [ ] 2.2 Delete `ExerciseCard.tsx`, `ResurfacedIdeaCard.tsx`, `FadingIdeasCard.tsx`, `TodayHeader.tsx`, and `useBriefing.ts`; verify `grep -rn "useBriefing\|briefing/today" frontend/src` finds nothing and the build passes.
- [ ] 2.3 Run `lifekit ui` on a DB with generated `dyl` cards and ask the human to check "Start where you left off", "Dislike and undo", "Header count", "Show earlier cards", the phone view over Tailscale, and the empty state on a fresh DB.

## 3. Docs

- [ ] 3.1 Update `docs/arch/README.md` (feed data flow, D4 diagram, endpoint table), `AGENTS.md` (Architecture: endpoints, no default book), and `docs/arch/testing.md` (new and removed tests, test count); verify the docs name no removed endpoint.

## Workflow follow-up

- Move the KANBAN row for slice 5 to Done and archive this change after merge.
