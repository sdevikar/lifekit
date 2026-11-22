---
name: address-pr-comments
description: >
  Triages every reviewer comment on a GitHub PR: checks branch sync, fetches
  inline threads, review bodies, and general comments, verifies and rates
  each one, implements only approved fixes, and drafts fact-only thread
  replies that it posts after approval. Use when the user asks to address,
  handle, or respond to PR review comments.
argument-hint: "[PR number]"
---

## What this skill does

Turns the comments on one PR into a verified report, fixes only what the user
approves, and replies in each thread after a second approval.

Arguments: $ARGUMENTS

---

## Step 1 — Check branch and sync

1. Find the PR: the number the user passed, or `gh pr view --json number,url,headRefName`.
2. Show the user the worktree (`git rev-parse --show-toplevel`) and the branch
   (`git branch --show-current`). If the branch is not the PR's
   `headRefName`, stop and ask.
3. Run `git fetch`. Then compare by content: `git diff HEAD @{u}`.
4. If the diff is not empty, show `git log --oneline --left-right @{u}...HEAD`
   and the diff stat. Ask before you continue.

## Step 2 — Fetch every comment

Take the host from `git remote get-url origin`. Pass `--hostname <host>` and
`--paginate` on every call:

| Kind | Call | ID |
|---|---|---|
| Inline review comments | `gh api repos/{owner}/{repo}/pulls/<n>/comments` | `[c<root id>]` |
| Review bodies | `gh api repos/{owner}/{repo}/pulls/<n>/reviews` | `[v<review id>]` |
| General PR comments | `gh api repos/{owner}/{repo}/issues/<n>/comments` | `[g<comment id>]` |

- Group inline comments into threads. The root is the comment with no
  `in_reply_to_id`. One thread is one finding.
- Skip reviews with an empty body.
- Get the user's login with `gh api user --jq .login`. The user's own comments
  are replies, not findings.

## Step 3 — Run the review loop

The report path is `.devflow/reviews/review_pr<n>_<YYYYMMDD>.md` in the project
root. On a re-run, reuse the newest `.devflow/reviews/review_pr<n>_*.md`.

Read `${CLAUDE_PLUGIN_ROOT}/references/review-loop.md` and follow it, with the
fetched comments as the findings, the IDs from step 2, and this report path.

## Step 4 — Draft the replies

After the loop records each item's status, draft replies for the items that
are `fixed` or `rejected`. Items that are not approved or blocked get no reply
this round. Each reply states only the current state, in these forms:

```text
**Fixed** in <short SHA>: <what changed>. <file>:<line>
**Rejected**: <reason, with the evidence or the earlier decision>
```

- `<file>:<line>` is the location at that commit.
- When a comment is partly fixed, write one `**Fixed**` line for the fixed part
  and one `**Rejected**` line for the rest.
- Do not thank, praise, restate the comment, or describe the process.

Where each reply goes:

- **Inline thread** — one reply on the thread root:
  `gh api -X POST repos/{owner}/{repo}/pulls/<n>/comments/<root id>/replies -f body=<reply>`
- **Review bodies and general comments** — one PR comment for all of them. For
  each point, quote it in one `>` line, then put its reply below:
  `gh pr comment <n> --body-file <file>`

Skip a thread whose last message is already the user's. Skip the combined PR
comment when every point in it already has a reply from the user after it. On
a re-run with no new reviewer comments, this means nothing is posted.

## Step 5 — Post after approval

Show every draft and where it goes. **Post nothing until the user approves.**
Post only the approved drafts. Then end with the loop's quick-glance table.

---

## Constraints

- Never post, commit, or push without the user's approval.
- Never push unless the user asks.
