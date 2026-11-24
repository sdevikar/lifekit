# Card-Associated Activity & Resume — Proposal

## Why

Chat and exercises must belong to a card, not to a free-floating conversation.
Users need a way to resume an in-progress or completed activity later without
hunting through a list.

## What Changes

- A conversation is always created with a `seed_kind` of `card` + `seed_ref`
  (exercise id or idea id). Free composer conversations are removed.
- Each feed card shows its activity state: not started / in progress / completed.
- A card carries a "Resume" affordance when it has an in-progress or completed
  activity; tapping reopens the drawer at that activity.
- Completed cards move to a "Recents" strip (or stay in feed marked done) — TBD
  during implementation; first pass keeps them in feed with a done badge.

## Resume mechanism (first pass)

- Drawer state is held in the feed page (`selectedCard`). Reopening a card with
  an existing conversation reuses that conversation instead of creating a new one.
- Conversation lookup by (seed_kind, seed_ref) is added to the API.

## Not In Scope

- Full recents redesign.
- Editing a completed exercise.

## Done Criterion

1. Every conversation has a card seed.
2. A card with prior activity reopens its existing conversation.
3. Card shows in-progress/completed state.