# LifeKit — accountability partner for what you read

**LifeKit turns a book you care about into a feed of cards, and you respond to
each card with a comment.**

A card holds one useful thing from the book: an idea, an exercise, a habit, a
journal prompt, or a question. You write a comment: a thought, a journal
entry, a check-in, or an answer. The coach replies, grounded in the book and
in what you wrote.

LifeKit is a **coach that checks in on what you did**, not a tutor that checks
what you learned. No quizzes, no grades, no profiling. Local-first,
single-user, localhost only.

**Start with `.agents/intent.md`** — the standing vision. (`.claude/intent.md`
symlinks to it.)

## Current state

Stage **v1** (see `docs/product/ROADMAP.md`): one book as a feed of cards, with
comments, coach replies, and reactions. The seven v1 slices are proposed in
`openspec/changes/`. What runs today is the PoC: the pipeline, a daily-briefing
feed, and a free chat, which v1 replaces.

- Stages and the reason for each decision: `docs/product/ROADMAP.md`
- Current state + what's next: `docs/product/KANBAN.md`
- User stories: `requirements/user-stories.md`
- Docs map: `docs/index.md`

## Run it

```bash
# one-time: ingest a book into the product DB, then
lifekit ui
# feed → http://127.0.0.1:3783, feed API → http://127.0.0.1:8765
```

Long model runs (extraction, evals) go to the home workstation's Ollama over
Tailscale — never run them on a small VM. Never commit secrets.

## How we build

Spec-first: OpenSpec proposals before code, one independently testable slice
per proposal. The human makes every product decision and approves every
proposal; agents draft proposals and write code against approved ones. See
[`AGENTS.md`](AGENTS.md) for the full workflow.
