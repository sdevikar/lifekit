# Intent: Feed + conversations UI

**Author:** Atlas (product owner) — from Swapnil's approved mock direction
**Date:** 2026-09-21
**Status:** draft
**Supersedes:** — (retires the no-frontend clause of A8; see `../docs/product/ASSUMPTIONS.md`)

<!--
Per-change proto-spec (Claude Academy "Capture as intent.md" practice).
Every change starts here: no spec without an approved intent, no code
without a spec. Brainstorm until concrete, then fill this in.
Checked against the standing contract in ../intent.md before approval.
-->

## Problem

In Swapnil's own words: "I want the UI to be a hybrid UI between what you came
up with in your mock and what DeepTutor has (chat interface). I want the cards
like you have and a way to start a chat." Refined 2026-09-21: the home page is
a feed with cards; the redundant top-level "Start a chat" button is gone; every
card carries its own "Talk about this"; a master text box at the bottom of the
feed starts a new conversation; each chat gets its own conversation view; the
user can always go back to the feed.

The CLI + MCP interface gives no daily coaching surface. LifeKit's mission is
"every day, one exercise to do and one idea to remember" — that needs a home
screen, not a terminal.

## Proposed outcome

A local web UI with two screens:

1. **Feed (home):** "Today" header (book + day), stage strip (ideas seen →
   retained → lived in practice), today's-exercise card (Mark done + Talk about
   this), resurfaced-idea card (Still with me + Talk about this + why-it-resurfaced
   note), fading-ideas card (per-idea Talk about this), conversations list, and a
   master composer at the bottom that opens a new conversation.
2. **Conversation:** DeepTutor-like grounded coach chat beside the content —
   header with "‹ Feed" back button, conversation title, message list, input.
   Tapping "Talk about this" on a card opens a conversation seeded on that card.

Observable success: Swapnil completes a full daily loop against real book data —
open feed → do the exercise → Mark done → Talk about this on a card → start a
new chat from the composer → return to feed — all local, no quiz framing, no
probabilities shown, no mastery gates.

## Affected users and systems

Single user (Swapnil). Touches: the daily briefing (Steps 5 + 7 — coach tools
and resurfacing schedule feed the cards); the store (new conversation storage +
completion logging from Mark done / Still with me); the coach LLM (replies
grounded in the book); a new UI layer (`frontend/` exists as a stub). The
throwaway Streamlit dogfood UI (`../ui/app.py`) is superseded by this.

## Constraints

Standing constraints from `../intent.md` that bound this change: local-first,
single user, localhost only, no auth / no cloud / no sync (A24). Deterministic
runtime owns scheduling, surfacing, and state; the LLM owns conversational
prose. Facts-only user model — no profiling, no inferred persona. Minimal code:
reuse the approved mock's plain HTML/CSS/JS rather than adopting a framework.
Long evals run on the home workstation Ollama, not this VM. Docs stay true —
`../docs/product/ROADMAP.md` / `../docs/product/ASSUMPTIONS.md` / `../docs/product/STATUS.md` updated with this change.

## Open questions

1. Stack: plain HTML/CSS/JS served by the backend (PO recommendation — the
   approved mock already is this) vs. a UI framework?
2. Served how — a `lifekit ui` command on a localhost port? Which port, and does
   it share a process with anything else?
3. Conversation storage: new table(s) in the existing SQLite store — schema TBD
   in the spec.
4. What happens to `../ui/app.py` (Streamlit dogfood) — remove now or leave until
   the new UI is dogfood-ready?
5. Does the feed need Steps 8–12 (sessions, momentum) first, or are Steps 5 + 7
   enough for v1? (PO recommendation: 5 + 7 are enough; sessions come later.)

## PO review

- Reviewed by: Atlas (product owner)
- Verdict: pending — awaiting Swapnil's approval of this draft
- Notes: —
