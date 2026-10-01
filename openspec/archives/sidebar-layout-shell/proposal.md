# Sidebar Layout Shell — Proposal

## Why

The app currently renders as a single-column centered feed (785px max-width) with a fixed bottom composer. Conversations live at `/c/[id]` as separate pages. This doesn't match the chat-app pattern the user wants (DeepTutor, ChatGPT, Open WebUI) where a left sidebar provides navigation and the main area shows content.

This first slice delivers the **layout shell only**: a sidebar with vertical icon tabs and a collapsible panel, with the existing feed rendering in the main area. No journal or chat functionality yet — just the structural skeleton that subsequent slices build on.

## What Changes

- **`frontend/src/app/layout.tsx`** — wrap children in a flex row: `<Sidebar />` + `<main>`. The `<main>` area takes remaining width and renders page content.

- **`frontend/src/components/Sidebar.tsx`** (new, `"use client"`) — the sidebar component:
  - **Icon strip** (far left, ~56px wide): Feed, Journal, Chat icons with labels. Always visible. Active tab highlighted.
  - **Collapsible panel** (~280px when open): shows navigation content for the active tab. For now, the Feed tab panel shows the app name and day summary; Journal and Chat panels show a placeholder ("Coming soon").
  - **Collapse toggle**: button to collapse the panel to just the icon strip. State persisted to `localStorage` (`lifekit-sidebar-collapsed`). Defaults to open.
  - Badge counts on Chat icon (number of conversations) — populated in slice 2.

- **`frontend/src/components/TabContext.tsx`** (new) — React context providing `{ activeTab, setActiveTab }` so any component can switch tabs. Tabs: `"feed" | "journal" | "chat"`.

- **`frontend/src/app/feed/page.tsx`** — remove the `ConversationsList` component (moved to Chat tab in slice 2). Remove the `MasterComposer` (restyled as floating input in slice 2). Keep TodayHeader, ExerciseCard, ResurfacedIdeaCard, FadingIdeasCard.

- **`frontend/src/app/page.tsx`** — unchanged (still redirects to `/feed`).

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: layout. The feed renders inside a sidebar-based layout shell. The sidebar provides tab-based navigation. The feed itself is visually unchanged — same cards, same theme, same interactions.

## Not In Scope

- Journal functionality (slice 3).
- Chat tab functionality (slice 2).
- Books tab (deferred — single-book dogfood, no switching need yet).
- Mobile/responsive sidebar behavior (desktop-first, localhost app).
- Deep-linking to `/c/[id]` (slice 2).

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`.
2. The app renders with a visible left sidebar: icon strip with Feed/Journal/Chat icons, collapsible panel.
3. Clicking Feed icon shows the feed in the main area (same content as today, minus ConversationsList and MasterComposer).
4. Clicking Journal or Chat icon shows a placeholder in the main area.
5. The collapse toggle hides/shows the panel. State persists across page reloads.
6. The sidebar is styled with existing theme tokens (`--lk-bg`, `--lk-card`, `--lk-border`, etc.) — no new colors.
7. `uv run pytest` shows no new failures beyond the known `test_split_dyl_pdf` (BACKLOG P2).
8. `docs/product/STATUS.md` updated in the same change.
