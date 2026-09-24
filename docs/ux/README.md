# UX

## Direction (approved 2026-09-21)

LifeKit's interface is a **feed + conversations** web UI — a hybrid of a daily-briefing card feed and a DeepTutor-style grounded coach chat. Local single-user, served on localhost, no auth, no cloud, no sync (A24 in [assumptions](../product/ASSUMPTIONS.md)).

- **Feed (home):** "Today" header (book + day) → stage strip (ideas seen → retained → lived in practice) → today's-exercise card (Mark done + Talk about this) → resurfaced-idea card (Still with me + Talk about this + why-it-resurfaced note) → fading-ideas card (per-idea Talk about this) → conversations list → master composer at the bottom that opens a new conversation.
- **Conversation:** coach chat grounded in the book, with a "‹ Feed" back button. Tapping "Talk about this" on any card opens a conversation seeded on that card. Every chat is its own conversation; the user can always go back to the feed.

What the UI is *not*: quiz framing, retention percentages, grades, mastery gates. The deterministic runtime owns scheduling and state; the LLM owns conversational prose.

## Spec status

- Intent (draft, awaiting approval): [`intent/ui-feed-and-conversations.md`](../../intent/ui-feed-and-conversations.md)
- Umbrella proposal + 4 slices at `../../openspec/changes/step-13-ui-feed-conversations/`:
  - 13a ✅ feed API (Flask, localhost `:8765`)
  - 13b ✅ feed screen (Next.js, component set)
  - 13c ✅ conversation view (chat UI with seed display)
  - 13d in progress — `lifekit ui` serve command
- Run: `uv sync` (Python deps) + `npx next build` (frontend) in `frontend/`, then `lifekit ui`
