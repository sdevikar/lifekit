# LifeKit — Project Intent

**Read this first.** This file says what LifeKit is, what it will never become,
and how we build it. If anything else in the repo contradicts this file, this
file wins. Surface the conflict instead of working around it.

The stages, and the reason behind each product decision, live in
[`docs/product/ROADMAP.md`](../docs/product/ROADMAP.md).

## What LifeKit is

**LifeKit turns a book you care about into a feed of cards, and you respond to
each card with a comment.**

A card holds one useful thing from the book: an idea, an exercise, a habit, a
journal prompt, or a question. You read the card. You write a comment: a
thought, a journal entry, a check-in, an answer. The coach replies below your
comment. That is the whole app.

LifeKit is a personal coach: an accountability partner that helps you turn what
you read into what you do. It is **not** a learning platform.

- **A tutor checks what you learned. LifeKit checks in on what you did.**
- LifeKit can ask you a question about an idea, but it never marks the answer.
  It shows the author's answer next to yours, and that is all.

LifeKit is a standalone app. It is never an Agent Skill, a plugin, or a feature
of another product.

## How it works

1. **Understand the book.** A book (PDF or EPUB) becomes a tree of sections and
   passages. The pipeline then finds typed items in it, each one tied to a
   verbatim quote. This runs offline, once per book.
2. **Turn items into cards.** Each useful item becomes a card with a type. Code
   stores each card as an OpenUI program. Nothing is generated while you look at
   the feed.
3. **Respond with comments.** The feed shows the cards in reading order. Under
   each card is a comment thread. You comment. The coach replies, grounded in
   the book and in what you wrote. You can like or dislike a card or a coach
   reply.

## The interaction model

- **One screen: the feed.** No sidebar, no tabs, no drawers, no separate chat.
  The phone and the desktop show the same single column.
- **One way to act: comment.** A journal entry, a check-in, a note on an
  exercise, and an answer to a question are all comments. The comment box
  accepts markdown.
- **One signal: reactions.** Like or dislike a card or a coach reply. A
  disliked card leaves the feed.
- **The coach always answers.** Every comment gets a reply. The reply fits the
  comment: a few warm words for a journal entry, a real answer for a question.
- **Everything the app or the model shows is OpenUI.** Cards and coach replies
  render through one OpenUI renderer. What the user types stays the user's own
  markdown.

## Principles

These hold for the life of the product.

- **Simple beats complete.** LifeKit does not have to do everything. Add a
  control only when a comment cannot do the job.
- **Grounded in the book.** Every card points to an exact passage. What the
  author says, what the author tells you to do, and what LifeKit derived stay
  visibly separate.
- **Deterministic runtime, generative surface.** Code decides which cards exist,
  their order, and their state. The model writes coach replies and, from v3,
  card layouts. Generated UI is checked before anyone sees it.
- **Doing over browsing.** Every card asks for a response. No dashboards.
- **No scores, ever.** No grades, no visible retention, no mastery gates, no
  streaks. Questions are self-checks. A reaction rates the card, not the user.
- **The user's words are never lost.** A failed coach reply never deletes or
  hides what the user wrote.
- **Beautiful is a feature.** People return to things that feel good to use.
  Spend design effort on the card and the thread, because they are the whole
  product.
- **Local-first, single user.** Localhost only. No auth, no cloud, no sync.
  Nothing leaves the machine unless the user explicitly sends it.
- **No psychological profiling.** When LifeKit remembers things about you, it
  remembers facts (what you read, did, and wrote), never an inferred persona.
- **Minimal code.** Write only what the spec needs. One path, no fallbacks kept
  "just in case".
- **Plain English.** Explain like a person, not a spec sheet.

## Never build

- Mastery machinery: BKT, IRT, KST, grades, or scores of any kind.
- Social features: other people, followers, public posts, or shared feeds. The
  comment thread is between the user and the coach only.
- Manual scheduling UI, or reflective work placed in todo lists or calendars.
- Agent Skills export, or LifeKit as a plugin inside another tool.

## Stages

| Stage | One line |
|-------|----------|
| 0. PoC | Pipeline, coach tools, and a first feed and chat. Done 2026-10. |
| 1. v1 | One book as a feed of cards, with comments, coach replies, and reactions. **Current.** |
| Dogfood | Daily real use of v1 before anything new is designed. |
| 2. v2 | A "+" button for posts not tied to a card, and a worksheet card type. |
| 3. v3 | The model writes richer card layouts in OpenUI, such as animations. |
| 4. v4 | Share a card and its context to an external chat app. |

Parked ideas, the reason for each stage, and the full decision log are in
[`docs/product/ROADMAP.md`](../docs/product/ROADMAP.md). The slices of the
current stage are in [`docs/product/KANBAN.md`](../docs/product/KANBAN.md).

## How we build

- **Spec first.** An OpenSpec proposal comes before code. Tests and done
  criteria are part of the proposal. One proposal is one slice that can be
  tested on its own.
- **Roles.** The human makes every product decision and approves every
  proposal. Agents draft proposals, write code against approved proposals, and
  keep the docs true. An agent never approves its own work.
- **Docs stay true.** The commit that merges a slice also updates
  `docs/product/KANBAN.md`, and `docs/product/ASSUMPTIONS.md` when an assumption
  changes.
- **Local-first execution.** Long model runs go to the home workstation's
  Ollama over Tailscale, never the sandbox. Never commit secrets.

Coding-agent mechanics (commands, verification, code search, git) live in
`AGENTS.md`.

## Where things live

| What | Where |
|------|-------|
| Stages, decisions, and their reasons | `docs/product/ROADMAP.md` |
| Current state, slices, known issues | `docs/product/KANBAN.md` |
| Assumptions (IDs and revisit triggers) | `docs/product/ASSUMPTIONS.md` |
| User stories | `requirements/user-stories.md` |
| Proposals | `openspec/changes/<slug>/` (pending) → `openspec/archives/<slug>/` (done) |
| Architecture | `docs/arch/` |
| Research and borrow/reject notes | `docs/research/` |
| Superseded docs (history only) | `docs/archive/` |

**Inspiration.** DeepTutor (`HKUDS/DeepTutor`; local checkout
`/home/swapnil/workspace/projects/DeepTutor`) inspired the deterministic runtime
behind a generative surface. Its tutor features (quizzes, mastery) are never
copied.

## Changing this file

This file changes only with the human's explicit approval. Propose the exact
diff and wait. If work shows the file is stale, flag it and propose the update.
