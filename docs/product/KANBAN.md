# LifeKit Kanban

## In Progress

*(nothing yet)*

## Upcoming

| # | Slice | Proposal | Depends On | Status |
|---|-------|----------|------------|--------|
| 1 | Chat markdown rendering | `openspec/changes/chat-markdown-rendering/` | — | Awaiting approval |
| 2 | Chat pending feedback | `openspec/changes/chat-pending-feedback/` | — | Awaiting approval |
| 3 | Chat Tab (needs a/b/c split) | `openspec/changes/chat-tab-sidebar/` | #1, #2 | Awaiting approval |
| — | Journal Tab A/B/C | `openspec/changes/journal-tab-a-storage-api/`, `-b-editor/`, `-c-toc-navigation/` | — | **Deferred** — needs an `intent.md` amendment |

## Future (deferred)

| Item | Reason |
|------|--------|
| Books tab | Single-book dogfood, no switching need yet. Add when book #2 exists. |
| LLM-generated journal titles | Cheap tasking model later. First-line truncation for now. |
| Chat token streaming | SSE + partial-flush persistence + client reader. Decide after the pending state is dogfooded — the screen may already feel responsive without it. |
| Journal TipTap vs textarea | Deliberate dependency decision, carried in `journal-tab-b-editor`. |

## Done

| Slice | Shipped | Notes |
|-------|---------|-------|
| Sidebar Layout Shell | 2026-09-30 | Icon strip (Feed/Journal/Chat) + collapsible panel. Spec archived at `../../openspec/archives/sidebar-layout-shell/`. |
| Sidebar refinements | 2026-10-01 | Collapse toggle moved to the panel's top-right (icon strip top when collapsed). |
| Settings icon + lucide panel icons | 2026-10-01 | Gear tab at strip bottom (placeholder page); collapse/expand now `panel-left-open`/`panel-left-close`. |
