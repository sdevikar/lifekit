# LifeKit Kanban

## In Progress

*(nothing yet)*

## Upcoming

Ordered by dependency, then by value-per-unit-work. Everything here is
`Awaiting approval` — the human approves, Atlas never self-approves.

| # | Slice | Proposal | Depends On | Status |
|---|-------|----------|------------|--------|
| 1 | Sidebar nav model (single column) | `sidebar-nav-model/` | — | Awaiting approval |
| 2 | Chat Tab **a** — conversation list | `chat-tab-sidebar-a-conversation-list/` | #1 | Awaiting approval |
| 3 | Chat Tab **b** — ChatView + selection | `chat-tab-sidebar-b-chatview/` | #2 | Awaiting approval |
| 4 | Chat Tab **c** — entry points + deep links | `chat-tab-sidebar-c-entry-points/` | #2, #3 | Awaiting approval |

**Why this order.** `MessageList` and `ChatInput` now have their final shape —
Markdown rendering and the pending state both landed 2026-10-01, so slice b
introduces `ChatView.tsx` on top of components that are not about to change
again. #1 comes first because the sidebar is currently **two columns** and
prints icon labels in both states; a nav row — icon, label, and a trailing `+`
that appears on hover — is the unit slice a needs for `New chat`, and the
current layout cannot express it. #2 → #3 → #4 then follows the Chat Tab's
natural order: panel-only, then the main-area view, then entry points and
routing that depend on both.

Umbrella rationale for the Chat Tab is at
`openspec/changes/chat-tab-sidebar/proposal.md`.

**Two open questions remain**, both in `chat-tab-sidebar/proposal.md`:
`MasterComposer` is dead code — wire it up, delete it, or leave it. The composer
is the only path to an *unseeded* chat, so if it comes back it belongs in the
feed and pairs naturally with #4.

Resolved 2026-10-01 in `sidebar-nav-model`: Journal's `+` is **shown and
inert** (`aria-disabled` with a tooltip, not a working control) until the
journal slices land, and the Feed panel's `LifeKit / Today` block is
**dropped** as redundant once nav rows carry labels.

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
