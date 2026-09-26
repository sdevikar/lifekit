# LifeKit — Project Intent

**Read this first.** This is the standing vision for LifeKit: what it is,
what it will never become, and how we get from proof-of-concept to a product.
If anything else in the repo contradicts this file, this file wins — surface
the conflict instead of working around it.

## The vision

**Every day, LifeKit gives you one exercise to do and one idea to remember.**

LifeKit is a personal-coach app — an accountability partner for turning what
you read into what you do. It sits on top of the books you care about,
surfaces the right exercise or idea at the right time, and gives you a place
to do the work and talk it through.

LifeKit is **not** a learning platform. The distinction is deliberate:

- **DeepTutor is a tutor that checks what you learned. LifeKit is a coach
  that checks what you did.**
- LifeKit never quizzes, never shows grades, retention percentages, or
  mastery gates. Completion is self-declared; the product's job is to show up
  with the right thing, not to score you.

LifeKit is an off-the-shelf, multi-book app. It is never an Agent Skill, a
harness extension, or a feature of something else.

## How it works

Three parts, in this order:

1. **Understand the book structurally** — the *book model*: parts →
   chapters → sections, plus typed actionable items (exercises, key ideas,
   decision rules, anti-patterns) with quote-grounded citations. Think of it
   as a code index for books. This is where the modeling investment goes.
2. **Surface the right thing at the right time** — the *deterministic
   runtime*: scheduling, surfacing, and state live in code, not in the model.
   FSRS-style spaced repetition over completion history decides what resurfaces;
   the user never sees a number.
3. **Be the place where the user does the work** — the *venue*: a local feed
   (today's exercise card, resurfaced-idea card, fading ideas, conversations
   list, composer) plus grounded conversations. The LLM writes prose; it never
   owns decisions.

Supporting pieces: retrieval (RAG) exists for grounding, citations, and deep
dives — it is substrate, not the differentiator. The user model is
deliberately shallow: durable important facts only (goals, constraints,
preferences, what has been tried). No psychological profiling, no inferred
persona — that path would kill the project.

## Non-negotiables

- **Deep book model, shallow user model.** As above; the boundary is hard.
- **Venue, not menu.** The app is where exercises are performed, not
  browsed. No dashboards, no browsing surfaces that turn doing back into
  browsing.
- **Deterministic runtime, generative surface.** Scheduling, surfacing, and
  state are code. The LLM owns conversational prose only.
- **No quiz framing, ever.** No quizzes, visible grades, retention
  percentages, or mastery gates.
- **Local-first, single user.** Localhost only. No auth, no cloud, no sync.
- **Minimal code.** Do not write a single line of code that isn't necessary.
  Smallest diff that satisfies the spec.
- **Plain English first.** Explain like a person, not a spec sheet.
- **Never build:** deep user modeling beyond important facts, knowledge
  graphs, external-app dependencies (Anki bridges etc.), BKT/IRT/KST
  cognitive machinery, managed memory layers, notifications/nudges (until the
  core loop is proven with real use), streak gamification beyond a plain
  count, social features, manual scheduling UI, Agent Skills export,
  reflective work placed in todo lists or calendars.

## Stages: PoC to product

| Stage | What | Status |
|-------|------|--------|
| 1. Book pipeline | A book PDF becomes validated, quote-grounded exercises + key ideas in SQLite. Eval-gated per stage (split → extract → reduce/dedupe → validate). | Done |
| 2. Deterministic runtime | Coach tools (list / get / log completion / next exercise), multi-book registry, FSRS resurfacing over completion history. | Done |
| 3. Venue | Next.js feed + conversations web UI; feed API on localhost; `lifekit ui` boots both. Streamlit scaffolding retired. | Done 2026-09-24 |
| 4. Dogfood & harden | Daily real use of the loop. Fix what breaks. Decide the dogfood exit criterion. **We are here.** | Current |
| 5. Program layer | Coaching sessions, momentum — *proposed, not committed*. Unlocked only after Stage 4 proves the loop. | Proposed |
| — | Notifications/nudges | Deferred until the core loop is proven |

Deliberately undecided: anything beyond Stage 5. We don't design it until
Stage 4 is done.

## How we build

- **Spec-first.** OpenSpec proposals before code; tests and done criteria
  defined before implementation. One independently testable slice per
  proposal — never hand the coding harness a whole step at once.
- **The human writes the code** and makes all product decisions. Atlas
  (the agent) is product owner, project manager, and chief of staff:
  refining ideas, writing specs and designs, monitoring progress, keeping
  the project aligned with this file.
- **Docs stay true.** Whoever merges a change updates `docs/product/STATUS.md`,
  `docs/product/ROADMAP.md`, `docs/product/ASSUMPTIONS.md`, and
  `docs/product/BACKLOG.md` in the same commit.
- **Local-first execution.** Long model runs go to the home workstation's
  Ollama over Tailscale, never the sandbox. Never commit secrets.
- **Push discipline.** Fetch `origin/main` first; one consolidated commit per
  unit of work; verify the remote tree after pushing.

## Where things live

- **User stories** (what the user does, acceptance criteria):
  `requirements/user-stories.md`
- **Current state:** `docs/product/STATUS.md`
- **What's next and why:** `docs/product/ROADMAP.md`
- **Standing assumptions:** `docs/product/ASSUMPTIONS.md`
- **Known issues:** `docs/product/BACKLOG.md`
- **Rationale and borrow/reject decisions:** `docs/product/PHILOSOPHY.md`
- **Architecture:** `docs/arch/` (pillars, daily-loop data flow)
- **Proposals:** `openspec/changes/<slug>/` (pending) →
  `openspec/archives/<slug>/` (done)
- **Superseded docs:** `docs/archive/` (history only, not binding)

## Changing this file

This file changes only on the human's explicit approval. If the human says
something contradicting it, surface the conflict before doing anything else.
If work reveals it is stale, flag it and propose the exact diff — do not
silently drift.
