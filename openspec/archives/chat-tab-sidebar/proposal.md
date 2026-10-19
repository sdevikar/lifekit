# Chat Tab — Proposal (umbrella, split)

> **Split into three independently shippable slices.** `AGENTS.md` asks for one
> slice per proposal and warns the harness chokes on large ones. This file is the
> rationale and the umbrella; the slices are what get implemented:
>
> - [`../chat-tab-sidebar-a-conversation-list/`](../chat-tab-sidebar-a-conversation-list/)
>   — the list in the Chat panel. Panel-only.
> - [`../chat-tab-sidebar-b-chatview/`](../chat-tab-sidebar-b-chatview/)
>   — `selectedConvId` + `ChatView` in the main area.
> - [`../chat-tab-sidebar-c-entry-points/`](../chat-tab-sidebar-c-entry-points/)
>   — feed entry points and `/c/[id]` deep links. The only routing slice.
>
> All three now depend on
> [`../sidebar-nav-model/`](../sidebar-nav-model/), which replaces the
> two-column sidebar with a single-column nav. Slice a's `New chat` is a
> trailing `+` on a nav row, and that row does not exist until it lands.
>
> Two responsiveness problems found while writing this were split out first and
> have since shipped (2026-10-01):
>
> - [`../../archives/chat-markdown-rendering/`](../../archives/chat-markdown-rendering/)
>   — coach replies emitted Markdown that `MessageList.tsx` did not render.
> - [`../../archives/chat-pending-feedback/`](../../archives/chat-pending-feedback/)
>   — the user's own message did not appear until the coach finished replying.
>
> Landing those first left `MessageList` and `ChatInput` in their final shape,
> which is why slice b is a move rather than a rewrite.

## Why

Conversations are separate pages at `/c/[id]`, and the sidebar's Chat tab is a
placeholder (`Sidebar.tsx:81-83`). Conversations belong in the Chat tab: a list
in the panel, the active conversation in the main area. Makes them always one
click away, and collapses two navigation models — sidebar tabs *and* route
navigation — into one.

## Two findings that changed the plan

Both were found while writing the slices, and both contradict this document as
originally drafted.

**1. `ConversationsList` and `MasterComposer` are dead code.** Neither is
imported anywhere. `e6da69c` (Sidebar UI overhaul) removed both from
`feed/page.tsx`, and the `ConversationsList` call it removed was passing a
hardcoded `conversations={[]}` — the feed list had no data behind it even then.
So `GET /api/conversations` (`server.py:354-365`) is implemented and tested and
nothing calls it; there is currently no surface anywhere that lists a
conversation.

This changes slice a: the list component is *repurposed* rather than "restyled
for the sidebar", because its feed-shaped chrome (`lk-card` wrapper, `Coaching`
badge) is wrong in a `w-70` panel and it has no other caller to preserve.

It also changes the `MasterComposer` item below — see open questions.

**2. The header already has a control in the corner — and the whole layout is
wrong for it.** This document asks for a hover-`+` on the Chat panel title. The
panel's collapse toggle already occupies that row's top-right (`Sidebar.tsx:87`),
so there was nowhere to put it. Chasing that further showed the sidebar itself
is the problem: it is two columns, and it prints icon labels in *both* states.
A hover-`+` needs the icon, the label and the `+` to be one row, which the
current layout cannot express.

That is now [`../sidebar-nav-model/`](../sidebar-nav-model/) — a single column,
icon-only when collapsed, icon + label rows when expanded — and all three slices
depend on it.

## What Changes (across the three slices)

- **`frontend/src/hooks/useConversations.ts`** (new, slice a) — fetches the
  conversation list. Not added to `useBriefing`, which fetches feed data the
  Chat panel has no use for.
- **`frontend/src/components/feed/ConversationsList.tsx`** (slice a) —
  repurposed into a panel-shaped list.
- **`frontend/src/components/Sidebar.tsx`** (slices a, b) — Chat tab renders the
  conversation list, wires `New chat` to the nav row's trailing `+`, and wires
  selection.
- **`frontend/src/components/ChatView.tsx`** (new, slice b) — conversation view
  for the main area, composing `MessageList` + `ChatInput`. No `← Feed` button.
- **`frontend/src/components/TabContext.tsx`** (slice b) — gains
  `selectedConvId`. A second `ChatContext` was considered and rejected.
- **`frontend/src/components/TabContent.tsx`** (slice b) — renders `ChatView`
  for the Chat tab.
- **`frontend/src/app/feed/page.tsx`** (slice c) — "Talk about this" switches
  tabs instead of routing.
- **`frontend/src/app/c/[id]/page.tsx`** (slice c) — becomes a deep-link
  wrapper; `← Feed` removed.
- **`frontend/src/hooks/useConversation.ts`** — **unchanged across all three
  slices.** Markdown rendering and pending feedback already made it
  conversation-view-ready.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: conversations are listed in the Chat tab's sidebar
  panel; selecting one opens it in the main area; "Talk about this" on a feed
  card creates a conversation and opens it in the Chat tab without leaving the
  feed; `/c/[id]` deep links open in the Chat tab; returning to the feed is via
  the sidebar Feed icon.

## Not In Scope

- Journal functionality — the journal slices are separate and gated on an
  `intent.md` amendment.
- Books tab — deferred; single-book dogfood.
- Conversation search, filtering, renaming, deletion — not in the API, and the
  list is short.
- Collapsing the conversation list — see slice a's open question.
- Chat token streaming — still unspecced. See KANBAN "Future (deferred)".

## Open questions for the human

**`MasterComposer` is dead code.** This document originally asked for it to be
restyled as a floating pill in the feed. It is not rendered anywhere, so that is
polish on dead code. Three options: wire it up (it is the only path to an
*unseeded* chat — "New chat" in slice a creates a `composer`-seeded
conversation, but nothing lets you type the first message without a card), delete
it, or leave it. **Recommend deciding this before slice a**, because if the
composer comes back it belongs in the feed's main area and is a natural pair
with slice c's entry-point work.

**Collapsible list.** This document asks for a collapsible conversation list.
On a list of a handful of items that is state and chrome for nothing. Slice a
proposes to skip it. Reverse that if the panel will genuinely overflow.

## Ordering

Markdown rendering and pending feedback shipped first (independent, and both
give `ChatView` final-shaped children). Then
[`../sidebar-nav-model/`](../sidebar-nav-model/) — single-column nav, which the
`+` affordance needs. Then a → b → c: panel-only, then the main-area view, then
the entry points and routing that depend on both.