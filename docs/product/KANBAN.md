# LifeKit Kanban

## In Progress

*(nothing yet)*

## Upcoming

Ordered by dependency, then by value-per-unit-work. Everything here is
`Awaiting approval` — the human approves, Atlas never self-approves.

| # | Slice | Proposal | Depends On | Status |
|---|-------|----------|------------|--------|
| 1 | Chat Tab **a** — conversation list | `openspec/changes/chat-tab-sidebar/` (split not yet written) | — | Awaiting approval |
| 2 | Chat Tab **b** — ChatView + selection | same | #1 | Awaiting approval |
| 3 | Chat Tab **c** — entry points + deep links | same | #1, #2 | Awaiting approval |

**Why this order.** `MessageList` and `ChatInput` now have their final shape —
Markdown rendering (2026-10-01) and the pending state both landed, and the
Chat Tab **b** slice introduces `ChatView.tsx` on top of them. #1 → #2 → #3 is
the natural build order within the Chat Tab: panel-only, then the main-area
view, then the feed-page and routing changes that depend on both.

The a/b/c proposals are **not written yet** — the split is documented at the
bottom of `chat-tab-sidebar/proposal.md`. Write them before starting #1.

## Deferred

| Slice | Proposals | Reason |
|-------|-----------|--------|
| Journal Tab A — storage + API | `journal-tab-a-storage-api/` | Deferred with the journal. Backend-only and dependency-free, so it can be pulled forward on its own if the journal is ever unblocked. |
| Journal Tab B — editor | `journal-tab-b-editor/` | Deferred. Carries an open TipTap-vs-textarea decision. |
| Journal Tab C — TOC + navigation | `journal-tab-c-toc-navigation/` | Deferred. This is the slice that makes the journal a user-visible surface and needs the `.agents/intent.md` amendment. |

Journal slices are sequenced A → B → C and gated on a human-approved
`intent.md` amendment. Umbrella: `journal-tab/`.

## Future (deferred)

| Item | Reason |
|------|--------|
| Books tab | Single-book dogfood, no switching need yet. Add when book #2 exists. |
| LLM-generated journal titles | Cheap tasking model later. First-line truncation for now. |
| Chat token streaming | SSE + partial-flush persistence + client reader. Still **no proposal written** — `chat-pending-feedback/` explicitly deferred it. Decide after the pending state is dogfooded: if the wait is tolerable once the screen responds, streaming may not be worth it. |
| Journal TipTap vs textarea | Deliberate dependency decision, carried in `journal-tab-b-editor`. |

## Done

| Slice | Shipped | Notes |
|-------|---------|-------|
| Sidebar Layout Shell | 2026-09-30 | Icon strip (Feed/Journal/Chat) + collapsible panel. Spec archived at `../../openspec/archives/sidebar-layout-shell/`. |
| Sidebar refinements | 2026-10-01 | Collapse toggle moved to the panel's top-right (icon strip top when collapsed). |
| Settings icon + lucide panel icons | 2026-10-01 | Gear tab at strip bottom (placeholder page); collapse/expand now `panel-left-open`/`panel-left-close`. |
| Chat markdown rendering | 2026-10-01 | `react-markdown` + `remark-gfm` for coach replies, hand-rolled `.lk-prose` against the existing tokens; prompt now asks for Markdown. |
| Chat pending feedback | 2026-10-01 | Optimistic user message before the await + a dashed "Thinking…" status row. Client-state only — the server's reply-before-persist ordering is what makes the rollback correct and did not move. |
