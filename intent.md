# LifeKit Intent

**Status:** Standing product contract — 2026-09-20
**Read this before every task.** `PHILOSOPHY.md` is the rationale; this file
is the binding contract. When they conflict, this file wins until the human
updates it.

## Mission

Every day, LifeKit gives you one exercise to do and one idea to remember.

LifeKit is a personal-coach app: an intelligent, human-like layer on top of
book knowledge; a conversational venue where the user performs exercises and
reflects (with scheduling once the loop is proven); and an algorithmic coach
that surfaces the right thing at the right time.

## The loop

1. Understand each book structurally — the **book model**.
2. Surface the right exercise or idea at the right time — the **learning
   runtime**.
3. Be the place where the user does the work — the **venue**.

## Non-negotiable product rules

### 1. Deep book model, shallow user model

- Modeling investment goes into the **book**, not the person.
- The book model: structure tree (parts → chapters → sections) + typed
  actionable items (exercises, decision rules, anti-patterns, key ideas) +
  relations between items. Think code index: module tree, symbols, call
  graph. See `BOOK_MODEL.md`.
- The user model is **important facts only**: goals, constraints,
  preferences, what has been tried. NEVER build psychological profiling,
  inferred personas, or deep personalization. This is a hard boundary, not a
  tradeoff — deep user modeling would kill the project.

### 2. Venue, not menu

- The app is where exercises are **performed**, not browsed. Listing content
  is the menu; doing the exercise, reflecting, and being rescheduled is the
  venue.
- UI work serves doing. Do not add browsing surfaces, dashboards, or tabs
  that turn the venue back into a menu. Almost no book app is the venue —
  that is the opening.

### 3. Deterministic runtime, generative surface

- Scheduling, surfacing decisions, and state live in the deterministic
  **learning runtime** (MCP server). The LLM writes prose; it never owns
  decisions.
- FSRS governs resurfacing — over exercises *and* teach-backs.
- Feynman teach-backs test understanding: the user explains an idea in their
  own words, an LLM judge grades against the book model, the grade maps to
  an FSRS rating (≥0.8 Easy … <0.4 Again).
- The runtime emits signals + instructions, never canned coaching text.
  Motivation briefs are priority-ordered (milestone → reactivation →
  plateau → value-recall …), signals + instruction only.

## Things you must never build (unless this file is amended)

- Deep user modeling / personalization beyond important facts.
- Knowledge graphs.
- Anki bridges or any external-app dependency — local-first.
- BKT / IRT / KST cognitive machinery.
- Managed memory layers (Mem0). Facts live in SQLite + Markdown mirror.
- Notifications / nudges — deferred until the core loop is proven with real
  use.
- Streak gamification beyond a plain count; social features; manual
  scheduling UI.
- Agent Skills export.
- Reflective work placed in todo lists or calendars.

## SDLC contract

1. **Spec-first.** OpenSpec proposals before code. Define tests and done
   criteria before implementation.
2. **Minimal code.** Do not write a single line of code that isn't
   necessary. Smallest diff that satisfies the spec.
3. **Reuse proven open-source components.** Borrow backend, UX, and
   how-to-content ideas only where they serve the vision — never where they
   change it.
4. **Local-first.** Long-running model evals run on the home workstation's
   Ollama, never on this VM. Free OpenRouter models only, if separately
   authorized. Never restart workstation Ollama unilaterally.
5. **Never commit secrets.** Never expose credentials.
6. **Keep the docs true.** `STATUS.md`, `ROADMAP.md`, `ASSUMPTIONS.md`,
   `BACKLOG.md` stay accurate with every change.
7. **Push discipline.** Fetch `origin/main` first; one consolidated commit;
   verify the remote tree and spot-check contents after pushing.

## Gates

- **Dogfood exit criterion: UNDECIDED.** Until it is decided, no F-item and
  no learning-runtime work is unlocked. Do not start that work on your own.
- **Streamlit is scaffolding.** The venue UI framework is undecided — do not
  invest in a new framework without a decision recorded here.

## Changing this file

- This file changes **only on the human's explicit approval**. Propose the
  edit as a diff; never amend intent unilaterally.
- If the human says something in conversation that contradicts this file,
  stop and surface the conflict before writing code.
- If work reveals this file is stale or inaccurate, flag it and propose an
  update — do not silently drift.
