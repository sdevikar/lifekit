---
name: handoff
description: >
  Writes a handoff document for the current branch at
  .devflow/handoffs/handoff_<slug>_<YYYYMMDD-HHMM>.md, so a later session can
  continue the work with /devflow:pickup. Use when the user asks for a
  handoff, wants to save session state, or reaches a stopping point.
argument-hint: "[what the next session will focus on]"
---

## What this skill does

Writes one handoff document at a fixed path, with fixed frontmatter and fixed
sections. A new session finds it by branch, with no pasted path. If the user
passed arguments, treat them as the focus of the next session and tailor the
document to it: $ARGUMENTS

---

## Step 1 — Collect the git state

Run these from the working directory:

| Value | Command |
|---|---|
| Project root | `git rev-parse --show-toplevel` |
| Branch | `git branch --show-current` (empty on a detached HEAD) |
| HEAD | `git rev-parse HEAD` (full SHA) |
| PR and base | `gh pr view --json url,baseRefName` (skip if `gh` fails or no PR exists) |
| Base without a PR | `git symbolic-ref --short refs/remotes/origin/HEAD`, without the `origin/` prefix; else `main` |
| Time | `date +%Y%m%d-%H%M` |

## Step 2 — Build the path

`<project_root>/.devflow/handoffs/handoff_<slug>_<YYYYMMDD-HHMM>.md`

- On a feature branch, `<slug>` is the branch name with `/` changed to `-`.
  Branch `feat/foo` gives `handoff_feat-foo_20261112-1405.md`.
- On `main`, `master`, or a detached HEAD, `<slug>` is a short kebab-case topic
  that describes the work. Do not use the branch name.

## Step 3 — Make sure the folder exists

If `.devflow/handoffs/` is missing in the project root, create it. If
`.devflow/.gitignore` is missing, create it with the single line `*`. That
file makes git ignore the whole `.devflow/` folder.

## Step 4 — Write the document

Start the file with this frontmatter. Write every key, one per line, as
`key: value`. Leave a value empty when it does not apply, but keep the key.

```markdown
---
branch: <branch, or empty on a detached HEAD>
head: <full SHA>
base: <PR base branch, or the default branch>
pr: <PR URL, or empty>
status: <in-progress, or done when the user says the branch work is finished>
next: <the first next step, on one line>
---
```

Then write these sections, in this order. Write for a reader who never saw
this session.

1. **Goal** — what the work on this branch is for.
2. **Done** — what is finished, with commit SHAs where they exist.
3. **Not done** — what remains.
4. **Decisions and assumptions** — a table with the decision and its reason.
   Every decision states its reason.
5. **Open questions** — each question with the context needed to answer it.
6. **Next steps** — a numbered list. The first item matches `next`.
7. **Artifacts** — paths or URLs only. Do not copy their content. Reference
   plans, specs, reviews, PRs, and commits instead of repeating them.
8. **Suggested skills** — skills the next session should invoke, and when.
9. **How to check the state** — the commands that show where the work stands,
   for example `git log --oneline <base>..HEAD`, `git status`, and the test
   command.

## Step 5 — Report

Tell the user the path of the file and the `next` value. Tell them that the
next session shows a pointer to it, and that `/devflow:pickup` continues the
work.

---

## Constraints

- **No secrets.** Replace every token, key, or password with `<redacted>`.
- **Never commit or push the handoff.**
- **Never edit `.gitignore` without approval.**
- One handoff per run. Do not edit or delete older handoffs.
