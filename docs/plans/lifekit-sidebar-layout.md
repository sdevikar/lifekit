# LifeKit Sidebar Layout — Plan

**Date:** 2026-09-30
**Status:** Draft — awaiting human approval

## Goal

Change the app layout from a single-column centered feed to a chat-app-style layout: left sidebar with vertical tabs (Feed, Journal, Chat), main content area on the right. Keep the existing theme system and color scheme untouched.

## Reference Patterns

- **DeepTutor**: Far-left icon strip → collapsible sidebar panel → main content area
- **ChatGPT**: Left sidebar with conversation list (collapsible) → main chat area
- **Open WebUI**: Same pattern as ChatGPT

Common pattern: vertical icon strip (always visible) + collapsible panel (shows selected tab's navigation) + main content area.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│ ┌──────┐ ┌─────────────────┐ ┌─────────────────────────┐ │
│ │ Icon │ │  Sidebar Panel  │ │                         │ │
│ │ Strip │ │  (collapsible)  │ │    Main Content Area    │ │
│ │      │ │                 │ │                         │ │
│ │ Feed │ │  Journal TOC    │ │  Feed / Journal Editor  │ │
│ │ Jour │ │  or Chat List   │ │  or Chat Conversation   │ │
│ │ Chat │ │                 │ │                         │ │
│ │      │ │                 │ │                         │ │
│ └──────┘ └─────────────────┘ └─────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## What Changes

### 1. Layout Shell (`layout.tsx` + new `Sidebar` component)

- `layout.tsx` wraps children in a flex row: `<Sidebar />` + `<main>`
- New `Sidebar` component:
  - Icon strip (far left, ~56px): Feed, Journal, Chat icons — always visible
  - Panel (expands to ~280px, collapsible): shows navigation for the active tab
  - Collapse toggle button
- Active tab state in React context (`TabContext`)

### 2. Feed Tab (default)

- Sidebar panel: minimal — app name/logo, day summary
- Main area: existing feed content (TodayHeader, ExerciseCard, ResurfacedIdeaCard, FadingIdeasCard, MasterComposer)
- "Recent Conversations" card removed from feed (moved to Chat tab)

### 3. Chat Tab

- Sidebar panel: collapsible list of recent conversations (reuses `ConversationsList`, styled for sidebar)
- Main area: active conversation (reuses `MessageList` + `ChatInput`)
- Clicking a conversation in sidebar opens it in main area
- "Talk about this" on feed cards: creates conversation, switches to Chat tab, opens it
- `/c/[id]` route auto-switches to chat tab (deep-linking preserved)

### 4. Journal Tab

- **Database**: new `journal_entries` table
  ```sql
  CREATE TABLE journal_entries (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      content TEXT NOT NULL,  -- HTML from TipTap
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
  );
  ```
- **API endpoints** (in `server.py`):
  - `GET /api/journal` — list recent entries (id, title, updated_at) for TOC
  - `POST /api/journal` — create new entry
  - `GET /api/journal/<id>` — get single entry with content
  - `PUT /api/journal/<id>` — update entry (auto-save)
- **Sidebar panel**: collapsible TOC of recent entries (click to open in main area)
- **Main area**: TipTap rich text editor
  - Auto-save: debounced `onUpdate` → `PUT /api/journal/<id>`
  - Auto-generated title: first line of text content, truncated to ~50 chars
  - "New entry" button in sidebar panel
- **Dependency**: `@tiptap/react`, `@tiptap/starter-kit`, `@tiptap/extension-placeholder`

### 5. What Stays the Same

- Theme system (CSS variables, `light-dark()`, `ThemeToggle`) — untouched
- Color scheme, typography, card styles, button styles — untouched
- Feed API endpoints — untouched
- Conversation API endpoints — untouched
- All existing components (ExerciseCard, ResurfacedIdeaCard, etc.) — reused as-is

## File Changes

| File | Action |
|------|--------|
| `frontend/src/app/layout.tsx` | Modify — wrap in flex shell with sidebar |
| `frontend/src/components/Sidebar.tsx` | **New** — icon strip + collapsible panel |
| `frontend/src/components/JournalEditor.tsx` | **New** — TipTap editor with auto-save |
| `frontend/src/components/ChatView.tsx` | **New** — conversation view for main area |
| `frontend/src/app/feed/page.tsx` | Modify — remove ConversationsList, remove MasterComposer |
| `frontend/src/app/c/[id]/page.tsx` | Modify — wrapper that switches to chat tab |
| `frontend/src/types/api.ts` | Modify — add journal types |
| `lifekit/serve/server.py` | Modify — add journal API routes |
| `lifekit/db/schema.py` | Modify — add journal_entries table |
| `frontend/package.json` | Modify — add TipTap deps |

## Implementation Order

1. **Layout shell + sidebar** — icon strip, tab switching, collapsible panel. Feed renders in main area. No journal or chat yet.
2. **Chat tab** — conversation list in sidebar, conversation view in main area, "talk about this" switches to chat tab.
3. **Journal tab** — database table, API endpoints, TipTap editor, auto-save, auto-titles, TOC.

Each slice is independently testable and committable.

## Open Questions

1. **Sidebar collapse**: Collapsible to icon-only (like DeepTutor) or always open? Leaning collapsible.
2. **Journal title auto-generation**: First line truncated to ~50 chars — good enough?
3. **Chat URL routing**: Keep `/c/[id]` deep-linking (auto-switch to chat tab)? Leaning yes.
4. **Master composer**: Stay at bottom of feed's main area, or move to chat tab? Leaning: keep in feed.
