# LifeKit — accountability partner for what you read

**Every day, LifeKit gives you one exercise to do and one idea to remember.**

LifeKit is a personal-coach app: an intelligent layer on top of book
knowledge and a venue where you do the work. It understands books
structurally (the *book model*), surfaces the right exercise or idea at the
right time (deterministic runtime + FSRS resurfacing), and gives you a local
feed + conversations UI to practice and talk things through.

LifeKit is a **coach that checks what you did** — not a tutor that checks
what you learned. No quizzes, no grades, no profiling. Local-first,
single-user, localhost only.

**Start with `.agents/intent.md`** — the standing vision. (`.claude/intent.md`
symlinks to it.)

## Current state

Stage 4 of 6 (see `.agents/intent.md`): the venue is shipped — Next.js feed +
conversations UI, feed API, `lifekit ui` boots both on localhost. Now
dogfooding the daily loop.

- Current state: `docs/product/STATUS.md`
- What's next: `docs/product/ROADMAP.md`
- User stories: `requirements/user-stories.md`
- Docs map: `docs/index.md`

## Run it

```bash
# one-time: ingest a book into the product DB, then
lifekit ui
# feed → http://localhost:3000, feed API → http://localhost:8765
```

Long model runs (extraction, evals) go to the home workstation's Ollama over
Tailscale — never run them on a small VM. Never commit secrets.

## How we build

Spec-first: OpenSpec proposals (`openspec/changes/<slug>/`) before code,
one independently testable slice per proposal, tests and done criteria up
front. The human writes the code and makes product decisions; the agent is
product owner / project manager / chief of staff. Docs stay true — update
`docs/product/{STATUS,ROADMAP,ASSUMPTIONS,BACKLOG}.md` with every change.
