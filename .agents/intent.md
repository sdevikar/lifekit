# LifeKit — Project Intent

**Read this first.** This is the standing vision for LifeKit: what it is,
what it will never become, and how we get from proof-of-concept to a product.
If anything else in the repo contradicts this file, this file wins — surface
the conflict instead of working around it.

## The vision

**LifeKit turns the books you care about into things to do, ideas to keep,
and prompts to write — and gives you one place to do that work.**

LifeKit is a personal-coach app — an accountability partner for turning what
you read into what you do. It sits on top of your books, shows you cards
made from them, and gives you a place to do the work each card asks for and
talk it through.

LifeKit is **not** a learning platform. The distinction is deliberate:

- **DeepTutor is a tutor that checks what you learned. LifeKit is a coach
  that checks what you did.**
- LifeKit can ask you a question about an idea, but it never marks the
  answer. It shows the author's answer next to yours, and that is all. No
  grades, no scores, no retention percentages, no mastery gates. Completion
  is self-declared.

LifeKit is an off-the-shelf app. It is never an Agent Skill, a harness
extension, or a feature of something else.

**Inspiration.** LifeKit is inspired by DeepTutor (`HKUDS/DeepTutor`; local
checkout `/home/swapnil/workspace/projects/DeepTutor`) — a tutor with a
deterministic learning runtime and a workbench UI. LifeKit takes that shape and
points it at **books**. Borrow/reject decisions are recorded in `docs/research/`.

## How it works

Three parts, in this order:

1. **Understand the book** — the *book model*. A book (PDF or EPUB) becomes
   a tree of sections and passages, then a set of typed items (activities
   and ideas), each grounded in a verbatim quote. Think of it as a code
   index for books. This is where the modeling investment goes.
2. **Turn items into cards** — each useful item becomes a *card* with a
   type (insight, practice, habit, reflect, worksheet, question). The model
   writes the card's content and its UI once, offline; code validates both
   and stores them. Nothing is generated while you look at the feed.
3. **Be the place where the user does the work** — the *venue*: a feed of
   cards. Tapping a card opens a side drawer with the surface for that card
   type (a checklist, a journal, a form, a question) plus a grounded
   conversation about it. Everything you do in the drawer stays attached to
   that card.

Supporting pieces: retrieval (RAG) exists for grounding, citations, and deep
dives — it is substrate, not the differentiator.

## Principles (durable)

These hold for the life of the product.

- **Grounded in the book.** Every card points to an exact passage. What the
  author says, what the author tells you to do, and what LifeKit derived
  stay distinguishable — never silently merged.
- **Deterministic runtime, generative surface.** Code decides which cards
  exist, their order, and their state. The model writes card content, card
  UI, surface UI, and conversation prose. Generated UI is validated before
  it is stored.
- **Doing over browsing (venue, not menu).** Every card leads to an action.
  The feed and its drawer are the product; no dashboards.
- **No scores, ever.** No grades, visible retention, mastery gates, or
  streak gamification beyond a plain count. Questions are self-checks.
- **UI is a first-class investment.** The venue must feel like a place, not
  a demo.
- **Local-first, single user.** Localhost only. No auth, no cloud, no sync.
- **No psychological profiling.** When LifeKit remembers things about you,
  it remembers facts (what you read, did, wrote, said you want) — never an
  inferred persona.
- **Minimal code.** Do not write a line that isn't necessary. Smallest diff
  that satisfies the spec.
- **Plain English first.** Explain like a person, not a spec sheet.
- **Never build:** BKT/IRT/KST or other mastery machinery, social features,
  manual scheduling UI, Agent Skills export, reflective work placed in todo
  lists or calendars.

## PoC limits (temporary)

These limits exist to keep momentum, not because the ideas are wrong. Each
one has a trigger for when to revisit it.

| Limit | Why now | Revisit when |
|-------|---------|--------------|
| One book in the feed | Prove card quality on one book first. The book model stays multi-book ready. | v1 dogfood passes |
| No spaced repetition or daily selection — the feed shows every useful card in reading order | Brute force is enough to learn what "useful" means | The feed feels too long in dogfood |
| No tags or search | One book does not need them | v2 planning |
| No long-term user memory | The card history is the only memory in v1 | v2 planning |
| No knowledge graph or concept layer — only "same item" identity during extraction | No v1 feature reads a graph | Tags and semantic search are designed |
| No notifications or nudges | The core loop is not proven yet | v1 dogfood passes |
| No external-app dependencies (Anki bridges etc.), no managed memory services | Keep the stack small | A concrete need appears |

## Roadmap

| Stage | What | Status |
|-------|------|--------|
| 0. PoC pipeline + venue | PDF → exercises + key ideas (eval-gated); coach tools; FSRS; Next.js feed + chat. | Done 2026-10 |
| 1. v1 — card feed for one book | Book model v1 (PDF + EPUB), item extraction v2 with a usefulness gate, card types, generated card + surface UI, feed of cards, card drawer with persisted work and one conversation per card. | **Current** |
| 2. Dogfood v1 | Daily real use. Exit criterion in `docs/product/KANBAN.md` → Open questions. | Next |
| 3. v2 candidates | Spaced repetition / daily selection, tags + semantic search, long-term user memory, multi-book feed, program layer (coaching sessions, momentum), notifications. | Parked — not designed until stage 2 is done |

The proposals for each stage live in `docs/product/KANBAN.md` → Roadmap.

## How we build

- **Spec-first.** OpenSpec proposals before code; tests and done criteria
  defined before implementation. One independently testable slice per
  proposal — never hand the coding harness a whole stage at once.
- **The human writes the code** and makes all product decisions. Atlas
  (the agent) is product owner, project manager, and chief of staff:
  refining ideas, writing specs and designs, monitoring progress, keeping
  the project aligned with this file.
- **Docs stay true.** Whoever merges a change updates
  `docs/product/KANBAN.md` (and `docs/product/ASSUMPTIONS.md` when its log
  changes) in the same commit.
- **Local-first execution.** Long model runs go to the home workstation's
  Ollama over Tailscale, never the sandbox. Never commit secrets.

Coding-agent mechanics — commands, verification, trace usage, git/push
discipline — live in `AGENTS.md`.

## Where things live

- **User stories** (what the user does, acceptance criteria):
  `requirements/user-stories.md`
- **Current state, roadmap, known issues:** `docs/product/KANBAN.md`
- **Assumptions log (IDs + revisit triggers):** `docs/product/ASSUMPTIONS.md`
- **Surveys + borrow/reject decisions:** `docs/research/`
- **Architecture:** `docs/arch/` (`README.md` for the pipeline diagram,
  `testing.md` for the test map)
- **Proposals:** `openspec/changes/<slug>/` (pending) →
  `openspec/archives/<slug>/` (done)
- **Superseded docs:** `docs/archive/` (history only, not binding)
- **Inspiration** Deeptutor lives on this machine at `/home/swapnil/workspace/projects/DeepTutor` and on github at `https://github.com/HKUDS/DeepTutor`

## Changing this file

This file changes only on the human's explicit approval — propose the exact
diff and wait; never amend it unilaterally or silently drift. If work reveals
it is stale, flag it and propose the update.
