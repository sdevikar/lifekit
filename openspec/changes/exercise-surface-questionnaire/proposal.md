# Exercise Surface: Questionnaire — Proposal

**Status: proposal only — do not implement yet.**
**Depends on:** `exercise-type-system/`, `exercise-surface-routing/`

## Why

Self-help books often include self-assessments: "Rate yourself 1-5 on these
dimensions", "Answer these 10 questions about your current state", "Score your
progress on...". These produce a **structured result** — a set of answers to
specific questions.

## What Changes

### Component

**`frontend/src/components/exercises/QuestionnaireForm.tsx`** (new, `"use client"`):

- Renders in the **right pane** of the master-detail layout
- Receives `a2ui: { type: "questionnaire", exercise_id, config: { questions: [...] } }`
- Renders questions sequentially or all at once (depending on count)
- Question types:
  - `scale` — 1-5 (or 1-10) radio/select
  - `multiple_choice` — pick from options
  - `text` — free-text answer
- "Submit" button at the end
- On submit: `POST /api/exercise/<id>/response` with JSON `{ responses: [...] }`
- After submission, shows a completion state with a summary of answers

### Backend

Uses the `exercise_responses` table from `exercise-type-system/`.
`response_type = 'json'`, `response_data = { responses: [{ question_id, answer }] }`.

### A2UI message

```json
{
  "type": "questionnaire",
  "exercise_id": 44,
  "config": {
    "questions": [
      { "id": "q1", "text": "How often do you practice this technique?", "type": "scale", "options": [1, 2, 3, 4, 5] },
      { "id": "q2", "text": "What has been your biggest obstacle?", "type": "text" },
      { "id": "q3", "text": "Which of these describes your current state?", "type": "multiple_choice", "options": ["Just starting", "Getting consistent", "Second nature"] }
    ]
  }
}
```

## Capabilities

### New Capabilities

- `questionnaire-exercise`: the user can complete a structured self-assessment
  and the results are stored as the exercise's completion record.

## Not In Scope

- Scoring or interpretation of results — just store the answers.
- LLM analysis of responses — the user can chat about them instead.
- Conditional branching in questions — all questions shown for v1.
- Question randomization — the book defines the order.

## Done Criterion

1. A questionnaire exercise renders in the right pane of the master-detail layout.
2. All question types (scale, multiple_choice, text) render and accept input.
3. Submitting stores the responses in `exercise_responses`.
4. After submission, a summary of answers is shown.
5. `npm run build` and `npm run lint` pass.
6. `uv run pytest tests/ -v` passes.
