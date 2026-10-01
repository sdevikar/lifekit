# Journal Tab — Proposal

## Why

The user wants a place to write notes in rich text, auto-saved, with auto-generated titles and a TOC of recent entries — like a lightweight journaling app embedded in the sidebar. This is a new surface that doesn't exist today. The journal lives in its own SQLite table and API endpoints, separate from conversations.

## What Changes

- **`lifekit/db/schema.py`** — add `journal_entries` table:
  ```sql
  CREATE TABLE journal_entries (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
  );
  ```

- **`lifekit/serve/server.py`** — add journal API routes:
  - `GET /api/journal` — list recent entries (id, title, updated_at) for TOC.
  - `POST /api/journal` — create new entry (returns id).
  - `GET /api/journal/<id>` — get single entry with content.
  - `PUT /api/journal/<id>` — update entry (auto-save). Updates `updated_at`.

- **`frontend/package.json`** — add TipTap dependencies:
  - `@tiptap/react`, `@tiptap/starter-kit`, `@tiptap/extension-placeholder`

- **`frontend/src/components/JournalEditor.tsx`** (new, `"use client"`) — TipTap rich text editor:
  - Auto-save: debounced `onUpdate` (1s) → `PUT /api/journal/<id>`.
  - Auto-generated title: first line of text content, truncated to 50 chars. Updated on save.
  - "New entry" button: creates entry via `POST /api/journal`, opens it.
  - Loading state while fetching entry content.

- **`frontend/src/components/Sidebar.tsx`** — when Journal tab is active, the panel shows a **collapsible TOC** of recent entries (fetched from `GET /api/journal`). Clicking an entry opens it in the main area. A "New entry" button at the top. Hovering over the "Journal" panel title shows a `+` icon to start a new entry.

- **`frontend/src/types/api.ts`** — add journal types:
  ```typescript
  export interface JournalEntry {
    id: string;
    title: string;
    updated_at: string;
  }
  export interface JournalEntryDetail {
    id: string;
    title: string;
    content: string;
    created_at: string;
    updated_at: string;
  }
  ```

- **Selected journal entry state** — lives in `TabContext` or a separate `JournalContext`: `{ selectedEntryId, setSelectedEntryId }`.

## Capabilities

### New Capabilities

- `journal-entries`: rich text journaling. Users can write notes in rich text (bold, italic, headings, lists via TipTap StarterKit). Entries are auto-saved to SQLite. Titles are auto-generated from the first line of content. Recent entries appear in the sidebar TOC for quick navigation.

### Modified Capabilities

- `ui-feed-conversations`: layout. The Journal tab renders in the main area with the sidebar showing the entry TOC.

## Not In Scope

- Books tab (deferred — single-book dogfood).
- Journal entry deletion (can add later, not needed for v1).
- Journal search (entries are few, TOC is enough).
- LLM-generated titles (user said "cheap tasking model later" — for now, first-line truncation).
- Image embedding in journal (TipTap supports it, but YAGNI for v1).
- Mobile/responsive sidebar behavior.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`.
2. Clicking the Journal icon in the sidebar shows the entry TOC in the panel.
3. Clicking "New entry" creates a new entry and opens the editor in the main area.
4. Typing in the editor auto-saves after 1s debounce. Reloading the page preserves content.
5. The entry title is auto-generated from the first line (truncated to 50 chars).
6. The sidebar TOC updates to show the new/updated entry.
7. Rich text formatting works: bold, italic, headings, lists (TipTap StarterKit).
8. Hovering over the "Journal" panel title shows a `+` icon to start a new entry.
9. `uv run pytest` shows no new failures beyond the known `test_split_dyl_pdf` (BACKLOG P2).
10. `docs/product/STATUS.md` updated in the same change.
