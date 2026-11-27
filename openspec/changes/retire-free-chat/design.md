# Design — retire-free-chat

## Context

- `app/layout.tsx` wraps every page in `TabProvider`, `Sidebar`, and
  `TabContent`.
- `Sidebar.tsx` imports `TabContext` and `RecentConversations`;
  `RecentConversations` imports `useConversations`.
- `app/chat/page.tsx` imports `MasterComposer`, `ChatView`, and
  `useConversations`. `ChatView` imports `useConversation`, `MessageList`, and
  `ChatInput`. `ChatInput` and `MasterComposer` import `feed/icons.tsx`.
- `frontend/test_useConversation.mjs` drives `useConversation` against a
  running UI.
- After card-comments, the feed uses `CommentThread`, `CommentBox`, and
  `useComments`, and none of the files above.

## Goals / Non-Goals

**Goals:**
- One screen and one coach path, with no dead code left behind.
- Old URLs land on the feed.

**Non-Goals:**
- No change to the `conversations` or `messages` tables or their rows.
- No export of old free-chat history. Nobody asked for it, and the rows stay.
- No new navigation. The feed header is the only chrome.

## Decisions

### D1. Redirects in `next.config.ts`

`redirects()` returns entries with `permanent: false` for `/chat`, `/chat/:id`,
`/c/:id`, and `/journal`, each to `/feed`. A temporary redirect keeps the
browser from caching it, in case a later stage reuses a path.

Alternative: keep stub pages that call `redirect()`. Rejected: four files that
exist only to redirect.

### D2. Delete order

1. Edit `app/layout.tsx` to render `children` inside `<main>` only.
2. Delete the pages, then every component and hook that no file imports.
3. Run `npx next build`. The build fails on any import that is left.

### D3. Server routes

Delete the five conversation routes and `_generate_title`. Any code that
card-comments left calling `coach.build_messages` with no card goes too, so
`build_messages` always takes a card id.

## Risks / Trade-offs

- [A question that fits no card has nowhere to go] → Accepted (ROADMAP D10).
  The v2 "+" button and v4 sharing cover it.
- [Old free-chat history becomes unreachable in the UI] → The rows stay in
  SQLite. Accepted for a single dogfood user.

## Migration Plan

1. One commit: layout, deletions, redirects, route removal, docs.
2. Rollback: revert the commit.

## Open Questions

None.
