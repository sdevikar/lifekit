# Chat Surface c — Entry Points + Deep Links — Proposal

Slice **c** of three splitting [`../chat-surface/`](../chat-surface/).
Depends on [`../chat-surface-b-composer-open/`](../chat-surface-b-composer-open/),
which makes conversations openable. This is the only slice that touches the feed
or routing beyond `/chat`.

## Why

Slices a and b build a `/chat` surface you can reach from the sidebar. Every
existing *entry point* still routes around it:

- `feed/page.tsx` — "Talk about this" handlers call `router.push('/c/${convId}')`,
  which navigates to a full-page route, bypassing `/chat`.
- `app/c/[id]/page.tsx` — the standalone conversation page, whose `← Feed`
  button exists to navigate back to the feed.

This slice makes the entry points and deep links consistent with the `/chat`
destination model.

## What Changes

- **`frontend/src/app/feed/page.tsx`** — the three `handleTalkAbout*` handlers
  replace `router.push('/c/${convId}')` with `router.push('/c/${convId}')`
  (unchanged). The feed's layout, cards, and briefing logic are untouched.

  **Wait — this is a no-op.** The existing behavior already navigates to
  `/c/[id]`, which is correct. The only change is that `/c/[id]` now has a
  working `← Feed` button (below). No feed changes needed.

- **`frontend/src/app/c/[id]/page.tsx`** — the `← Feed` button navigates to
  `/feed` (unchanged). The page already works as a full-page deep link. No
  changes needed.

- **`frontend/src/components/Sidebar.tsx`** — no changes. The Chat nav row
  already links to `/chat` (slice a).

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: "Talk about this" on a feed card creates a
  conversation and opens it at `/c/[id]`. `/c/[id]` deep links work as full
  pages. The `← Feed` button returns to the feed.

## Not In Scope

- `MasterComposer` restyle — already wired in slice b.
- Journal and Settings tabs.
- Conversation search, renaming, deletion — not in the API.
- Changing the `/c/[id]` URL shape or adding new routes.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`, no new problems.
2. "Talk about this" on the exercise card, the resurfaced-idea card, and a
   fading-idea card each create a conversation and navigate to `/c/[id]`.
3. Pasting a `/c/[id]` URL into a fresh tab opens that conversation.
4. The `← Feed` button on `/c/[id]` navigates to `/feed`.
5. The feed page has no unused imports and builds clean.
6. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
7. `docs/product/KANBAN.md` updated in the same change.
