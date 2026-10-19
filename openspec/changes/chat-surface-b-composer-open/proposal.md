# Chat Surface b — Composer + Open Conversation — Proposal

Slice **b** of three splitting [`../chat-surface/`](../chat-surface/).
Depends on [`../chat-surface-a-route-list/`](../chat-surface-a-route-list/),
which creates the `/chat` route and the conversation list. Followed by
[`../chat-surface-c-entry-points/`](../chat-surface-c-entry-points/).

## Why

Slice a lists conversations but cannot open one, and there is no way to start a
new chat. This slice wires both: clicking a conversation opens it in the right
pane, and the empty state's composer creates a new one.

## What Changes

- **`frontend/src/app/chat/page.tsx`** — add `selectedConvId` (local `useState`,
  starts `null`). When non-null, the right pane renders `<ChatView convId={selectedConvId} />`.
  When null, the right pane renders `<MasterComposer onSubmit={...} />`.
  `ConversationsList` gets an `onOpen(id)` prop wired to `setSelectedConvId`.

- **`frontend/src/components/ChatView.tsx`** (new, `"use client"`) — the
  conversation view for the right pane. Composes `MessageList` + `ChatInput` and
  a title header. Calls `useConversation(convId)` itself; the hook is unchanged.
  Passes `pending={sending}` to `MessageList`. No `← Feed` button.

- **`frontend/src/components/feed/MasterComposer.tsx`** — wire into the `/chat`
  empty state. `onSubmit(text)` calls `POST /api/conversations` with
  `seed_kind: "composer"`, then `setSelectedConvId(newId)`. The composer is the
  only path to an unseeded chat.

- **`frontend/src/components/feed/ConversationsList.tsx`** — rows become
  `<button>` with `onClick={() => onOpen(id)}`. Slice a shipped them as
  non-interactive content; this is the slice that gives them a purpose.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: selecting a conversation in the `/chat` list opens it
  in the right pane. The composer in the empty state creates a new conversation
  and opens it.

## Not In Scope

- The `← Feed` button's removal from `/c/[id]` — slice c, which owns routing.
- Deep links and "Talk about this" entry points — slice c.
- `MasterComposer` restyle — it is wired in as-is.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`, no new problems.
2. Clicking a conversation in the list opens it in the right pane with its
   messages and input.
3. Clicking a second conversation swaps the right pane's content; the previous
   conversation's transcript is not left on screen.
4. With `selectedConvId` null, the right pane shows the composer, not a blank
   area.
5. Submitting the composer creates a conversation via `POST /api/conversations`
   and opens it in the right pane.
6. The header shows the conversation title; there is no `← Feed` button.
7. Sending a message from `ChatView` behaves as it does today: the message
   appears immediately, the pending row shows, the reply lands.
8. Both themes render correctly.
9. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
10. `docs/product/KANBAN.md` updated in the same change.
