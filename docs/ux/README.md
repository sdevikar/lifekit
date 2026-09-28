# UX

## Direction (approved 2026-09-21)

LifeKit's interface is a **feed + conversations** web UI — a hybrid of a daily-briefing card feed and a DeepTutor-style grounded coach chat. Local single-user, served on localhost, no auth, no cloud, no sync (A24 in [assumptions](../product/ASSUMPTIONS.md)).

- **Feed (home):** "Today" header (book + day) → stage strip (ideas seen → retained → lived in practice) → today's-exercise card (Mark done + Talk about this) → resurfaced-idea card (Still with me + Talk about this + why-it-resurfaced note) → fading-ideas card (per-idea Talk about this) → conversations list → master composer at the bottom that opens a new conversation.
- **Conversation:** coach chat grounded in the book, with a "‹ Feed" back button. Tapping "Talk about this" on any card opens a conversation seeded on that card. Every chat is its own conversation; the user can always go back to the feed.

What the UI is *not*: quiz framing, retention percentages, grades, mastery gates. The deterministic runtime owns scheduling and state; the LLM owns conversational prose.

## Status

Shipped. The feed + conversations UI is the product interface, served via
`lifekit ui` on localhost. Spec archived at
`../../openspec/archives/step-13-ui-feed-conversations/`.
