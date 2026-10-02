# Sidebar Nav Model — Proposal

Replaces the two-column sidebar with a single-column nav, following the
DeepTutor reference (`HKUDS/DeepTutor`, `assets/figs/web-1.6.5/OVERVIEW.png`).
**Must land before** the Chat Tab slices, because
[`../chat-tab-sidebar-a-conversation-list/`](../chat-tab-sidebar-a-conversation-list/)
puts a `+` on a nav row and that affordance does not exist yet in the current
layout.

## Why

The sidebar shipped in `e6da69c`, then `a0bf60d` moved the collapse toggle to the
panel's top-right, then `e5a399b` swapped the arrows for lucide panel icons and
added the Settings gear. None of those touched the structure. Reviewing it
against the DeepTutor reference shows the structure itself is wrong, not just a
control's position.

Ours is **two columns**:

```
┌────┬──────────────────────┐   ← w-14 icon strip (Sidebar.tsx:36)
│ 🏠 │  LifeKit              │   ← w-70 panel (Sidebar.tsx:70)
│ 📓 │  Today                │
│ 💬 │  Coming soon.         │
│ ⚙  │                  [⟨⟩]│   ← collapse toggle (Sidebar.tsx:87)
└────┴──────────────────────┘
```

Each nav item is an icon with a 10px label *underneath it*, printed in **both**
states — collapsed and expanded. DeepTutor is **one column** of icon + label
rows; collapsing narrows that same column to icons only and drops the labels.

Two consequences that bite now:

1. **The hover affordance cannot be built in the current layout.** "Hover the
   name, the row highlights, `+` appears" requires the icon, the label, and the
   `+` to be one hoverable element. Today the label lives in the icon strip and
   the panel header is a different column entirely. There is no row to hover.

2. **The icon strip does not shrink when collapsed, so collapsing buys
   nothing.** It stays 56px wide showing the same icons and the same tiny
   labels; only the panel disappears. The user gets less room and no clearer
   picture of what changed.

A nav row is the unit the Chat and Journal tabs need — a label that is also the
hover target for that tab's "new item" action. Build the unit once, here.

## What Changes

- **`frontend/src/components/Sidebar.tsx`** — collapse the icon strip and the
  panel into **one column**. Collapsed: a narrow icon-only strip. Expanded: the
  same nav items as icon + label rows, with tab content (the conversation list
  for Chat) below them.

  The nav item becomes a single row: icon, label, and — for Chat and Journal
  only — a trailing `+` that appears on hover and on keyboard focus.

  `IconTab` (`:95-122`) is reworked into that row. Its current shape — a
  `flex-col` button with the label in a sibling `<span>` (`:119`) — is exactly
  what has to change.

- **Labels are conditional on `collapsed`.** When collapsed, the label is not
  rendered at all rather than shrunk or clipped. Each icon keeps its
  `aria-label` and `title`, so the collapsed strip stays labelled for
  screen readers and tooltips.

- **Hover + focus reveal.** The `+` is revealed by `group-hover` on the row and
  `focus-visible` within it. Hover alone is not an accessible control, so the
  focus path is part of the requirement, not a nicety.

- **Which tabs get a `+`.** Chat and Journal only, per the reference. Feed and
  Settings have no "new item" action and must not show one. The row takes an
  optional trailing action rather than hardcoding a `+` for every tab.

- **The collapse toggle keeps its current placement** — panel's top-right when
  expanded, icon strip top when collapsed (`sidebar-refinements`). That part
  works and matches the reference's own top-right control.

## Design decisions this leaves open

The reference is a visual one, and pixel values are the human's call. What needs
answering before implementation, not during:

- **Journal's `+` will not work yet.** Journal is deferred behind an
  `intent.md` amendment (`journal-tab/`), so there is no journal entry to
  create. Options: render the Journal `+` disabled or hidden until Journal
  slice C lands, or show it and have it do nothing. **Recommend hidden** — a
  control that does nothing is worse than no control. See open questions.
- **Widths.** Collapsed ≈ 56px, expanded ≈ 260px. The reference's panel is
  proportionally wider than ours. Needs a look, not a guess.
- **Active-row treatment.** The reference uses a filled background on the active
  row (`bg-lk-user-msg` is already the token for this, `IconTab:112`). Keep it.
- **What the panel shows per tab.** Chat: the conversation list. Feed: nothing —
  the feed is the main area, so a title block is decoration. Journal and
  Settings: their placeholder until those tabs ship.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: the sidebar is a single column. Collapsed it is an
  icon-only strip; expanded it shows icon-and-label nav rows with the active
  tab's content below. Chat and Journal rows reveal a `+` on hover or keyboard
  focus.

## Not In Scope

- The conversation list itself — slice a.
- Selecting or opening a conversation — slice b.
- Feed entry points and `/c/[id]` routing — slice c.
- Journal content. This only builds the nav row and its slot.
- Icons. Reuse the existing `FeedIcon` / `JournalIcon` / `ChatIcon` /
  `SettingsIcon` (`Sidebar.tsx:124-197`) — do not swap the icon set.
- Renaming tabs, reordering them, or adding a tab.

## Open questions for the human

1. **Journal's `+`** — hidden until Journal lands, or shown-and-inert? Recommend
   hidden.
2. **Does Feed get a panel section?** With nav labels in the column, the Feed
   tab's current `LifeKit / Today` title block (`Sidebar.tsx:74-76`) is
   redundant chrome. Recommend dropping it. Confirm.
3. **Is `localStorage` persistence of the collapsed state kept?** Currently
   `COLLAPSE_KEY` (`:6`). Recommend yes, unchanged — no reason to make the user
   re-collapse on every load.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`, no new problems.
2. Collapsed, the sidebar is a single narrow icon-only strip with **no text
   labels visible**, and every icon still has an accessible name.
3. Expanded, the sidebar is one column of icon + label rows, no separate icon
   strip, no duplicate panel border.
4. Collapsing and expanding preserves the active tab and persists across
   reloads.
5. The active tab's row is visibly selected in both states.
6. Hovering the Chat row reveals a `+`; tabbing to it reveals it too, and it is
   operable by keyboard.
7. The Chat and Journal rows reveal `+`; the Feed and Settings rows do not.
8. Chat panel content (once slice a lands) renders below the nav rows in the
   same column, and is hidden entirely when collapsed.
9. Ask the human to eyeball collapsed and expanded in both light and dark
   themes — this is a visual change, so the check is theirs, not a screenshot.
10. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
11. `docs/product/STATUS.md` and `docs/product/KANBAN.md` updated in the same
    change.