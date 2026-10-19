# Chat Surface a — Route + Conversation List — Proposal

Slice **a** of three splitting [`../chat-surface/`](../chat-surface/).
Independently shippable: the `/chat` route exists and lists conversations, but
clicking one does nothing yet. Followed by
[`../chat-surface-b-composer-open/`](../chat-surface-b-composer-open/) and
[`../chat-surface-c-entry-points/`](../chat-surface-c-entry-points/).

**Depends on [`../sidebar-nav-model/`](../sidebar-nav-model/)**, which gives the
sidebar its single-column nav rows.

## Why

The Chat tab is a placeholder and the nav row's `+` is a dead button. There is no
surface anywhere that lists conversations — `GET /api/conversations` is implemented
and tested and nothing calls it. This slice creates the `/chat` destination and
puts the list there.

## What Changes

- **`frontend/src/components/Sidebar.tsx`** — remove the `+` from the Chat nav row
  (`TRAILING_PLUS` entry for `chat`). The row becomes a link to `/chat` via
  `router.push("/chat")`. The `inert` flag and hover-reveal logic for Chat are
  deleted.

- **`frontend/src/app/chat/page.tsx`** (new, `"use client"`) — the `/chat` route.
  Two-pane layout: `ConversationsList` on the left, an empty state on the right
  ("Select a conversation or start a new one"). No `selectedConvId` yet — slice b
  adds it. The page owns `useConversations` and passes the list down.

- **`frontend/src/hooks/useConversations.ts`** (new) — fetches
  `GET /api/conversations`, exposes `{ conversations, loading, error }`. No
  `refresh`: the page unmounts when the user navigates away, so a plain
  mount-effect refetches on return.

- **`frontend/src/components/feed/ConversationsList.tsx`** — repurpose for the
  `/chat` left pane. Drop the `lk-card` wrapper and `Coaching` badge. Add an empty
  state. Rows render as non-interactive content (not `<button>`) — slice b makes
  them clickable. No `onOpen` prop yet.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: the sidebar Chat row navigates to `/chat`, which lists
  the current book's conversations with titles and dates.

## Not In Scope

- **Opening a conversation.** Rows are not clickable until slice b.
- **Starting a new chat.** The composer arrives in slice b.
- **Search, filtering, renaming, deletion.** Not in the API; list is short.
- Anything on the feed, or in routing beyond `/chat` — slices b and c.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`, no new problems.
2. Clicking the Chat nav row navigates to `/chat`.
3. The `/chat` page shows the conversation list on the left, with titles and
   dates, matching `GET /api/conversations`.
4. The list is empty-state clean when there are no conversations.
5. Conversation rows are **not** focusable and show no pointer cursor.
6. No `+` appears on the Chat nav row in any state.
7. The list renders correctly in both light and dark themes.
8. The feed page is unchanged and still builds.
9. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
10. `docs/product/STATUS.md` updated in the same change.
