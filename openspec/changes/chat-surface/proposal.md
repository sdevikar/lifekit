# Chat Surface — Proposal (umbrella, split)

> **Split into three independently shippable slices.** `AGENTS.md` asks for one
> slice per proposal and warns the harness chokes on large ones. This file is the
> rationale and the umbrella; the slices are what get implemented:
>
> - [`../chat-surface-a-route-list/`](../chat-surface-a-route-list/)
>   — the `/chat` route with the conversation list. Two-pane shell, no opening yet.
> - [`../chat-surface-b-composer-open/`](../chat-surface-b-composer-open/)
>   — open a conversation in the right pane; composer creates a new one.
> - [`../chat-surface-c-entry-points/`](../chat-surface-c-entry-points/)
>   — feed entry points and `/c/[id]` deep links.
>
> All three depend on
> [`../sidebar-nav-model/`](../sidebar-nav-model/), which gives the sidebar its
> single-column nav rows. The Chat nav row becomes a link to `/chat`.

## Why

The Chat tab is a placeholder (`Sidebar.tsx:81-83` renders `Coming soon.`), and
the nav row's trailing `+` is a dead button. Conversations exist at `/c/[id]` but
there is no surface that lists them — `GET /api/conversations` is implemented and
tested and nothing calls it.

DeepTutor's pattern: Chat is a **destination**, not a tab. The sidebar row
navigates to `/chat`; the page is a two-pane workspace — conversation list on the
left, active conversation (or a composer) on the right. No "+" button. Starting a
chat means typing in the composer; the first message creates and persists the
conversation.

This proposal adopts that pattern. The sidebar's Chat row becomes a link to
`/chat`; the conversation list and composer live on the `/chat` page, not in the
sidebar panel.

## What Changes (across the three slices)

- **`frontend/src/components/Sidebar.tsx`** (slice a) — remove the `+` from the
  Chat nav row; the row becomes a link to `/chat`.
- **`frontend/src/app/chat/page.tsx`** (new, slice a) — the `/chat` route. Two-pane
  layout: `ConversationsList` on the left, empty state on the right.
- **`frontend/src/hooks/useConversations.ts`** (new, slice a) — fetches
  `GET /api/conversations`. Same as the archived slice a's hook.
- **`frontend/src/components/feed/ConversationsList.tsx`** (slice a) — repurposed
  for the `/chat` left pane. Same treatment as the archived slice a: drop the
  `lk-card` wrapper and `Coaching` badge, add an empty state.
- **`frontend/src/components/ChatView.tsx`** (new, slice b) — conversation view for
  the right pane. Composes `MessageList` + `ChatInput`. Same as the archived slice b.
- **`frontend/src/components/feed/MasterComposer.tsx`** (slice b) — wired into the
  `/chat` empty state. Submitting creates a conversation and opens it.
- **`frontend/src/app/feed/page.tsx`** (slice c) — "Talk about this" creates a
  conversation and navigates to `/c/[id]`.
- **`frontend/src/app/c/[id]/page.tsx`** (slice c) — `← Feed` navigates to `/feed`.
- **`frontend/src/hooks/useConversation.ts`** — **unchanged across all three
  slices.**

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: the sidebar Chat row navigates to `/chat`, a two-pane
  surface listing conversations on the left and showing the active conversation (or
  a composer) on the right. "Talk about this" on a feed card creates a conversation
  and opens it at `/c/[id]`. `/c/[id]` deep links work as full pages.

## Not In Scope

- Journal functionality — the journal slices are separate and gated on an
  `intent.md` amendment.
- Books tab — deferred; single-book dogfood.
- Conversation search, filtering, renaming, deletion — not in the API, and the
  list is short.
- Chat token streaming — still unspecced. See KANBAN "Future (deferred)".
- Collapsing the conversation list — on a list of a handful of items a collapse
  control is state and chrome for nothing.

## Ordering

[`../sidebar-nav-model/`](../sidebar-nav-model/) shipped 2026-10-01. Then
a → b → c: the route and list, then opening and composing, then entry points and
deep links.
