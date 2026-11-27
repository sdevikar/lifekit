# Proposal — feed-only-ui

## Why

v1 has one screen, the feed (ROADMAP D1). The only way to talk to the coach
is a comment on a card (ROADMAP D2, D10). Today the app on `main` still has the
PoC layout: a left sidebar with Feed, Journal, and Chat links and a list of
recent conversations. The sidebar takes width from the single column and
points the user at free chat, which v1 retires.

This slice comes first, before slices 1 to 6. It makes the app match the v1
direction now, so every later slice builds on a feed-only layout and no slice
has to work around the old chat.

## What Changes

- **BREAKING (internal only):** delete the pages `/chat`, `/chat/<id>`,
  `/c/<id>`, and `/journal`. Each of these URLs redirects to `/feed`, so old
  bookmarks still land somewhere.
- Delete the sidebar, its recent-conversations list, the tab context, the chat
  view and its input, the message list, the free-chat composer, the
  conversation hooks, and the `useConversation` regression test.
- Remove the "Talk about this" buttons from the current briefing cards, and
  `createConversation` from `useBriefing`. These buttons open the chat page,
  which no longer exists.
- `app/layout.tsx` renders the page alone, with no sidebar or tab wrapper.
- Delete the routes `GET`/`POST /api/conversations`, `GET`/`DELETE
  /api/conversations/<id>`, and `POST /api/conversations/<id>/messages`.
  Delete the helpers only they use: `_generate_title`, `_coach_messages`,
  `_retrieve_passages`, `_search_chapters`, and `_fts_query`. Delete their
  tests.
- Keep the `conversations` and `messages` tables and their rows. card-comments
  uses the tables for card threads.
- Keep the OpenUI chat library (`frontend/src/lib/openui.tsx`), its prompt
  generator, and `lifekit/serve/openui_prompt.py`. card-generation and
  card-comments build on them.

## After this slice

What you will see in the app:
- The feed page alone, with no left sidebar.
- Old links (`/chat`, `/chat/<id>`, `/c/<id>`, `/journal`) open the feed.
- The same old feed as before: today's exercise, a resurfaced idea, and the
  fading ideas. "Mark done" and the "still with me?" buttons still work.

What is not there yet (expected, not a bug):
- You cannot talk to the coach. The "Talk about this" buttons are gone. Card
  comments bring the coach back in slice 6.
- The feed still shows the same front-matter ideas every day. Slice 5 replaces
  the feed with real cards.
- Old chats stay in the database, but no page shows them.

## Capabilities

### New Capabilities

- `feed-only-ui`: the feed is the only page, old URLs redirect to it, and the
  free-chat API is gone.

### Modified Capabilities

None. `openspec/specs/` holds no capabilities yet.

## Impact

- Frontend: delete `app/chat/`, `app/c/`, `app/journal/`,
  `components/Sidebar.tsx`, `components/sidebar/RecentConversations.tsx`,
  `components/TabContext.tsx`, `components/TabContent.tsx`,
  `components/ChatView.tsx`, `components/conversation/ChatInput.tsx`,
  `components/conversation/MessageList.tsx`,
  `components/feed/MasterComposer.tsx`, `components/feed/icons.tsx` (no
  remaining user), `hooks/useConversations.ts`, `hooks/useConversation.ts`,
  and `frontend/test_useConversation.mjs`. Edit `app/layout.tsx`,
  `app/feed/page.tsx`, `ExerciseCard.tsx`, `ResurfacedIdeaCard.tsx`,
  `FadingIdeasCard.tsx`, `hooks/useBriefing.ts`, and `next.config.ts`
  (redirects).
- Backend: `lifekit/serve/server.py` (routes and helpers removed),
  `tests/test_feed_api.py` (`TestConversations` and `TestConversationMessages`
  removed; the schema tests for the two tables stay).
- Docs: `AGENTS.md` (Verification and Architecture no longer name the
  conversation routes or the `useConversation` test), `docs/arch/testing.md`,
  `docs/arch/README.md`.
- Depends on: nothing. This is slice 0.
- Gap: from this slice until card-comments (slice 6), the app has no way to
  talk to the coach. See design.md, Risks.
