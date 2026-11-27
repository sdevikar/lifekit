# Proposal — retire-free-chat

## Why

v1 has one screen, the feed, and one way to talk to the coach, a comment on a
card (ROADMAP D1, D10). After card-comments, the old free chat is a second
path: the `/chat` pages, the composer, the sidebar with recent conversations,
and the `/journal` placeholder. Two paths split the user's history, and the
sidebar takes width from the single column. This slice removes them.

## What Changes

- **BREAKING (internal only):** delete the pages `/chat`, `/chat/<id>`,
  `/c/<id>`, and `/journal`. Each of these URLs redirects to `/feed`, so old
  bookmarks still land somewhere.
- Delete the sidebar, its recent-conversations list, the tab context, the chat
  view and its input, the free-chat composer, the conversation hooks, and the
  `useConversation` regression test.
- Delete `MessageList.tsx`. card-comments renders coach replies in
  `CommentThread` with the OpenUI renderer, so nothing else uses it.
- `app/layout.tsx` renders the page alone, with no sidebar or tab wrapper. The
  page title and description match the feed.
- Delete the routes `GET`/`POST /api/conversations`, `GET`/`DELETE
  /api/conversations/<id>`, and `POST /api/conversations/<id>/messages`, with
  `_generate_title` and their tests.
- Keep the `conversations` and `messages` tables. Card threads use them. Old
  free-chat rows stay, unread.

## Capabilities

### New Capabilities

- `free-chat-removal`: what URLs and API routes no longer exist, and where an
  old URL goes.

### Modified Capabilities

None. `openspec/specs/` holds no capabilities yet.

## Impact

- Frontend: delete `app/chat/`, `app/c/`, `app/journal/`,
  `components/Sidebar.tsx`, `components/sidebar/RecentConversations.tsx`,
  `components/TabContext.tsx`, `components/TabContent.tsx`,
  `components/ChatView.tsx`, `components/conversation/ChatInput.tsx`,
  `components/conversation/MessageList.tsx`,
  `components/feed/MasterComposer.tsx`, `hooks/useConversations.ts`,
  `hooks/useConversation.ts`, `frontend/test_useConversation.mjs`; edit
  `app/layout.tsx` and `next.config.ts` (redirects). `components/feed/icons.tsx`
  keeps only the icons still used.
- Backend: `lifekit/serve/server.py` (routes removed),
  `tests/test_feed_api.py` (conversation cases removed).
- Docs: `AGENTS.md` (Verification no longer names the `useConversation` test),
  `docs/arch/testing.md`, `docs/arch/README.md`.
- Depends on: card-comments (the only remaining coach path).
