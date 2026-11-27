# Tasks — feed-v1

## 1. Backend

- [ ] 1.1 Add `card_state` and `card_events` (D1) to `lifekit/db/schema.py`; verify `init_db()` runs twice on a fresh DB and on a dogfood copy.
- [ ] 1.2 Write `lifekit/serve/feed.py` with `default_book`, `feed_page`, `card_surface`, `hide_card`, and `unhide_card` (D2, D3); verify tests for "Done and hidden cards left out", "Retired card left out", "Second page", "Entry shape", "Hide and undo", and "Hidden card stays hidden after re-ingest" pass in `tests/test_card_feed.py` against a temp DB with hand-inserted cards.
- [ ] 1.3 Wire the four routes in `FeedAPI` and drop the `"dyl"` default; verify tests for "Unknown book", "No cards yet" (empty response), and a Flask test-client round trip pass.
- [ ] 1.4 Remove the briefing routes and helpers (D5) and their tests in `tests/test_feed_api.py`, `tests/test_coach.py`, and `tests/test_scheduler.py`; verify "Old endpoint" returns 404 and `uv run pytest tests/ -q` shows only the known `test_split_dyl_pdf` failure.

## 2. Frontend

- [ ] 2.1 Bring over from `origin/feat/card-first-feed` the layout changes in `feed/page.tsx` and `layout.tsx`, `ActivityDrawer.tsx`, the `useConversation.ts` and `ChatView.tsx` changes, and the `openui_prompt.py` fix, without its `server.py` patch; verify `npx next build` passes.
- [ ] 2.2 Write `useFeed.ts` and `FeedCardView.tsx` (D4) and switch `feed/page.tsx` to them; verify `npx next build` and `npx eslint src` pass.
- [ ] 2.3 Change `ActivityDrawer` to take a card id, load the surface, and render it with the surface library; remove its chat; verify `npx next build` passes.
- [ ] 2.4 Add the full-screen sheet below 768 px and the `?card=` URL state; verify `npx next build` passes.
- [ ] 2.5 Delete `ExerciseCard.tsx`, `ResurfacedIdeaCard.tsx`, `FadingIdeasCard.tsx`, `TodayHeader.tsx`, and `useBriefing.ts`; verify `grep -rn "useBriefing\|briefing/today" frontend/src` finds nothing and the build passes.
- [ ] 2.6 Run `lifekit ui` on a DB with generated `dyl` cards and ask the human to check "Open from the feed", "Phone view" (on the phone over Tailscale), "Hide and undo", "Header after a hide", and the empty state on a fresh DB.

## 3. Docs

- [ ] 3.1 Update `docs/arch/README.md` (feed data flow, D4 diagram, endpoint table), `AGENTS.md` (Architecture: endpoints, no default book), and `docs/arch/testing.md` (new and removed tests, test count); verify the docs name no removed endpoint.

## Workflow follow-up

- Move the KANBAN row for slice 5 to Done and archive this change after merge.
