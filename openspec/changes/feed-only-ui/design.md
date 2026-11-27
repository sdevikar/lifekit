# Design — feed-only-ui

## Context

- `app/layout.tsx` wraps every page in `TabProvider`, `Sidebar`, and
  `TabContent`.
- `Sidebar.tsx` imports `TabContext` and `RecentConversations`.
  `RecentConversations` imports `useConversations`.
- `app/chat/page.tsx` imports `MasterComposer`, `ChatView`, and
  `useConversations`. `ChatView` imports `useConversation`, `MessageList`, and
  `ChatInput`. `ChatInput` and `MasterComposer` import `SendIcon` from
  `feed/icons.tsx`. Nothing imports its other export, `ConversationIcon`.
- `app/feed/page.tsx` calls `useBriefing().createConversation` and then
  `router.push("/c/<id>")` from three "Talk about" buttons (lines 24–56).
- `frontend/test_useConversation.mjs` drives `useConversation` against a
  running UI.
- `lifekit/serve/server.py`: the five conversation routes are the only callers
  of `_generate_title` and `_coach_messages`. `_coach_messages` is the only
  caller of `_retrieve_passages`, which calls `_fts_query` and
  `_search_chapters`. The briefing routes use `_book_info`, which stays.

## Goals / Non-Goals

**Goals:**
- The feed is the only page, and no code for free chat stays behind.
- Old URLs land on the feed.

**Non-Goals:**
- No change to the briefing cards beyond removing the chat buttons. feed-v1
  replaces them.
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

1. Edit `app/layout.tsx` to render `children` inside `<main>` only. Keep the
   theme script and the metadata ("Daily coaching: one exercise, one idea.").
2. Remove the "Talk about" buttons and their `onTalkAbout` props, and
   `createConversation` from `useBriefing`.
3. Delete the pages, then every component and hook that no file imports.
4. Run `npx next build`. The build fails on any import that is left.

### D3. Server routes and helpers

Delete the five conversation routes and the helpers in Context that only they
reach. card-comments writes new grounding in `lifekit/serve/coach.py` on
`passages_fts`, so nothing waits for the old helpers. The old code stays in git
history. card-comments names its three bugs so the new code does not repeat
them.

### D4. Keep the OpenUI library

`frontend/src/lib/openui.tsx`, `frontend/scripts/gen_openui_prompt.ts`, and
`lifekit/serve/openui_prompt.py` have no reader after this slice. They stay,
because card-generation splits the library and card-comments renders coach
replies with it (ROADMAP D6). Deleting them now and adding them back two
slices later would only add churn.

## Risks / Trade-offs

- [From this slice until card-comments, the user cannot talk to the coach] →
  Accepted. LifeKit has one dogfood user, and nobody uses the app between
  slices. The briefing cards still work: mark an exercise done, answer "still
  with me?".
- [A question that fits no card has nowhere to go] → Accepted (ROADMAP D10).
  The v2 "+" button and v4 sharing cover it.
- [Old free-chat history becomes unreachable in the UI] → The rows stay in
  SQLite. Accepted for a single dogfood user.

## Migration Plan

1. One commit: layout, button removal, deletions, redirects, route removal,
   docs.
2. Rollback: revert the commit.

## Open Questions

None.
