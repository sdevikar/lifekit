---
branch: docs/roadmap-v2
head: a373dda26fd73d50cf422066a241e0cd003fe249
base: main
pr:
status: done
session: 4f5d21d7-2064-4192-90d9-00c50dd0f19f
summary: v1 direction (feed with comments) merged to main as docs and seven draft proposals, slices 0-6; no code changed
---

# Handoff — v1 feed with comments: intent, roadmap, proposals (2026-11-27)

`head` is the commit this session built on. The commit that adds this file
comes right after it, and `main` fast-forwards to that commit.

**Read first.** This is a personal project. The human is brainstorming and
picks it up in personal time. **Do not write code** until the human asks for a
slice by name. No code changed in this session.

To restore context on any machine:

1. Read `.agents/intent.md`.
2. Read `docs/product/ROADMAP.md`.
3. Read `docs/product/KANBAN.md` → "Now / In progress".
4. Read `DESIGN.md` before any UI work.

## What the human decided this session

| # | Decision | Where it lives |
|---|----------|----------------|
| 1 | One screen, the feed. No side drawer, sidebar, or separate chat. | ROADMAP D1 |
| 2 | A comment is the only way to act on a card (journal, check-in, notes, answers). The box takes markdown. | ROADMAP D2, D3 |
| 3 | The coach replies to every comment. A reaction-only reply is v2. | ROADMAP D4 |
| 4 | Like and dislike on cards and on coach replies. Dislike replaces "Not useful". | ROADMAP D5 |
| 5 | OpenUI for everything shown. Code builds card programs in v1; the model writes them in v3. | ROADMAP D6 |
| 6 | Worksheet and the "+" button (posts without a card) ship together in v2. Templates map to practice in v1. | ROADMAP D7, D13 |
| 7 | Free chat is retired. v4 shares a card and its context to an external chat app. | ROADMAP D10, D14 |
| 8 | Slice 0 comes first: make the app feed-only before any other slice. | ROADMAP "v1 slices", `openspec/changes/feed-only-ui/` |
| 9 | Follow the Astryx design language (rules only, not the library). | `DESIGN.md`, ROADMAP D15 |
| 10 | This direction is final. Merge the docs and proposals to `main`. | — |

## The v1 slices (all proposed, none approved)

| # | Proposal | Depends on |
|---|----------|------------|
| 0 | `feed-only-ui`: remove the sidebar, the chat pages, `/journal`, the "Talk about this" buttons, and `/api/conversations*`. Old URLs redirect to `/feed`. | — |
| 1 | `card-types-v1` | 0 |
| 2 | `book-model-v1` | 0 |
| 3 | `item-extraction-v2` | 1, 2 |
| 4 | `card-generation` | 1, 3 |
| 5 | `feed-v1` | 0, 4 |
| 6 | `card-comments` | 5 |

All seven pass `openspec validate --strict`. `feed-only-ui` replaces the
earlier `retire-free-chat` proposal (it was slice 7). It moved to the front
because `main` still shows the PoC sidebar with Feed, Journal, and Chat.

## What changed

- `.agents/intent.md`: rewritten (approved in the human's message). Roles now
  say agents write code against approved proposals.
- `docs/product/ROADMAP.md`: stages, a v1 sketch, per-type comment meaning,
  slices 0–6, decisions D1–D15, the dogfood exit check, parked items, retired
  ideas.
- `DESIGN.md` (new, repo root): the D1 layout, the D15 rules with the Astryx
  record behind each rule (pinned at `meta/astryx@550427c`), what we do not use
  from Astryx, and where the tokens live.
- `KANBAN.md`, `ASSUMPTIONS.md` (A27 retired; A29, A30 updated; A31–A34 new),
  `requirements/user-stories.md`, `README.md`, `docs/index.md`, `AGENTS.md`.
- Archived to `docs/archive/`: `requirements-2026-09/` (old requirements set),
  `ux-2026-10/` (old UX direction and token extraction), `plans-2026-10/`
  (sidebar and chat-layout plans).
- `.devflow/`: devflow's layout. `.devflow/.gitignore` ignores everything
  except `handoffs/`, so handoffs are tracked. The old `docs/handoffs/` ignore
  rule is gone.

## Findings in the current code (fixed by the proposals, not yet in code)

- `post_message` deletes the user's message when the model call fails
  (`lifekit/serve/server.py`, `generate`).
- `post_message` grounds on `app.config["book_id"]`, not the conversation's book.
- `_coach_messages` reads history after the message is stored, then appends it
  again, so the model sees the user's text twice.
- feed-only-ui deletes this code. card-comments lists the three bugs so the new
  coach code does not repeat them.
- The feed's "Talk about this" buttons open `/c/<id>` (`frontend/src/app/feed/page.tsx:24-56`).
  So from slice 0 until slice 6, the app has no way to talk to the coach. The
  proposals accept this gap.
- `TodayHeader.tsx` holds `ThemeToggle`; feed-v1 moves it to the new header.

## Waiting on the human

1. Approve the seven proposals (or ask for changes).
2. Approve the dogfood exit check: 10 of 14 days; ≤20% of reacted cards
   disliked; ≤20% of coach replies disliked.
3. Approve the 80% golden-set precision target for item extraction.
4. Decide whether to delete the remote branches listed under Notes.

## Next steps for an agent

1. After approval, implement slice 0 (`feed-only-ui`). Then slices 1 and 2 in
   parallel, then 3 → 6 in order.
2. Long model runs (extraction, question cards) go to the home workstation.
3. Update `docs/arch/` and `AGENTS.md` Architecture only when a slice lands.

## Notes

- `origin/feat/card-first-feed` (5 commits) is abandoned, not merged. Its one
  useful lesson is commit `aa4d3f3`: the local model writes
  `Card(children=[...])`, which does not render. card-comments now records the
  fix to make (a rule in `frontend/scripts/gen_openui_prompt.ts`).
- `origin/feat/ui-design-language-overhaul-2441092854256426498` is fully merged
  into `main`. It is safe to delete.
- The local ref `origin/docs/roadmap-v2` can look stale. Pushes go by URL to
  `git@github-personal:sdevikar/lifekit.git`. Run `git fetch` with that URL to
  refresh it.
- Old proposals in `openspec/changes/` (exercise-surface-*, journal-tab*,
  chat-surface*, openui-*, step-8…11) fail `openspec validate` because they
  have no specs. They are history; KANBAN lists them as superseded or parked.
- `AGENTS.md` names `GLOSSARY.md` and `docs/adr/`, which do not exist yet.
- `ponytail-review` was not available in this session.
