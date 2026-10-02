# Journal Tab C — TOC + Navigation — Proposal

Slice C of the deferred Journal Tab, and the last one. Builds on B
([`../journal-tab-b-editor/`](../journal-tab-b-editor/)).

## Why

The editor works but is unreachable — there is no way to list or reopen an
entry. This slice wires the Journal tab into the sidebar so entries are one
click away, which is what makes the surface usable rather than a curiosity.

## What Changes

- **`frontend/src/components/TabContext.tsx`** — add
  `{ selectedEntryId, setSelectedEntryId }`. Keep it in the existing tab context
  rather than adding a second provider; the journal is a tab like the others.

- **`frontend/src/hooks/useJournal.ts`** (new) — `listEntries`, `createEntry`,
  `getEntry`, `updateEntry` over `frontend/src/types/api.ts`. Kept out of
  `useBriefing` — that hook is the feed's, and journal entries do not belong to
  the briefing contract.

- **`frontend/src/components/Sidebar.tsx`** — when the Journal tab is active,
  the panel shows a TOC of recent entries from `GET /api/journal`, newest
  first. The active entry is highlighted. A "New entry" button sits at the top;
  hovering the "Journal" panel title reveals a `+` that does the same thing.

- **`frontend/src/components/TabContent.tsx`** — render `JournalEditor` in the
  main area for the Journal tab, replacing the "Coming soon." placeholder.

- **`frontend/src/app/j/[id]/page.tsx`** (new) — deep-link target, same thin
  wrapper shape as the Chat tab slice: on mount, set the selected entry and
  switch to the Journal tab. Without this, an entry id is not shareable.

## Capabilities

### New Capabilities

- `journal-entries`: recent entries are listed in the Journal panel and open in
  the main area. New entries are reachable from the panel and deep-linkable.

## Not In Scope

- Entry deletion or renaming in the UI (no API for it).
- Search or filtering — the list is short.
- Books tab.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`.
2. Clicking the Journal icon lists entries in the panel.
3. Clicking an entry opens it in the main area with its content.
4. "New entry" and the panel-title `+` both create and open an entry.
5. The TOC reflects a newly created or recently updated entry.
6. `/j/<id>` opens that entry in the Journal tab in a fresh tab.
7. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
8. `docs/product/STATUS.md` updated in the same change.
9. `.agents/intent.md` amended — **human approval required**, this slice is the
   one that makes the journal a user-visible surface.