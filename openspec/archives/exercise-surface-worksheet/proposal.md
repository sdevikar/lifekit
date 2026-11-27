# Exercise Surface: Worksheet — Proposal

**Status: proposal only — do not implement yet.**
**Depends on:** `exercise-type-system/`, `exercise-surface-routing/`

## Why

Some self-help exercises are structured templates: "Fill in this table", "Map
out your X", "Complete this framework for your situation". A worksheet has
**multiple fields of different types** — a mix of text, scales, and choices —
that together form a structured result.

## What Changes

### Component

**`frontend/src/components/exercises/WorksheetForm.tsx`** (new, `"use client"`):

- Renders in the **right pane** of the master-detail layout
- Receives `a2ui: { type: "worksheet", exercise_id, config: { fields: [...] } }`
- Renders fields sequentially:
  - `text` — single-line input
  - `textarea` — multi-line input
  - `scale` — 1-5 radio/select
  - `multiple_choice` — pick from options
- "Submit" button at the end
- On submit: `POST /api/exercise/<id>/response` with JSON `{ responses: [...] }`
- After submission, shows a completion state

### Backend

Uses the `exercise_responses` table from `exercise-type-system/`.
`response_type = 'json'`, `response_data = { responses: [{ field_id, value }] }`.

### A2UI message

```json
{
  "type": "worksheet",
  "exercise_id": 46,
  "config": {
    "fields": [
      { "id": "f1", "label": "Situation", "type": "textarea" },
      { "id": "f2", "label": "Your emotional state (1-5)", "type": "scale" },
      { "id": "f3", "label": "What you did", "type": "textarea" },
      { "id": "f4", "label": "What you learned", "type": "textarea" }
    ]
  }
}
```

## Capabilities

### New Capabilities

- `worksheet-exercise`: the user can fill in a structured template and the
  result is stored as the exercise's completion record.

## Not In Scope

- LLM analysis of the worksheet — the user can chat about it instead.
- Conditional fields (show field B only if field A = X) — all fields shown for v1.
- Multiple pages/sections — all fields on one page for now.
- Saving partial worksheets — submit or nothing (can add autosave later).

## Done Criterion

1. A worksheet exercise renders in the right pane of the master-detail layout.
2. All field types render and accept input.
3. Submitting stores the responses in `exercise_responses`.
4. After submission, a completion state is shown.
5. `npm run build` and `npm run lint` pass.
6. `uv run pytest tests/ -v` passes.
