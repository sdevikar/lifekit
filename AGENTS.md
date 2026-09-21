# AGENTS.md — LifeKit coding-agent instructions

These instructions are for the coding agent (OpenCode). The product owner is
Atlas; the human (Swapnil) writes the code with you and makes all product
decisions.

## Intent: two artifacts, one workflow

LifeKit runs the AI-native SDLC intent practice (Claude Academy "Capture as
`intent.md`"). OpenCode has no native support for it, so these rules stand in
for it — follow them exactly.

There are two intent artifacts:

1. **`intent.md` (repo root)** — the *standing product intent*: mission,
   non-negotiable rules, never-build list, gates. Derived from
   `docs/product/PHILOSOPHY.md`; on any conflict, `intent.md` wins. Every change is
   checked against it.
2. **`intent/<slug>.md`** — the *per-change proto-spec*: problem, proposed
   outcome, affected users/systems, constraints, open questions. Template:
   `intent/_template.md`.

### The workflow (this is what keeps the SDLC in check)

1. **Every change starts as an intent.** No spec without an approved intent;
   no code without a spec. When the human describes a change in chat, draft
   it as `intent/<slug>.md` from the template — brainstorm first (scope,
   users, constraints, what success looks like) until it is concrete.
2. **PO review before commit.** Atlas (product owner) reviews and corrects
   the draft; the verdict goes in the intent's PO-review section.
3. **Human approval is the gate.** Accept = the intent enters Design
   (becomes an OpenSpec proposal). Reject = closed, no further work. The
   human alone approves; the agent never self-approves.
4. **Check against standing intent.** Every per-change intent must be
   consistent with root `intent.md` (rules, never-build list, gates). A
   gated item (F-items, learning-runtime work, new UI framework) needs its
   gate resolved first — surface it, don't code past it.
5. **Intent is stable once spec'd.** Changes to an intent after its spec is
   written are a smell — flag them to the human instead of silently
   absorbing them.
6. **Standing `intent.md` changes only on human approval.** Propose the
   exact diff and wait for explicit approval; never amend it unilaterally.
   If the human says something contradicting it, surface the conflict
   before doing anything else. If work reveals it is stale, flag it and
   propose an update — do not silently drift.

At the start of every task or session: read `intent.md` first, then
`docs/product/STATUS.md` for current project state.

## Working agreements

- **Spec-first:** OpenSpec proposals before code; tests and done criteria
  defined before implementation.
- **Minimal diffs:** the smallest change that satisfies the spec. No
  speculative generality, no drive-by refactors.
- **Docs stay true:** keep `docs/product/STATUS.md`, `docs/product/ROADMAP.md`, `docs/product/ASSUMPTIONS.md`,
  `docs/product/BACKLOG.md` accurate with every change.
- **Push discipline:** fetch `origin/main` first; one consolidated commit
  per unit of work; verify the remote tree after pushing.
- **Local-first:** long evals run on the home workstation's Ollama, never
  on this VM. Never commit secrets.
