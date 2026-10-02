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

## Design decisions

All resolved by the human on 2026-10-01:

- **Journal's `+`: shown and inert.** It appears on hover/focus like Chat's, and
  does nothing until the journal slices land. Accepted over hiding it, so the
  nav row does not need a second visual state later. `aria-disabled` with a
  native `title` saying it is not available yet — there is no tooltip primitive
  in the codebase (`Sidebar.tsx:27,116` and `ThemeToggle.tsx:59` all use native
  `title`), and building one for a single string is not worth it.
  **Not focusable** — the human's call, over a focusable-but-disabled button.
  A keyboard user does not reach it; the tab order stays clean.
- **The Feed panel's `LifeKit / Today` block is dropped** (`Sidebar.tsx:74-76`).
  Once nav rows carry labels, a title block repeating the app name above them
  is redundant chrome.
- **Widths.** Collapsed `w-10` (40px, down from the current `w-14`), expanded
  unchanged at `w-70` (280px) so conversation titles still fit on one line.
- **Nav ordering is kept:** Feed / Journal / Chat at the top, Settings pinned to
  the bottom by the existing `flex-1` spacer (`Sidebar.tsx:59`). This matches the
  reference, which does the same.
- **Active-row treatment:** keep `bg-lk-user-msg` (`IconTab:112`), already the
  token for it.

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

None outstanding. Both were answered on 2026-10-01: Journal's `+` is shown and
inert, and the Feed title block goes. `localStorage` persistence of the
collapsed state is kept unchanged (`COLLAPSE_KEY`, `:6`) — no reason to make
the user re-collapse on every load.

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
   Journal's `+` is visibly present but inert — `aria-disabled`, not focusable,
   with a native `title` saying it is not available yet. Chat's creates a
   conversation (once slice a lands).
8. The Feed tab's panel shows no `LifeKit / Today` block — the title is gone.
9. Collapsed, the sidebar is `w-10`; expanded, `w-70`.
10. Chat panel content (once slice a lands) renders below the nav rows in the
    same column, and is hidden entirely when collapsed.
11. Ask the human to eyeball collapsed and expanded in both light and dark
    themes — this is a visual change, so the check is theirs, not a screenshot.
12. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
13. `docs/product/STATUS.md` and `docs/product/KANBAN.md` updated in the same
    change.