# Proposal — card-activity-drawer

## Why

After feed-v1, the drawer shows a card's surface, but nothing the user writes
is kept, and the card's status never moves past `new`. The user's parked item 4
asks for chat and journal entries tied to one card through the card's id. This
is pulled into v1 in a minimal form, because a journal prompt or a worksheet
that forgets what the user wrote is not useful, and dogfood would measure
nothing.

Two bugs in today's chat also matter here:
- `post_message` grounds every reply on `app.config["book_id"]`, not on the
  conversation's own `book_id` (`lifekit/serve/server.py`, `_coach_messages`
  call).
- Grounding searches `book_chunks`, then falls back to whole chapters with term
  counting (`_retrieve_passages`, `_search_chapters`). book-model-v1 adds
  `passages` and `passages_fts`, which are the better source.

## What Changes

- Save the drawer's surface state per card: `card_state.surface_state` (JSON,
  at most 64 KB). The drawer sends it with `PUT /api/cards/<id>/surface-state`
  800 ms after the last change, and restores it with the renderer's
  `initialState` when the card opens again.
- Move the card's status in code:
  - `new` → `opened` when the drawer opens.
  - `opened` → `in_progress` on the first saved state.
  - → `done` when the user taps the surface's DoneButton (`@MarkDone()`), if
    `can_finish` allows it. The drawer shows the missing parts if it does not.
- `@CheckIn()` on a habit card logs a `checkin` event, at most one per card per
  day.
- One conversation per card: new column `conversations.card_id` with a unique
  index. `GET /api/cards/<id>/conversation` returns that card's conversation,
  or makes it on first use.
- The drawer shows the surface on top and the card's conversation below it.
  `AskCoach` sends its prompt into that conversation.
- Card chat grounding uses: the conversation's own book; the card's content and
  quote; the card's passage and its neighbours; the user's surface state (first
  2000 characters); and passages found with `passages_fts` for the message. Each
  card type adds its `coach_instruction` from `card_types.toml`.
- Composer (free) chat also moves to `passages_fts` and the conversation's
  book. Remove `_retrieve_passages`, `_search_chapters`, and the
  `python -m lifekit.store` ingest path. The `book_chunks` and `chapters` tables
  stay, frozen.
- `GET /api/cards/<id>` returns one card for deep links. `/feed?card=<id>`
  opens that card's drawer on load. Recent conversations that have a card id
  link to the card's drawer instead of `/c/<id>`.

## Capabilities

### New Capabilities

- `card-activity`: what the drawer saves for a card, how the card's status
  moves, the card's single conversation, and how that conversation is grounded.

### Modified Capabilities

None. `openspec/specs/` holds no capabilities yet.

## Impact

- Backend: `lifekit/serve/feed.py` (state, done, check-in, card lookup),
  new `lifekit/serve/coach.py` (grounding, moved out of `server.py`),
  `lifekit/serve/server.py` (routes; `post_message` uses the conversation's
  book), `lifekit/db/schema.py` (migration for two columns and one index).
- Removed: `lifekit/store/__main__.py` ingest entry and its `book_chunks`
  writer, the Makefile `ingest` target's old command, `_retrieve_passages`,
  `_search_chapters`.
- Frontend: `ActivityDrawer.tsx` (state, actions, embedded chat),
  `useConversation.ts` (load by card), the sidebar's recent-conversation links,
  `feed/page.tsx` (deep link).
- Depends on: feed-v1, card-generation, book-model-v1 (`passages_fts`),
  card-types-v1 (`next_status`, `can_finish`, `coach_instruction`).
