# Chat Tab a — Conversation List — Proposal

Slice **a** of three splitting [`../chat-tab-sidebar/`](../chat-tab-sidebar/).
Independently shippable and reviewable: panel-only, no main-area component, no
shared state, no routing change. Followed by
[`../chat-tab-sidebar-b-chatview/`](../chat-tab-sidebar-b-chatview/) and
[`../chat-tab-sidebar-c-entry-points/`](../chat-tab-sidebar-c-entry-points/).

**Depends on [`../sidebar-nav-model/`](../sidebar-nav-model/)**, which turns the
sidebar into a single column of nav rows. This slice's `New chat` control lives
on the Chat nav row, revealed on hover — which does not exist until that slice
lands.

## Why

The Chat tab is a placeholder. `Sidebar.tsx:81-83` renders
`Coming soon.` for it, while the feed's conversation list was deleted from
`feed/page.tsx` in `e6da69c` (Sidebar UI overhaul) and has not been replaced.
So today there is **no surface anywhere in the app that lists conversations** —
`GET /api/conversations` is implemented and tested (`server.py:354-365`) and
nothing calls it. The only ways into a conversation are "Talk about this" on a
feed card and a pasted `/c/[id]` URL.

This slice puts the list back where it belongs: in the Chat panel, so a
conversation is always one click away.

## What Changes

- **`frontend/src/hooks/useConversations.ts`** (new) — fetches
  `GET /api/conversations` and exposes `{ conversations, loading, error, refresh }`.
  It re-fetches when the Chat tab becomes active, so a conversation created
  elsewhere is there the next time the user opens the panel.

  Deliberately **not** added to `useBriefing`. That hook fetches
  `/api/briefing/today`; the Chat panel needs no briefing, and mounting it
  there would pull feed data for a chat surface. One fetch, one hook, one
  concern.

- **`frontend/src/components/feed/ConversationsList.tsx`** — repurpose, not
  extend. This component is **currently unreferenced** (nothing imports it since
  `e6da69c`), and its chrome is feed-shaped: an `lk-card` wrapper
  (`ConversationsList.tsx:14`) and a `Coaching` badge (`:19`) that are wrong in a
  `w-70` sidebar panel (`Sidebar.tsx:70`). Strip both, keep the row markup and
  the `onOpen(id)` contract, add an empty state.

  Repurposing beats a `variant` prop: there is exactly one caller after this
  slice, and a variant flag with one value is a boolean pretending to be a
  design system. It also turns dead code live rather than adding a near-copy.

  No new component file. The list is not moving to `components/conversation/`
  in this slice — one move, when the panel and the main area both consume it.

- **`frontend/src/components/Sidebar.tsx`** — the Chat tab's section renders the
  conversation list. The `New chat` control is the trailing `+` on the **Chat
  nav row**, which `../sidebar-nav-model/` already builds the hover/focus slot
  for — this slice only supplies the handler: POST a `seed_kind: "composer"`
  conversation, then `onOpen` the new id so it appears in the list immediately.

  `useBriefing.createConversation` (`:53-60`) already does this POST, but it
  lives in a hook that fetches the briefing. The panel calls `apiPost` from
  `useConversations` instead — one fetch, and the new conversation is already
  in the list the hook just returned.

  This replaces the older draft's plan to put a hover-`+` on the panel title.
  That was fighting the old two-column layout: the panel's collapse toggle
  already owns that row's top-right (`Sidebar.tsx:87`), so the `+` had nowhere
  to go. On a nav row there is a trailing slot by construction.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: the Chat tab's sidebar panel lists the current
  book's conversations with titles and dates, and offers a `New chat` action.

## Not In Scope

- **Collapsing the list.** The parent proposal asks for a collapsible list; on
  a list of a handful of items a collapse control is state and chrome for
  nothing. Add it when the list is demonstrably taller than the panel.
- **Opening a conversation.** This slice renders the list; clicking a row has
  nowhere to go until slice b introduces `selectedConvId`. The `onOpen` handler
  is wired to a no-op with a `TODO` naming slice b — the panel is not
  shippable as a *destination* yet, only as a surface.
- **Search, filtering, renaming, deletion.** Not in the API; list is short.
- Anything in the main area, on the feed, or in routing — slices b and c.
- Restyling `MasterComposer` — see the parent proposal's open questions.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`, with no new lint
   problems.
2. Clicking the Chat icon shows the conversation list in the panel, with
   titles and dates, matching `GET /api/conversations`.
3. The list is empty-state clean when there are no conversations.
4. `New chat` creates a conversation and it appears in the list without a
   reload.
5. `New chat` is the trailing `+` on the Chat nav row, revealed on hover and on
   keyboard focus, and operable by keyboard alone with an `aria-label`.
6. The list renders in both light and dark themes — the panel background is
   `--lk-card` in both, so check that hover and border states read.
7. The feed page is unchanged and still builds.
8. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
9. `docs/product/STATUS.md` updated in the same change.