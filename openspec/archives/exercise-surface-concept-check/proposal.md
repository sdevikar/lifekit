# Exercise Surface: Concept Check — Proposal

**Status: proposal only — do not implement yet.**
**Depends on:** `exercise-type-system/`, `exercise-surface-routing/`

## Why

The Feynman technique: "Explain X in your own words." Self-help books use this
constantly — "Summarize the key idea of this chapter", "Teach this concept to
a friend", "Describe Y simply". The user writes a short explanation, which
serves as both a completion record and a learning artifact.

## What Changes

### Component

**`frontend/src/components/exercises/ConceptCheckInput.tsx`** (new, `"use client"`):

- Renders in the **right pane** of the master-detail layout
- Receives `a2ui: { type: "concept_check", exercise_id, config: { prompt } }`
- Renders the prompt as a heading, a `<textarea>` below it
- Autosave: debounced 1s, `PUT /api/exercise/<id>/response` with the text
- Shows a "Saved" indicator after each autosave
- On completion, the card transitions to recents (completed)

This is intentionally similar to `JournalPrompt` — the difference is semantic
(explaining vs reflecting), not structural. If they converge in implementation,
that's fine.

### Backend

Uses the `exercise_responses` table from `exercise-type-system/`.
`response_type = 'text'`, `response_data = <the explanation>`.

### A2UI message

```json
{
  "type": "concept_check",
  "exercise_id": 45,
  "config": { "prompt": "Explain the AEIOU framework in your own words." }
}
```

## Capabilities

### New Capabilities

- `concept-check-exercise`: the user can explain a concept in their own words,
  and the explanation persists as the exercise's completion record.

## Not In Scope

- LLM grading of the explanation — the user can chat about it instead.
- Comparison against a "correct" answer — no quizzes, ever (intent.md).
- Rich text formatting — plain text for now.

## Done Criterion

1. A concept_check exercise renders in the right pane of the master-detail layout.
2. The prompt is visible and the textarea accepts input.
3. Typing and navigating away/back preserves the content (autosave works).
4. The response is stored in `exercise_responses`.
5. `npm run build` and `npm run lint` pass.
6. `uv run pytest tests/ -v` passes.
