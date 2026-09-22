# Intent: Feed + conversations UI

**Author:** Atlas (product owner) — from Swapnil's approved mock direction
**Date:** 2026-09-21
**Status:** approved 2026-09-21 (human approval; enters Design as OpenSpec proposal)
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

## Pillars

The project decomposes into seven pillars, each independently workable
against a stable interface. Step 13 needs only some of them.

1. **Book pipeline (intake)** — Steps 1–4: split → extract → reduce/dedupe →
   validate. Turns a published book PDF into validated, quote-grounded
   exercises + key ideas registered under a `book_id`. Interface: "a
   structured book in the store." Its evals are its own gate.
2. **Book store & model** — SQLite schema + multi-book registry (Step 6;
   `docs/backend/BOOK_MODEL.md` proposal). The data contract every pillar
   reads and writes: chapters, sections, exercises, key ideas, completions,
   conversations. Facts-only — no user profiling.
3. **Resurfacing engine** — deterministic scheduling (Step 7, FSRS-adapted).
   Reads completion history + "still with me" signals; emits today's
   exercise, today's resurfaced idea, and fading ideas. Owns scheduling,
   surfacing, and state.
4. **Coach actions** — the deterministic action surface (Step 5:
   `list_exercises`, `get_exercise`, `log_completion`, `next_exercise`;
   MCP tools). The write path: records what the user did, with completion
   provenance (self-declared vs assessed).
5. **Retrieval (RAG)** — chunking + retrieval over book content for
   grounding. Supports chat citations, reference lookups, deep dives. Not
   the differentiator; a quality upgrade is explicitly later (BACKLOG
   F9–F11).
6. **Grounded chat** — the conversational coach: LLM replies grounded in the
   book via retrieval; conversations seeded from feed cards; one stored
   conversation per chat. The runtime owns state and turn structure; the LLM
   owns the prose.
7. **Feed UI** — the local web frontend: feed cards, stage strip,
   conversations list, master composer, conversation view. Framework TBD
   (open question 1).

Proposed but not committed — **Program layer** (Steps 8–11: coaching
sessions, momentum, interviewer): a future eighth pillar, not a dependency
of this change.

Cross-cutting, not pillars: per-pillar evals/quality gates, the intent/SDLC
workflow itself, docs, and the standing constraints (local-first, facts-only
user model, notifications deferred until the loop is proven).

## Affected users and systems

Single user (Swapnil). Touches: the daily briefing (Steps 5 + 7 — coach tools
and resurfacing schedule feed the cards); the store (new conversation storage +
completion logging from Mark done / Still with me); the coach LLM (replies
grounded in the book); a new UI layer (`frontend/` exists as a stub). The
throwaway Streamlit dogfood UI (`../ui/app.py`) is superseded by this.

## How this change maps to the pillars

- **New:** Feed UI (pillar 7); the grounded-chat surface (pillar 6 — a new
  surface on the existing retrieval + LLM plumbing); conversation storage
  (pillar 2 — one additive table, schema TBD in the spec).
- **Reused as-is:** the resurfacing engine's outputs (pillar 3) feed the
  cards; coach actions (pillar 4) back Mark done / Still with me.
- **Untouched:** the book pipeline (pillar 1) and retrieval internals
  (pillar 5) — chat uses retrieval exactly as it exists today.

This settles open question 5: the feed needs only pillars 2, 3, 4, 6,
and 7. Steps 5 + 7 are sufficient for v1; the program layer (Steps 8–12)
is not a dependency.

## Constraints

Standing constraints from `../intent.md` that bound this change: local-first,
single user, localhost only, no auth / no cloud / no sync (A24). Deterministic
runtime owns scheduling, surfacing, and state; the LLM owns conversational
prose. Facts-only user model — no profiling, no inferred persona. Minimal code: the
smallest diff that satisfies the spec. The UI framework is **Next.js**
(decided 2026-09-21 on the human's explicit approval; recorded in
`../intent.md` Gates).
Long evals run on the home workstation Ollama, not this VM. Docs stay true —
`../docs/product/ROADMAP.md` / `../docs/product/ASSUMPTIONS.md` / `../docs/product/STATUS.md` updated with this change.

## Open questions

1. UI framework: **decided 2026-09-21 — Next.js** (human approval;
   plain HTML/CSS/JS rejected as too simplistic). DeepTutor's web UI is
   Next.js 16 + React 19 + TypeScript + Tailwind (per its repo's
   `web/package.json`) — the reference stack, not a mandate to match
   versions. Recorded in `../intent.md` Gates per the standing contract.
2. Served how — a `lifekit ui` command on a localhost port? Which port, and does
   it share a process with anything else?
3. Conversation storage: new table(s) in the existing SQLite store — schema TBD
   in the spec.
4. What happens to `../ui/app.py` (Streamlit dogfood) — remove now or leave until
   the new UI is dogfood-ready?
5. Does the feed need Steps 8–12 (sessions, momentum) first, or are Steps 5 + 7
   enough for v1? (PO recommendation: 5 + 7 are enough; sessions come later.)

## PO review

- Reviewed by: Atlas (product owner) — 2026-09-21
- Verdict: **approved** — human approved 2026-09-21; enters Design as
  `openspec/changes/step-13-ui-feed-conversations/`
- Notes: PO review pass added the Pillars section and the pillar mapping,
  cross-referenced against `../intent.md` and `../docs/product/ROADMAP.md`;
  open question 1 resolved to Next.js on human approval (DeepTutor stack
  datapoint). No conflicts with the standing contract.
