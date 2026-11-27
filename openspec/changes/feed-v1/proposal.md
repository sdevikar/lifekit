# Proposal — feed-v1

## Why

The v1 goal is a feed for one book that shows useful content, "not random
crap". Today `/feed` shows a daily briefing: one exercise, one resurfaced idea,
and up to five "fading" ideas (`lifekit/serve/server.py`: `_briefing`,
`_resurfaced_idea`, `_fading_ideas`). The ideas come out in `ORDER BY id`, the
book id defaults to `"dyl"`, and the cards are fixed React components
(`ExerciseCard.tsx`, `ResurfacedIdeaCard.tsx`, `FadingIdeasCard.tsx`).

Roadmap v2 parks spaced repetition and daily selection (intent.md → "PoC limits"
and ASSUMPTIONS A29). So the feed becomes simple: every card of the book that
the user has not hidden or finished, in reading order. The cards are the
generated, validated programs from card-generation.

The `feat/card-first-feed` branch already moves the feed to a card list with a
side drawer (`ActivityDrawer.tsx`). This change keeps its layout and replaces
its data source.

## What Changes

- New endpoint `GET /api/feed?book_id=&cursor=` returns the book and a page of
  20 cards in position order. It leaves out hidden, done, and retired cards.
  With no `book_id`, it uses the most recent book that has cards. The
  hardcoded `"dyl"` default goes away.
- New endpoints `POST /api/cards/<id>/hide` ("Not useful") and
  `DELETE /api/cards/<id>/hide` (Undo). Both log an event, so the dogfood
  review can count "Not useful" taps.
- New tables `card_state` (status per card) and `card_events` (append-only log).
- The feed page renders each card's `card_ui` with the OpenUI `Renderer` and the
  card library. The `@OpenActivity()` action opens the side drawer.
- The drawer renders the card's `surface_ui` with the surface library. This
  slice does not save what the user types; card-activity-drawer adds that.
- "Not useful" is a code-owned menu on each card, not part of the generated
  program, so every card has it. Hiding shows an Undo toast.
- Below 768 px wide, the drawer becomes a full-screen sheet with a back button.
- **BREAKING (internal only):** delete `/api/briefing/today`,
  `/api/completions`, `/api/idea-signals`, the briefing helpers, the old feed
  components, `useBriefing`, and their tests. The old tables stay in the
  database, unused.
- Take from `feat/card-first-feed`: the drawer layout in `feed/page.tsx` and
  `layout.tsx`, `ActivityDrawer.tsx`, and the one-line fix in
  `lifekit/serve/openui_prompt.py`. Leave out its `server.py` regex patch and
  its three proposals (superseded, see KANBAN).

## Capabilities

### New Capabilities

- `card-feed`: which cards the feed shows, in what order and page size, how
  the user hides a card and undoes that, and how a card opens its drawer.

### Modified Capabilities

None. `openspec/specs/` holds no capabilities yet.

## Impact

- Backend: `lifekit/serve/server.py` (new routes, removed routes and helpers),
  new `lifekit/serve/feed.py`, `lifekit/db/schema.py` (two tables).
- Frontend: `frontend/src/app/feed/page.tsx`, new
  `frontend/src/components/feed/FeedCardView.tsx`,
  `frontend/src/components/ActivityDrawer.tsx` (from the branch, changed), new
  `frontend/src/hooks/useFeed.ts`; delete `ExerciseCard.tsx`,
  `ResurfacedIdeaCard.tsx`, `FadingIdeasCard.tsx`, `TodayHeader.tsx`,
  `useBriefing.ts`.
- Tests: rewrite `tests/test_feed_api.py`; drop briefing cases in
  `tests/test_coach.py` and `tests/test_scheduler.py` that call removed code.
- Depends on: card-generation (the `cards` table and both libraries).
