# Combine product tracking docs — Proposal

## Why

`docs/product/` has six files that restate the same two things — *state of the
world* (what's shipped, what's broken) and *plan of work* (what's next) — so
they drift. Evidence in the repo today:

- Three "open issues" lists, none correct: STATUS says `D3–D7, H3–H4, P2–P6`;
  ROADMAP says `D3–D7, H1–H4, P1–P6`; BACKLOG actually holds `D3–D10, H3–H4,
  P2–P6`. `H1`, `H2`, `P1` are referenced but never defined.
- Two numbering systems for one roadmap: `intent.md` "Stages 1–5" vs ROADMAP
  "Steps 0–13".
- KANBAN's "Next up: fix the 3 logged bugs" lists bugs that aren't on the board;
  two of the three are already shipped.
- PHILOSOPHY duplicates `intent.md`, `docs/arch/README.md`, and
  `docs/research/lifekit-borrow-report.md`.

Every proposal's `tasks.md` already pairs "Update STATUS.md and KANBAN.md" — in
practice they are one unit.

## Decisions

- **One living tracker, named `KANBAN.md`.** `STATUS.md` is folded in and
  deleted; the merged file keeps the KANBAN name. It opens with a short
  **"How to use this file"** guide so each section's purpose is explicit.
- **`ASSUMPTIONS.md` stays a separate file** — an assumption log with IDs and
  revisit triggers is a distinct job. Only a one-line pointer changes.

## What changes

### 1. `KANBAN.md` becomes the single tracker

Structure, with what belongs in each section (this map also goes at the top of
the file):

| Section | What goes here | Merged from |
|---|---|---|
| Current state | Capability view — one row per area, status today (shipped / placeholder / proposed). No history. | STATUS area table |
| Now / In progress | Work actively being done | KANBAN |
| Upcoming | Approved or awaiting-approval proposals, ordered by dependency then value | KANBAN + ROADMAP Steps 8–12 |
| Deferred / Future | Known but not scheduled (incl. superseded proposals) | KANBAN Deferred + Future |
| Known issues | Defects + spec-vs-reality notes, stable IDs | BACKLOG D/H/P |
| Future ideas | Unapproved feature ideas | BACKLOG F1–F15 |
| Done | Shipped slices, newest first, with archive link | KANBAN Done + STATUS shipped detail |
| Open questions | Undecided design questions | PHILOSOPHY |
| Locked assumptions | Step-0 canonical text | ROADMAP |

- Reconcile the drifted open-issue lists and KANBAN's "3 logged bugs" while
  merging (keep "empty conversations" as an open issue; the other two shipped).
- ROADMAP's "rejected" items are already in `intent.md`'s never-build list — drop,
  don't duplicate.

### 2. Delete `STATUS.md`, `BACKLOG.md`, `ROADMAP.md`, `PHILOSOPHY.md`

Redistribution per the table, plus: PHILOSOPHY "UI is a first-class investment"
→ `intent.md` non-negotiable; PHILOSOPHY open questions → KANBAN "Open
questions"; everything else in PHILOSOPHY already lives in `intent.md`,
`docs/arch/`, or `docs/research/lifekit-borrow-report.md`.

### 3. Move the test inventory out of STATUS

STATUS lines 52–64 (the 13-row test map) → new `docs/arch/testing.md`.

### 4. `ASSUMPTIONS.md` — one-line pointer fix only

Line 13 `Canonical text lives in \`ROADMAP.md\`...` →
`Canonical text lives in \`KANBAN.md\` (Locked assumptions)...`. Nothing else
in the file changes.

### 5. `intent.md` (`.agents/intent.md`) — approved

**(a)** Add to "The vision", after the "off-the-shelf, multi-book app" paragraph:

> **Inspiration.** LifeKit is inspired by DeepTutor (`HKUDS/DeepTutor`; local
> checkout `/home/swapnil/workspace/projects/DeepTutor`) — a tutor with a
> deterministic learning runtime and a workbench UI. LifeKit takes that shape
> and points it at **books**: turning any book into exercises and ideas, plus
> other self-improvement content to learn and practise. Borrow/reject decisions
> are recorded in `docs/research/`.

**(b)** Add to Non-negotiables, after "Venue, not menu":

> - **UI is a first-class investment.** Design is not scaffolding; the venue
>   must look and feel like a place, not a demo.

**(c)** "Where things live": replace the ROADMAP/BACKLOG/PHILOSOPHY bullets with
a single `docs/product/KANBAN.md` entry (state + plan + known issues) and a
`docs/research/` entry (surveys + borrow report).

**(d)** "How we build → Docs stay true": the list becomes
`docs/product/KANBAN.md` (plus `ASSUMPTIONS.md` when its log changes).

### 6. `AGENTS.md` — skills + DeepTutor direction (approved)

**(a)** New section "Skills — reach for these":

> Use the `skill` tool when a task matches. The ones that matter here:
> - `impeccable` and `frontend-design` — any UI work or critique.
> - `reverse-engineer-anything` — inspecting DeepTutor or any binary/artifact with REA.
> - `ponytail` — active for all code work (the laziness ladder).
> - superpowers process skills: `brainstorming` (before building),
>   `systematic-debugging`, `test-driven-development`, `verification-before-completion`.

**(b)** Working agreement — Design source is DeepTutor:

> **Design source is DeepTutor.** The local checkout at
> `/home/swapnil/workspace/projects/DeepTutor` is the UI reference (layout,
> sidebar, chat/workbench patterns); copy what fits, read it with
> `reverse-engineer-anything`. Do not copy its quiz/mastery features (intent
> never-build).

Also update AGENTS.md's "Start here" (read `KANBAN.md`, not `STATUS.md`).

### 7. Repoint live references

- `README.md` (24–25), `docs/index.md` (product row + "Docs stay true" line 22),
  `docs/backend/README.md` (4, 10), `docs/algorithms/README.md` (5, 22),
  `docs/requirements/appendix.md` → `KANBAN.md` / `docs/research/`.
- `.serena/memories/core.md` (13, 25) → update the memory, then re-run
  `tools.serena.onboarding()`.
- Pending `openspec/changes/*/tasks.md` (step-8/9/10/11, chat-surface-b,
  chat-surface-c) → "Update `docs/product/KANBAN.md`".
- Archived `openspec/archives/` and `docs/archive/` are history — leave untouched.

## Capabilities

### Modified Capabilities

- `product-docs`: one living tracker (`KANBAN.md`) replaces
  STATUS/KANBAN/BACKLOG/ROADMAP/PHILOSOPHY; `ASSUMPTIONS.md` unchanged but for a
  pointer.

## Not in scope

- Git-hook enforcement of the tracker update (separate conversation).
- Re-deciding or re-opening anything in `ASSUMPTIONS.md`.
- Rewriting archived proposal/plan history.

## Done criteria

1. `docs/product/` contains only `KANBAN.md` and `ASSUMPTIONS.md`.
2. `STATUS.md`, `BACKLOG.md`, `ROADMAP.md`, `PHILOSOPHY.md` deleted; no live
  reference to them remains (archives excepted).
3. KANBAN opens with a "How to use this file" section map and covers: current
  state, in-progress, upcoming, deferred, known issues, future ideas, done, open
  questions, locked assumptions.
4. Test inventory lives in `docs/arch/testing.md`.
5. `intent.md` and `AGENTS.md` updated as approved above.
6. The drifted facts are reconciled into one correct open-issue list.
8. No code or tests touched; `make lint` still clean.
