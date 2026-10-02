# LifeKit Kanban

## In Progress

*(nothing yet)*

## Upcoming

Ordered by dependency, then by value-per-unit-work. Everything here is
`Awaiting approval` — the human approves, Atlas never self-approves.

| # | Slice | Proposal | Depends On | Status |
|---|-------|----------|------------|--------|
| 1 | Chat markdown rendering | `openspec/changes/chat-markdown-rendering/` | — | Awaiting approval |
| 2 | Chat pending feedback | `openspec/changes/chat-pending-feedback/` | — | Awaiting approval |
| 3 | Chat Tab **a** — conversation list | `chat-tab-sidebar/` (split not yet written) | #1, #2 | Awaiting approval |
| 4 | Chat Tab **b** — ChatView + selection | same | #3 | Awaiting approval |
| 5 | Chat Tab **c** — entry points + deep links | same | #3, #4 | Awaiting approval |

**Why this order.** #1 and #2 have no dependencies and each is independently
shippable, so they go first and each is real dogfood value on its own. They
also *precede* the Chat Tab work deliberately: #4 introduces `ChatView.tsx`,
which reuses `MessageList` and `ChatInput` — both of which #1 and #2 rewrite.
Landing them first means `ChatView` is built once against their final shape
instead of being reworked. #3 → #4 → #5 is the natural build order within the
Chat Tab: panel-only, then the main-area view, then the feed-page and routing
changes that depend on both.

The a/b/c proposals are **not written yet** — the split is documented at the
bottom of `chat-tab-sidebar/proposal.md`. Write them before starting #3.

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
| Chat token streaming | SSE + partial-flush persistence + client reader. Decide after #2 is dogfooded — the screen may already feel responsive without it. |
| Journal TipTap vs textarea | Deliberate dependency decision, carried in `journal-tab-b-editor`. |

## Done

| Slice | Shipped | Notes |
|-------|---------|-------|
| Sidebar Layout Shell | 2026-09-30 | Icon strip (Feed/Journal/Chat) + collapsible panel. Spec archived at `../../openspec/archives/sidebar-layout-shell/`. |
| Sidebar refinements | 2026-10-01 | Collapse toggle moved to the panel's top-right (icon strip top when collapsed). |
| Settings icon + lucide panel icons | 2026-10-01 | Gear tab at strip bottom (placeholder page); collapse/expand now `panel-left-open`/`panel-left-close`. |
