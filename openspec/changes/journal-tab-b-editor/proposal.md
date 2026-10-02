# Journal Tab B — Editor — Proposal

Slice B of the deferred Journal Tab. Builds on slice A
([`../journal-tab-a-storage-api/`](../journal-tab-a-storage-api/)).

## Why

Once storage exists, the missing half is a place to actually write. This slice
delivers the editor and its autosave behavior, with the sidebar TOC deferred to
slice C.

## Dependency decision (must be resolved before implementation)

Two options, and they are not equivalent:

| | TipTap | `<textarea>` + Markdown |
|---|---|---|
| Formatting | real WYSIWYG (bold, italic, headings, lists) | Markdown source, rendered preview or none |
| Added deps | `@tiptap/react`, `@tiptap/starter-kit`, `@tiptap/extension-placeholder` | none |
| Storage | JSON document | plain text |
| Read-back | needs a renderer to show stored entries later | trivial |

Slice A stores `content` as `TEXT`, which suits both (TipTap serializes to JSON
in that column). The human picks. Nothing else in this proposal depends on the
choice.

Note: the frontend currently has **zero** component-library dependencies — all
icons are hand-rolled SVG. A three-dependency editor is a real decision, not a
detail.

## What Changes

- **`frontend/src/components/JournalEditor.tsx`** (new, `"use client"`) — the
  editor surface for one entry.
  - Loads the entry on mount via `GET /api/journal/<id>`, shows a loading state
    while fetching.
  - Autosave: `onUpdate` debounced 1s, then `PUT /api/journal/<id>`. The 1s
    debounce is the floor; do not autosave on every keystroke.
  - Title: first line of the text content, truncated to 50 characters, sent
    with each save. A user-set title is preserved if one exists — do not
    clobber it on every keystroke.
  - "New entry" button calls `POST /api/journal` and opens the returned id.

- **`frontend/src/types/api.ts`** — add `JournalEntry` (id, title, updated_at)
  and `JournalEntryDetail` (adds content, created_at), matching the shape slice
  A serves.

## Capabilities

### New Capabilities

- `journal-entries`: the user can write an entry and it persists without a save
  button. Titles default to the first line of what was written.

## Not In Scope

- Sidebar TOC, tab navigation, deep-linking. Slice C.
- Entry deletion, search, image embedding, LLM-generated titles.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`.
2. Typing in the editor and reloading the page preserves the content.
3. Nothing is lost while typing continuously — debounce fires, not every key.
4. An entry with no title gets one from the first line, truncated at 50 chars.
5. A manually set title is not overwritten by later autosaves.
6. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
7. `docs/product/STATUS.md` updated in the same change.