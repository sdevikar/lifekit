# Step 13c: Conversation view — proposal

## Why

"Talk about this" is the feed's second half: a grounded coach chat seeded
on a card, with a way back. This slice fills the `/c/[id]` stub from 13b.

## What changes

- **Conversation screen:** header with "‹ Feed" back button + conversation
  title; message list (user/coach); input box pinned at the bottom.
- **Chat loop:** load via `GET /api/conversations/:id`; send via `POST
  /api/conversations/:id/messages`; render the coach reply. Request/
  response only — no streaming in v1.
- **Card seeding:** conversations created from "Talk about this" open with
  the card's exercise/idea as context (via `seed_kind`/`seed_ref` stored by
  13a); the seed is visible, not editable history.
- Back navigation always returns to the feed; each chat stays its own
  conversation.

## Done criterion

1. Full loop against the real API + dogfood DB: seed from a card → send a
   message → grounded coach reply renders → reload shows persisted history.
2. "‹ Feed" returns to the feed; reopening a conversation from the feed's
   list restores it.
3. Replies stay grounded in the book; no quiz framing, no grades.

## Non-goals

- Streaming, message editing, deleting conversations. `lifekit ui` (13d).
