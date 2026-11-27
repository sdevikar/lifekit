# Exercise Surface: Journal — Proposal

**Status: proposal only — do not implement yet.**
**Depends on:** `exercise-type-system/`, `exercise-surface-routing/`

## Why

Self-help books frequently ask the reader to write reflectively: "Describe a
time when you...", "Write about how you would apply...", "Reflect on your
experience with...". These are journaling exercises — they produce a text
artifact in response to a specific prompt.

The existing Journal Tab proposals (`journal-tab-a/b/c/`) are for
**free-writing** — a blank page. This proposal is for **prompt-driven**
journaling: the card shows a prompt, the user writes, the response is stored
as the exercise's completion.

## What Changes

### Component

**`frontend/src/components/exercises/JournalPrompt.tsx`** (new, `"use client"`):

- Renders in the **right pane** of the master-detail layout
- Receives `a2ui: { type: "journal", exercise_id, config: { prompt } }`
- Renders the prompt as a heading, a `<textarea>` below it
- Autosave: debounced 1s, `PUT /api/exercise/<id>/response` with the text
- Shows a "Saved" indicator after each autosave
- On completion, the card transitions to recents (completed)

### Backend

Uses the `exercise_responses` table from `exercise-type-system/`.
`response_type = 'text'`, `response_data = <the written text>`.

### A2UI message

```json
{
  "type": "journal",
  "exercise_id": 42,
  "config": { "prompt": "Describe a time when you successfully applied the 5 Whys technique." }
}
```

## Capabilities

### New Capabilities

- `journal-exercise`: the user can write a reflective response to a prompt,
  and it persists as the exercise's completion record.

## Not In Scope

- Rich text formatting (TipTap) — plain text for now.
- LLM-generated prompts — the prompt comes from the book extraction.
- Free-writing journal — that's the separate Journal Tab surface.
- Markdown rendering of responses — plain text display.

## Done Criterion

1. A journal exercise renders in the right pane of the master-detail layout.
2. The prompt is visible and the textarea accepts input.
3. Typing and navigating away/back preserves the content (autosave works).
4. The response is stored in `exercise_responses`.
5. `npm run build` and `npm run lint` pass.
6. `uv run pytest tests/ -v` passes.
