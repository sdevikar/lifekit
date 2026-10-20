# Exercise Surface: Tracking — Proposal

**Status: proposal only — do not implement yet.**
**Depends on:** `exercise-type-system/`, `exercise-surface-routing/`

## Why

Many self-help exercises ask the reader to track something over time: "Log your
mood daily", "Record each time you practice X", "Track your habits for a week".
These produce a **series of data points** — not a single completion.

The current `completions` table can't represent time-series data. This proposal
adds the tracking surface.

## What Changes

### Component

**`frontend/src/components/exercises/TrackingLog.tsx`** (new, `"use client"`):

- Renders in the **right pane** of the master-detail layout
- Receives `a2ui: { type: "tracking", exercise_id, config: { metric, unit, frequency } }`
- Shows a simple input: a number (or scale) + optional note + "Log" button
- Below: a list of recent entries (last 7 days), most recent first
- Below that: a simple streak counter (consecutive days logged)
- Each entry shows the date, value, and optional note

### Backend

Uses the `exercise_tracking` table from `exercise-type-system/`.
Each entry is a row: `exercise_id, tracked_at, value (JSON), note`.

### A2UI message

```json
{
  "type": "tracking",
  "exercise_id": 43,
  "config": {
    "metric": "mood",
    "unit": "1-5",
    "frequency": "daily"
  }
}
```

## Capabilities

### New Capabilities

- `tracking-exercise`: the user can log repeated data points over time and
  see their history and streak.

## Not In Scope

- Charts or graphs — a simple list is enough for v1.
- Reminders or notifications — the feed card is the reminder.
- Goal setting or targets — the exercise config can include them later.
- Multiple metrics per exercise — one metric per tracking exercise.

## Done Criterion

1. A tracking exercise renders in the right pane of the master-detail layout.
2. The input accepts entries and the "Log" button works.
3. Recent entries display below the input.
4. The streak counter increments on consecutive days.
5. Entries persist in `exercise_tracking`.
6. `npm run build` and `npm run lint` pass.
7. `uv run pytest tests/ -v` passes.
