# Journal Tile Layout — Proposal

**Supersedes:** [`../journal-tab-c-toc-navigation/`](../journal-tab-c-toc-navigation/)
(sidebar TOC + navigation). That proposal assumed a sidebar list; this one
replaces it with a DeepTutor-style tile grid in the main area.

**Status: proposal only — do not implement yet.** The journal is still gated
on an `intent.md` amendment. This proposal supersedes the old slice C layout
but does not unblock the journal.

## Why

The old journal slice C proposed a sidebar TOC — a vertical list of entries in
the sidebar panel. DeepTutor's pattern is a **tile grid**: entries as cards in
the main area, each showing title, date, and a content preview, in a responsive
masonry-style grid. This is more scannable, more visual, and matches the
DeepTutor aesthetic the user wants to adopt.

The journal remains deferred (gated on `intent.md` amendment). This proposal
replaces the layout approach but does not change the deferral status.

## What Changes

### Main area — tile grid

- **`frontend/src/app/journal/page.tsx`** — replace the "Coming soon."
  placeholder with a responsive tile grid:
  - Each entry is a card showing: title, formatted date, and a 2-3 line
    content preview (plain text, truncated).
  - Cards are CSS Grid: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3` (or
    similar responsive breakpoints).
  - Clicking a card opens the entry (navigates to `/journal/<id>` or opens
    in-place — TBD by slice B).
  - A "New entry" button at the top of the grid.

### Sidebar — no TOC

- The sidebar does **not** show a journal TOC. The tile grid in the main area
  is the navigation. The sidebar's Journal nav row is enough.

### Deep links

- `/journal/<id>` — opens a specific entry (same as old slice C's `/j/<id>`,
  but under `/journal/` to match the route group).

## Capabilities

### Modified Capabilities

- `journal-entries`: entries display as a responsive tile grid in the main
  area, not a sidebar list. Each card shows title, date, and preview.

## Not In Scope

- Journal storage + API — slice A (unchanged, still deferred).
- Journal editor — slice B (unchanged, still deferred).
- Entry deletion, search, or filtering.
- LLM-generated titles — first-line truncation until a cheap tasking model
  exists.
- The `intent.md` amendment that unblocks the journal — still required
  before any journal slice is implemented.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`.
2. `/journal` renders a responsive tile grid of entries.
3. Each card shows title, date, and a content preview.
4. Clicking a card opens the entry.
5. "New entry" creates and opens a new entry.
6. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
7. `docs/product/KANBAN.md` updated in the same change.
8. `.agents/intent.md` amended — **human approval required** before
   implementation.
