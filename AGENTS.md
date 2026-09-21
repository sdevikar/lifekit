# AGENTS.md — LifeKit coding-agent instructions

These instructions are for the coding agent (OpenCode). The product owner is
Atlas; the human (Swapnil) writes the code with you and makes all product
decisions.

## intent.md is the contract

- `intent.md` at the repo root is the **standing product/SDLC contract**.
  `PHILOSOPHY.md` is the rationale; on any conflict, `intent.md` wins.
- At the start of every task or session: read `intent.md` first, then
  `STATUS.md` for current project state.

## Managing intent.md (OpenCode does not support it natively)

Because OpenCode has no native intent-file support, these rules stand in for
it — follow them exactly:

1. **Check before coding.** Before writing any code, check the task against
   `intent.md`: the three product rules, the "never build" list, the SDLC
   contract, and the gates. If the task conflicts with any of them, STOP and
   ask the human. Do not reinterpret the contract to fit the task.
2. **Never edit intent.md on your own.** If the human's request implies an
   intent change, propose the exact diff and wait for explicit approval
   before touching the file.
3. **Surface contradictions.** If the human says something in conversation
   that contradicts `intent.md`, surface the conflict before doing anything
   else — do not code past it.
4. **Flag drift.** If work reveals that `intent.md` is stale or inaccurate,
   flag it and propose an update. Do not silently drift from it.
5. **Gates are hard.** The dogfood exit criterion gate and the venue-UI
   framework gate are product decisions. Do not start gated work (F-items,
   learning-runtime work, new UI framework) without a recorded decision in
   `intent.md`.

## Working agreements

- **Spec-first:** OpenSpec proposals before code; tests and done criteria
  defined before implementation.
- **Minimal diffs:** the smallest change that satisfies the spec. No
  speculative generality, no drive-by refactors.
- **Docs stay true:** keep `STATUS.md`, `ROADMAP.md`, `ASSUMPTIONS.md`,
  `BACKLOG.md` accurate with every change.
- **Push discipline:** fetch `origin/main` first; one consolidated commit
  per unit of work; verify the remote tree after pushing.
- **Local-first:** long evals run on the home workstation's Ollama, never
  on this VM. Never commit secrets.
