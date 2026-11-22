---
name: atomic-commits
description: >
  Plans and executes code changes as an ordered sequence of atomic git
  commits, with a review pause after each commit. Use before writing any code
  change, with or without a formal plan. Triggers: (1) plan-mode exit ("let's
  implement", "start coding", "go ahead", after /plan or a design-doc review);
  (2) direct implementation requests ("fix X", "add X", "change X",
  "refactor X", "update X", "can you modify…", "make this…"); (3) requests for
  commit planning, commit decomposition, "break this into commits", or
  combining commits before a push.
---

## What this skill does

Decomposes an upcoming code change into an ordered sequence of atomic commits
**before any code is written**, then executes one commit at a time with a
review pause between each. Each commit is self-contained, purposeful, and as
small as it can be without being artificial.

---

## Entry point — determine the scope

**A. Coming out of plan mode** — a written plan exists. Use it as the source of
truth for Phase 1.

**B. No prior plan** — the user gave a direct request. Before Phase 1:
1. Restate the change in one sentence.
2. Ask only the questions whose answers change the commit structure (e.g.,
   "should the config change be separate?"). Skip if the request is clear.
3. Use the request as the scope document.

In both cases, **do not write any code until the commit plan is approved.**

---

## Phase 1 — Produce the commit plan

Output a numbered commit sequence. Each entry includes:

- **Purpose** — one sentence, one logical category (e.g., "add shared retry
  utility", "implement feature logic + unit tests", "update CI config")
- **Files** — every file that will be created or modified
- **Message** — a short conventional-commit subject line

Order dependencies first: if commit N needs something from commit M, M comes
first. For a one-commit plan, state it in one line.

**Present the plan and wait for explicit approval.** The user may reorder,
split, or merge commits.

### Merge test — what belongs in one commit

Put two changes in one commit when **nobody would revert or cherry-pick one
without the other**.

| Keep together | Keep apart |
|---|---|
| A config key and the code that reads it | A refactor and a behavior change |
| A function change and its tests | Mechanical changes (renames) and logic changes |
| A new module and its unit tests | A shared utility used by several features |
| | Unrelated bug fixes found along the way |
| | Dependency bumps |
| | CI or build changes that stand alone |

If two changes touch the same file but serve different purposes, they belong in
different commits — split the work, not the file.

### Intermediate states

If a commit alone leaves the repo broken, merge it with the commit that fixes
it. Do not write scaffolding, mocks, or harness code only to keep
intermediate commits green. If a broken boundary is unavoidable, mark it in
the plan. The final commit must leave the repo buildable.

### Volume check

Over-splitting slows review as much as over-merging. A plan with more than 4
commits must state, for each commit after the fourth, why it cannot merge
with another. If no good reason exists, merge it.

---

## Phase 2 — Execute one commit at a time

For each commit, in order:

1. Implement the changes for that commit — and only that commit.
2. Run `git status`. If a listed file holds changes from outside this commit,
   stop and tell the user.
3. Stage only the files listed for this commit, by name:
   `git add <file1> <file2> ...`
4. Confirm `git diff --cached --stat` matches the plan, then
   `git commit -m "<message>"`.
5. **Show the user what was committed. Wait for explicit approval before the
   next commit.**

If the user changes scope mid-sequence, update the remaining plan first.

---

## Combine pass

On request, or before a push:

1. List commits ahead of the base: `git log --oneline <base>..HEAD`.
2. Propose combining commits that **pass** the merge test.
3. Wait for approval before rewriting. If any commit is already pushed, state
   that a force push is needed.
4. Do not use interactive rebase. For adjacent commits, use
   `git reset --soft HEAD~<n>` and recommit. For non-adjacent commits, use
   `git commit --fixup=<sha>` then
   `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash <base>`.

After a rewrite on a branch with an open PR, propose a new PR body that
states only the intent. Post it only after approval.

---

## Constraints

- **Never use `git add -A` or `git add .`.**
- **No Co-Authored-By lines** unless the user explicitly requests them.
- **Never combine unrelated changes** in one commit, even in the same file.
- **A long commit message signals an oversized commit** — split it.
