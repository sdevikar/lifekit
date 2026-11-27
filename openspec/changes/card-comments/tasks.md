# Tasks — card-activity-drawer

## 1. Backend state

- [ ] 1.1 Add the D1 migration to `lifekit/db/schema.py`; verify `init_db()` runs twice on a fresh DB and on a dogfood copy with old conversations.
- [ ] 1.2 Add `get_card`, `open_card`, `save_state`, `finish_card`, and `check_in` to `lifekit/serve/feed.py` (D2) using `next_status` and `can_finish`; verify tests for "Open then type", "Reopen a done card", "State too large", "Worksheet with a missing field", "Insight got it", and "Second check-in on one day" pass in `tests/test_card_activity.py`.
- [ ] 1.3 Add `card_conversation` (D3); verify tests for "Reopen keeps the chat" (same id twice) and "Two requests at once" (two connections, same id) pass.
- [ ] 1.4 Wire the D2 routes in `FeedAPI` and drop feed-v1's `/surface` route; verify a Flask test-client round trip of open → save → done passes.

## 2. Grounding

- [ ] 2.1 Move `_fts_query` and the message builder into `lifekit/serve/coach.py` and rewrite it per D4; make `post_message` pass the conversation's `book_id` and `card_id`; verify tests for "Grounded on the card's book" and "Coach sees the user's entry" pass in `tests/test_coach.py` with a stub provider.
- [ ] 2.2 Remove the old grounding path (D6); verify `grep -rn "_search_chapters\|_retrieve_passages\|lifekit.store --pdf" lifekit Makefile AGENTS.md` finds nothing and `uv run pytest tests/ -q` shows only the known `test_split_dyl_pdf` failure.

## 3. Frontend

- [ ] 3.1 Change `ActivityDrawer` to load `GET /api/cards/<id>`, call open, restore with `initialState`, and save with the debounce and flush (D5); verify `npx next build` passes.
- [ ] 3.2 Handle `MarkDone`, `CheckIn`, and `ToAssistant` in `onAction` and show the missing-parts message; verify `npx next build` passes.
- [ ] 3.3 Embed `ChatView` for the card's conversation under the surface; let `useConversation` take a conversation id from the card; verify the `useConversation` regression test still passes (`node --experimental-strip-types frontend/test_useConversation.mjs`).
- [ ] 3.4 Open the drawer from `/feed?card=<id>` on load, show "This card no longer exists." for an unknown id, and link card conversations in `RecentConversations.tsx` to `/feed?card=<card_id>`; verify `npx next build` and `npx eslint src` pass.
- [ ] 3.5 Run `lifekit ui` and ask the human to check "Draft survives a reload", "Reopen keeps the chat", "Ask from an insight", "Recent conversation link", the worksheet missing-field message, and a habit check-in, on desktop and on the phone.

## 4. Docs

- [ ] 4.1 Update `docs/arch/README.md` (D4 and D5 diagrams, endpoint table), `AGENTS.md` (quick reference ingest command, endpoints), and `docs/arch/testing.md` (new tests, count); verify the docs name no removed function or command.

## Workflow follow-up

- Move the KANBAN row for slice 6 to Done and archive this change after merge.
