# Proposal — feed-v1

## Why

The v1 goal is a feed for one book that shows useful content. Today `/feed`
shows a daily briefing: one exercise, one resurfaced idea, and up to five
"fading" ideas (`lifekit/serve/server.py`: `_briefing`, `_resurfaced_idea`,
`_fading_ideas`). The ideas come out in `ORDER BY id`, so the feed always shows
the Dedication and Contents ideas. The book id defaults to `"dyl"`, and the
cards are fixed React components (`ExerciseCard.tsx`, `ResurfacedIdeaCard.tsx`,
`FadingIdeasCard.tsx`).

v1 has one screen, the feed (ROADMAP D1). It shows every card of the book in
reading order. The user responds to a card with a reaction or a comment. Cards
have no done state, so the feed opens at the furthest card the user responded
to (ROADMAP D9). This slice builds the feed and the reactions. card-comments
adds the thread under each card.

## What Changes

- New endpoint `GET /api/feed?book_id=&after=&before=` returns the book, a page
  of 20 cards in position order, and cursors for the pages before and after.
  With no cursor, the page starts at the furthest card the user responded to.
  It leaves out retired and disliked cards. With no `book_id`, it uses the most
  recent book that has cards. The hardcoded `"dyl"` default goes away.
- New endpoint `PUT /api/cards/<id>/reaction` sets like, dislike, or none, and
  logs the change, so the dogfood review can count dislikes and active days.
- New tables `card_state` (reaction and "responded" flag per card) and
  `card_events` (append-only reaction log).
- The feed page renders each card's `card_ui` with the OpenUI `Renderer` and the
  card library, inside a `CardContext` provider (card-generation D4).
- Code draws like and dislike under each card, outside the generated program. A
  disliked card folds into one line, "Marked not useful · Undo".
- One centered column at every screen width. A "Show earlier cards" button at
  the top loads the page before; scrolling to the end loads the page after.
- The header shows the book title, a plain card count, and the theme toggle.
- **BREAKING (internal only):** delete `/api/briefing/today`,
  `/api/completions`, `/api/idea-signals`, the briefing helpers, the old feed
  components, `useBriefing`, and their tests. The old tables stay in the
  database, unused.

## After this slice

What you will see in the app:
- The feed shows the book's cards in reading order, 20 at a time. More cards
  load when you scroll to the end.
- The header shows the book title, the card count, and the theme toggle.
- Like and dislike under each card. A disliked card folds into one line,
  "Marked not useful · Undo".
- When you open the feed again, it starts at the furthest card you reacted to.
  "Show earlier cards" loads the cards before it.
- The old briefing is gone: today's exercise, "Mark done", and "still with
  me?".

What is not there yet (expected, not a bug):
- No comment box. You cannot write anything on a card, and the coach does not
  reply. Slice 6 adds both.
- Question cards keep the author's answer hidden. Only a comment opens it, in
  slice 6.
- If the database has no cards, the feed says "No cards yet. Run `lifekit
  ingest <file>`." Run the ingest stages from slices 2 to 4 on the home
  workstation first.

## Capabilities

### New Capabilities

- `card-feed`: which cards the feed shows, in what order and page size, where
  it starts, and how the user reacts to a card.

### Modified Capabilities

None. `openspec/specs/` holds no capabilities yet.

## Impact

- Backend: `lifekit/serve/server.py` (new routes, removed routes and helpers),
  new `lifekit/serve/feed.py`, `lifekit/db/schema.py` (two tables).
- Frontend: `frontend/src/app/feed/page.tsx`, new
  `frontend/src/components/feed/FeedCardView.tsx`,
  `frontend/src/components/feed/ReactionBar.tsx`, new
  `frontend/src/hooks/useFeed.ts`; delete `ExerciseCard.tsx`,
  `ResurfacedIdeaCard.tsx`, `FadingIdeasCard.tsx`, `TodayHeader.tsx`,
  `useBriefing.ts`.
- Tests: rewrite `tests/test_feed_api.py`; drop briefing cases in
  `tests/test_coach.py` and `tests/test_scheduler.py` that call removed code.
- Depends on: feed-only-ui (no sidebar), card-generation (the `cards` table and the card library),
  card-types-v1 (`comment_hint`).
- The `feat/card-first-feed` branch is not used (ROADMAP D1).
