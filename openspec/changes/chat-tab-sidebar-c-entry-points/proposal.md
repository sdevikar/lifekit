# Chat Tab c — Entry Points + Deep Links — Proposal

Slice **c** of three splitting [`../chat-tab-sidebar/`](../chat-tab-sidebar/).
Depends on
[`../chat-tab-sidebar-b-chatview/`](../chat-tab-sidebar-b-chatview/), which
makes a conversation openable in the main area. This is the only slice that
touches feed pages or routing, which is why it goes last and stands alone.

## Why

Slices a and b build a Chat tab you can reach by clicking the sidebar icon.
Every existing *entry point* still routes around it:

- `feed/page.tsx:29,39,53` — all three "Talk about this" handlers call
  `router.push('/c/${convId}')`, which navigates **away from the feed** to a
  full-page route, discarding the tab the user was in.
- `app/c/[id]/page.tsx` — the standalone conversation page, whose `← Feed`
  buttons (`page.tsx:43` and `:69`, one per header branch) exist to undo that
  navigation.

So the sidebar would be a second-class way in: click the icon to chat, but any
card you start a chat *from* dumps you onto a different page with its own
header and a back button. Two navigation models at once.

## What Changes

- **`frontend/src/app/feed/page.tsx`** — the three `handleTalkAbout*` handlers
  replace `router.push(...)` with `setActiveTab("chat")` +
  `setSelectedConvId(convId)`. They are the only change; the feed's layout,
  cards, and briefing logic are untouched.

  `useRouter` goes unused in this file and its import is removed.

- **`frontend/src/app/c/[id]/page.tsx`** — becomes a thin wrapper that, on
  mount, resolves the route id and calls `setActiveTab("chat")` +
  `setSelectedConvId(id)`. It renders nothing.

  The route **keeps working**: a pasted or bookmarked `/c/[id]` still lands on
  that conversation, which is the whole reason the URL exists. The wrapper is
  how a URL reaches state that now lives in a context above the page.

  Note the ordering: the wrapper must set the tab *and* the id together. Setting
  the id first renders `ChatView` with the previous selection; setting the tab
  first shows the empty state. Neither is wrong, but both in one render is.

- **`frontend/src/app/c/[id]/page.tsx`** — `← Feed` is deleted. `ChatView` has
  no back button (slice b), and the sidebar's Feed icon is the way back. This is
  the change that makes the two navigation models one.

- **`frontend/src/components/feed/MasterComposer.tsx`** — **do not touch in this
  slice.** The parent proposal asks for a floating-pill restyle; this component
  is currently unreferenced (see the parent proposal's open questions), so
  restyling it is work on dead code. Decide its fate separately — wire it up or
  delete it — rather than polishing it here.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: "Talk about this" on a feed card creates a
  conversation and opens it in the Chat tab's main area, without leaving the
  feed. `/c/[id]` deep links open that conversation in the Chat tab. Returning
  to the feed is via the sidebar Feed icon; there is no `← Feed` button.

## Not In Scope

- `MasterComposer` restyle or wiring (see above).
- Journal and Settings tabs.
- Conversation search, renaming, deletion — not in the API.
- Changing the `/c/[id]` URL shape, or adding new routes.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`, no new problems.
2. "Talk about this" on the exercise card, the resurfaced-idea card, and a
   fading-idea card each create a conversation, switch to the Chat tab, and
   open it — all three entry points, not just one.
3. The feed stays on screen until the tab switch; no `/c/...` navigation occurs.
4. Pasting a `/c/[id]` URL into a fresh tab opens that conversation in the Chat
   tab. Test with a hard reload, not client-side navigation.
5. A `/c/<unknown-id>` URL does not crash — it shows the conversation view's
   error state, not a blank page. (`useConversation` sets `error` on a failed
   fetch; confirm the view renders it.)
6. There is no `← Feed` button anywhere in the conversation view, and the
   sidebar Feed icon returns to the feed.
7. The feed page has no unused imports and builds clean.
8. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
9. `docs/product/STATUS.md` updated in the same change.