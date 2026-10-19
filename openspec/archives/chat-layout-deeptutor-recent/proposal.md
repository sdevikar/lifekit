# Chat Layout — DeepTutor-style Recent Sidebar — Proposal

**Supersedes:** [`../chat-surface-c-entry-points/`](../chat-surface-c-entry-points/)
(two-pane chat list + entry points). That proposal assumed the two-pane layout
stayed; this one removes it.

## Why

The two-pane `/chat` layout (conversation list left, conversation right) wastes
a third of the viewport on a list of a handful of items, and the conversation
list belongs in the sidebar — that is where DeepTutor puts it, and where the
user expects it. DeepTutor's chat is single-column: conversation + composer
full-width, with conversation history as a collapsible section in the sidebar.

This proposal makes LifeKit's chat match: `/chat` becomes single-column, and
the sidebar gains a collapsible "Recent" section listing conversations, grouped
by recency (Today / Yesterday / Last 7 days / Earlier), with rename and delete.

## What Changes

### 1. `/chat` route — single-column

- **`frontend/src/app/chat/page.tsx`** — remove the two-pane layout. The page
  shows either the active conversation (`ChatView`) or the `MasterComposer`
  empty state. No `ConversationsList`, no left pane.
- **`frontend/src/components/feed/ConversationsList.tsx`** — no longer used
  on `/chat`. Repurposed for the sidebar (below).
- The conversation header in `ChatView.tsx` gains a title that can be renamed
  inline (click to edit, Enter to save, Escape to cancel), matching
  DeepTutor's pattern.

### 2. Sidebar — collapsible "Recent" section

- **`frontend/src/components/Sidebar.tsx`** — when the Chat tab is active, the
  sidebar panel shows a "Recent" section below the nav rows:
  - Collapsible: click the "Recent" header to expand/collapse the list.
  - Grouped by recency: Today, Yesterday, Last 7 days, Earlier.
  - Each row: conversation title (truncated) + last message preview (one line).
  - Hover reveals rename (pencil) and delete (trash) icons.
  - Click navigates to `/chat/<conversation-id>`.
  - A "New chat" button at the top of the section.
- The conversation data comes from `GET /api/conversations` (already exists).
- Rename and delete call the existing `PATCH/DELETE /api/conversations/<id>`
  endpoints (if they exist) or are deferred if the API doesn't support them yet.

### 3. Routing

- `/chat` — single-column chat view (active conversation or composer).
- `/chat/<conversation-id>` — deep link to a specific conversation.
- The old `/c/<id>` route is preserved as a redirect to `/chat/<id>` for
  backward compatibility with any existing links.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: the conversation list lives in the sidebar as a
  collapsible "Recent" section. `/chat` is single-column. Conversations are
  deep-linkable at `/chat/<id>`.

### New Capabilities

- `chat-recent-sidebar`: the sidebar shows a collapsible list of recent
  conversations grouped by recency, with rename and delete affordances.

## Not In Scope

- Journal tile layout — separate proposal.
- Conversation search or filtering — the list is short.
- Chat token streaming — still unspecced.
- Drag-to-reorder conversations — DeepTutor has it, but YAGNI for now.
- Workspace grouping — LifeKit has no workspaces yet; group by recency only.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`.
2. `/chat` renders single-column: conversation + composer, no left pane.
3. Sidebar shows a collapsible "Recent" section when Chat tab is active.
4. Clicking a conversation in the sidebar navigates to `/chat/<id>`.
5. "New chat" creates a conversation and navigates to it.
6. Rename and delete work on each row (or are deferred if the API doesn't
   support them).
7. Pasting a `/chat/<id>` URL opens that conversation.
8. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
9. `docs/product/STATUS.md` updated in the same change.
