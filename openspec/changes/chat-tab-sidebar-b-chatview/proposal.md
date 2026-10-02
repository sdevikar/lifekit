# Chat Tab b — ChatView + Selection — Proposal

Slice **b** of three splitting [`../chat-tab-sidebar/`](../chat-tab-sidebar/).
Depends on
[`../chat-tab-sidebar-a-conversation-list/`](../chat-tab-sidebar-a-conversation-list/),
which leaves the `onOpen(id)` handler in `Sidebar.tsx` waiting for somewhere to
go. Followed by
[`../chat-tab-sidebar-c-entry-points/`](../chat-tab-sidebar-c-entry-points/).

## Why

Slice a lists conversations but cannot open one. Today the conversation view
lives only in the route component `app/c/[id]/page.tsx` — a page that owns its
own header, its own back button, and its own scroll container. To put a
conversation in the Chat tab's main area, that view has to stop being a route.

The current page cannot be reused as-is: `← Feed` navigates to `/feed`
(`page.tsx:30`), which is wrong once the sidebar owns navigation, and its header
duplicates what the sidebar already shows.

## What Changes

- **`frontend/src/components/ChatView.tsx`** (new, `"use client"`) — the
  conversation view for the main area. Composes `MessageList` + `ChatInput` and
  a title header. It calls `useConversation(selectedConvId)` itself; the hook is
  unchanged.

  Both child components are now final-shaped — Markdown rendering and the
  pending state landed 2026-10-01 — so this is a move, not a rewrite. `ChatView`
  must pass `pending={sending}` to `MessageList`; that prop exists precisely so
  this component does not have to invent the wiring.

- **`frontend/src/components/TabContext.tsx`** — add `selectedConvId` and
  `setSelectedConvId` to the existing context value. The parent proposal offers
  "TabContext or a separate ChatContext"; TabContext wins. It is already the
  single piece of cross-component UI state above both the sidebar and the main
  area, and a second context for two adjacent values means two providers and two
  `useContext` throws to maintain.

  `selectedConvId` starts `null`, which is the "no conversation open" state and
  what `ChatView` renders its empty state for.

- **`frontend/src/components/TabContent.tsx`** — render `<ChatView />` when
  `activeTab === "chat"` instead of `Coming soon.`. Journal and settings keep
  their placeholder.

- **`frontend/src/components/Sidebar.tsx`** — wire the `onOpen` handler left
  dangling in slice a to `setSelectedConvId(id)`. Delete the `TODO`.

- **`app/c/[id]/page.tsx`** — **untouched in this slice.** It keeps working as a
  standalone page until slice c converts it to a deep-link wrapper. Deleting the
  back button here would break the only working way to reach a conversation.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: selecting a conversation in the Chat panel opens it
  in the main area. With no conversation selected, the Chat tab shows an empty
  state inviting a new chat.

## Not In Scope

- The `← Feed` button's removal — slice c, which owns routing.
- Deep links and the "Talk about this" entry points — slice c.
- `MasterComposer` restyle — see the parent proposal's open questions.
- Deleting `app/c/[id]/page.tsx` — slice c turns it into a wrapper rather than
  removing it, so the URL keeps working.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`, no new problems.
2. Clicking a conversation in the Chat panel opens it in the main area with its
   messages and input.
3. Clicking a second conversation swaps the main area's content, and the
   previous conversation's transcript is not left on screen.
4. With `selectedConvId` null, the Chat tab shows an empty state — not a blank
   area and not `Coming soon.`
5. The header shows the conversation title, and there is **no** `← Feed` button
   (navigation is the sidebar's job) — but `/c/[id]` still works as before,
   because this slice does not touch that route.
6. Sending a message from `ChatView` behaves as it does today: the message
   appears immediately, the pending row shows, the reply lands.
7. The title header and scroll behaviour read correctly in both light and dark
   themes.
8. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
9. `docs/product/STATUS.md` updated in the same change.