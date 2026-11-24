# Card-First Feed with Right Drawer — Proposal

**Status: in progress (first pass).**

## Why

The venue drifted from intent: chat became a destination tab and the sidebar became a
second navigation surface. The intent says the venue is "a local feed ... plus
grounded conversations" — one feed, with conversations attached to cards. A
separate DeepTutor-style chat tab also competes with DeepTutor itself; LifeKit
should feel like one simple place where every interaction starts with a card.

## What Changes

- Remove the left sidebar/TOC entirely. The feed is the whole page.
- Every interaction starts by tapping a feed card. Tapping opens a right-side
  drawer that slides over the feed.
- The drawer hosts the activity for that card: card context, grounded chat, and
  the exercise completion action.
- The feed remains visible behind the drawer (dimmed) so the user never loses
  place.
- Routes `/chat`, `/journal`, `/c/*` are retired in favour of the feed + drawer.
  Deep links to a conversation reopen its card's drawer.

## Layout

```
┌──────────────────────────────────────────────┐
│  Feed (full width)        │  Drawer (right)  │
│                           │                  │
│  [card]                   │  Card context     │
│  [card]  ──tap──►         │  Chat (grounded) │
│  [card]                   │  [Complete]      │
│                           │  [Close]         │
└──────────────────────────────────────────────┘
```

## Not In Scope (first pass)

- Animations beyond CSS slide-in.
- Mobile-specific drawer sizing (desktop first).
- Persisting drawer open state across reloads.

## Done Criterion

1. No sidebar renders; feed occupies full width.
2. Tapping a card opens the right drawer with that card's context.
3. Drawer contains grounded chat for the card.
4. Closing the drawer returns to the feed unchanged.
5. `npm run build` passes.