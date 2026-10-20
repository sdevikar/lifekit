# Exercise Surface Routing — Proposal

**Status: proposal only — do not implement yet.**

## Why

Every exercise originates from a feed card. When the user taps a card, the UI
transitions to a **master-detail pane** (like Copilot/Claude chat). The card is
embedded in the left pane with an animation. The exercise component renders in
the right pane. This proposal defines the routing model, the transition, and
the completion state machine.

## What Changes

This is a **frontend-only** proposal. No backend changes.

## The master-detail layout

When the user taps a feed card, the UI transitions to:

```
┌─────────────────────────────────────────────────────────────┐
│  Left pane (card context)  │  Right pane (exercise surface) │
│                            │                                │
│  ┌──────────────────────┐  │  ┌──────────────────────────┐ │
│  │ Card embedded here   │  │  │ Component renders here   │ │
│  │ (animated in from    │  │  │ based on exercise_type:  │ │
│  │  the feed)           │  │  │                          │ │
│  └──────────────────────┘  │  │  journal → JournalEditor │ │
│                            │  │  tracking → TrackingLog  │ │
│  Exercise metadata          │  │  questionnaire → Form    │ │
│  - prompt / purpose        │  │  concept_check → Input    │ │
│  - type icon + label        │  │  worksheet → Form        │ │
│  - source chapter          │  │  action → ActionSteps    │ │
│  - due date                │  │                          │ │
│                            │  │                          │ │
│  [← Back to feed]          │  │  [Complete]              │ │
└─────────────────────────────────────────────────────────────┘
```

## The transition

1. User taps a feed card.
2. The card **animates** from its feed position into the left pane (FLIP
   animation or similar — the card visually "moves" into the master pane).
3. The right pane fades in with the exercise component.
4. The feed collapses to the background (or slides away).

The animation communicates: *this card is now the context for the activity.*

## Exercise state machine

An exercise has three states that determine what happens when the user
navigates away:

| State | What happens on back | Where the card goes |
|-------|---------------------|---------------------|
| **Unchanged** — user opened but didn't interact | Card returns to the feed | Feed |
| **In-progress** — user started but didn't complete | Card stays in a "draft" area; user can resume | Recents (marked in-progress) |
| **Completed** — user finished the exercise | Card is saved as a completed activity | Recents (marked completed) |

### Recents tab

The existing Recents tab (currently conversations-only) becomes the home for
**all recent activity** — conversations and exercises together.

Each recents item shows:
- The exercise type icon
- The exercise title
- The completion status (completed / in-progress)
- The date

Tapping a completed exercise reopens the master-detail pane in read-only mode.
Tapping an in-progress exercise reopens it in editable mode.

## Type icons

Each exercise type has a suggestive icon next to the summary title:

| exercise_type | Icon | Suggests |
|---------------|------|----------|
| `action` | checkmark / todo list | Doing something |
| `journal` | notebook / pencil | Writing reflectively |
| `tracking` | chart / graph | Logging over time |
| `questionnaire` | question mark / list | Self-assessment |
| `concept_check` | lightbulb | Explaining an idea |
| `worksheet` | table / grid | Filling in a template |

Icons are hand-rolled SVG (the frontend has zero component-library deps).
They appear on the feed card, in the master pane, and in recents.

## Not In Scope

- The exercise surfaces themselves — separate proposals.
- The A2UI message format from the backend — separate proposal.
- The animation implementation details (FLIP vs framer-motion) — decide during
  implementation.
- Mobile-specific behavior — desktop first, mobile follows.
- The recents tab UI changes — that's part of this proposal but the detailed
  layout is implementation-specific.

## Done Criterion

1. Tapping a feed card transitions to a master-detail pane with the card on
   the left and the exercise component on the right.
2. The card animates from the feed into the left pane.
3. The right pane renders the correct component for the exercise type.
4. Type icons appear next to exercise titles in the feed, master pane, and
   recents.
5. Completing an exercise sends the card to the recents tab.
6. Back with no changes returns the card to the feed.
7. Back with in-progress changes keeps the card in recents (in-progress).
8. `npm run build` and `npm run lint` pass.
