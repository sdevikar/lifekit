---
name: self-review
description: >
  Reviews your own change with the built-in /code-review, verifies each
  finding, rates each fix, and implements only the fixes you approve. Writes
  the report to .devflow/reviews/. Use before or after a push, or when the user
  asks to review their own branch, diff, or PR.
argument-hint: "[low|medium|high]"
---

## What this skill does

Picks what to review, runs `/code-review` at an effort level the user confirms,
and feeds the findings into the shared review loop. It adds no review logic of
its own.

Arguments: $ARGUMENTS

---

## Step 1 — Pick the target

| Situation | Check | Target |
|---|---|---|
| The branch has a PR | `gh pr view --json number` succeeds | The PR number |
| No PR, and unpushed commits | No upstream, or `git rev-list @{u}..HEAD` prints a line | No target |
| No PR, and everything is pushed | — | `<default branch>...HEAD` |

Find the default branch with `git symbolic-ref --short refs/remotes/origin/HEAD`,
without the `origin/` prefix. Use `main` if that fails.

A range leaves out the working tree. So for a `<default branch>...HEAD` target,
run `git status --short` first. If it prints a line, ask the user to commit
first. Wait for the answer.

## Step 2 — Confirm the effort level

If the user gave `low`, `medium`, or `high`, use it and skip this step.

Otherwise suggest one from the diff, and wait for the user to confirm:

| Diff | Suggest |
|---|---|
| Only markdown files | `low` |
| A few files, no security, auth, CI, or data code | `medium` |
| Many files, or security, auth, CI, or data code | `high` |

## Step 3 — Run the review

Invoke the built-in `code-review` skill with `<level> <target>` as its
arguments. Leave out the target when step 1 gave none.

In a terminal, the review runs in the background. End your turn, and write no
report until the findings arrive. Then continue with step 4.

## Step 4 — Run the review loop

The report path is `.devflow/reviews/review_<slug>_<YYYYMMDD>.md` in the project
root. Build `<slug>` as `devflow:handoff` does: the branch name with `/`
changed to `-`, or a short kebab-case topic on `main`, `master`, or a detached
HEAD. On a re-run, reuse the newest `.devflow/reviews/review_<slug>_*.md`, even
from an earlier day.

Read `${CLAUDE_PLUGIN_ROOT}/references/review-loop.md` and follow it, with:

- **Findings** — the `/code-review` findings.
- **IDs** — `[r1]`, `[r2]`, … in the order the findings arrive. On a re-run,
  match each finding to an existing row by file and issue, not by line. Do not
  add a row for a match. Number new findings after the highest existing `[r<n>]`.
- **Report path** — the path above.

---

## Constraints

- Never commit without the approval gate in the loop.
- Never push unless the user asks.
