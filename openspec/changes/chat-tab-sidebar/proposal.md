# Chat Tab — Proposal

## Why

Conversations are currently separate pages at `/c/[id]`, and the "Recent Conversations" card sits at the bottom of the feed. In the new sidebar layout, conversations belong in the Chat tab: a collapsible list of recent chats in the sidebar panel, with the active conversation shown in the main area. This matches the DeepTutor/ChatGPT pattern and makes conversations always one click away.

## What Changes

- **`frontend/src/components/Sidebar.tsx`** — when Chat tab is active, the panel shows a **collapsible conversation list** (reuses the existing `ConversationsList` component, restyled for sidebar). A "New chat" button at the top creates a new conversation via the composer. Hovering over the "Chat" panel title shows a `+` icon to start a new chat.

- **`frontend/src/components/ChatView.tsx`** (new, `"use client"`) — the conversation view for the main area:
  - Renders `MessageList` + `ChatInput` (reuses existing components).
  - Shows conversation title in a header bar (no back button — navigation is via the sidebar Feed tab).
  - Handles loading and error states (reuses patterns from `app/c/[id]/page.tsx`).

- **`frontend/src/hooks/useConversation.ts`** — unchanged. `ChatView` calls it with the selected conversation ID.

- **`frontend/src/hooks/useBriefing.ts`** — add a `listConversations` function that calls `GET /api/conversations` and returns the list. Used by the sidebar panel.

- **`frontend/src/app/feed/page.tsx`** — the "Talk about this" button handler changes: instead of `router.push(/c/${convId})`, it calls `setActiveTab("chat")` and sets the selected conversation ID. The new conversation opens in the Chat tab's main area.

- **`frontend/src/app/c/[id]/page.tsx`** — becomes a thin wrapper: on mount, switches to Chat tab and sets the selected conversation ID. Preserves deep-linking (pasting a `/c/[id]` URL opens that conversation in the Chat tab). The `<- Feed` button is removed; navigation back to feed is via the sidebar Feed tab icon.

- **`frontend/src/components/MasterComposer.tsx`** — restyled as a **floating input** (centered, pill-shaped, elevated with shadow) instead of a full-width fixed bar. Stays in the feed's main area.

- **Selected conversation state** — lives in `TabContext` or a separate `ChatContext`: `{ selectedConvId, setSelectedConvId }`. The sidebar sets it, `ChatView` reads it.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: chat navigation. Conversations are listed in the Chat tab's sidebar panel. Clicking one opens it in the main area. "Talk about this" on feed cards creates a conversation and switches to the Chat tab. Deep-linking to `/c/[id]` auto-switches to the Chat tab. Navigation back to feed is via the sidebar Feed tab icon (no `<- Feed` button).

## Not In Scope

- Journal functionality (slice 3).
- Books tab (deferred).
- Conversation search or filtering (list is short, no need yet).
- Conversation deletion or renaming (not in current API).

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`.
2. Clicking the Chat icon in the sidebar shows the conversation list in the panel.
3. Clicking a conversation opens it in the main area with messages and input.
4. "Talk about this" on a feed card creates a new conversation and switches to the Chat tab with that conversation open.
5. Pasting a `/c/[id]` URL in a new tab opens that conversation in the Chat tab.
6. The MasterComposer is restyled as a floating input in the feed.
7. The conversation list in the sidebar shows conversation titles and dates (reuses existing `ConversationsList` styling).
8. Hovering over the "Chat" panel title shows a `+` icon to start a new chat.
9. The `<- Feed` button is removed from the conversation view; navigation back to feed is via the sidebar Feed tab icon.
10. `uv run pytest` shows no new failures beyond the known `test_split_dyl_pdf` (BACKLOG P2).
11. `docs/product/STATUS.md` updated in the same change.
