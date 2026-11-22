---
name: pickup
description: >
  Continues work from the current handoff for this branch. Finds the handoff
  in .devflow/handoffs/, checks it against git, reports any drift, and lists the
  next steps. Use when a session starts with a handoff pointer, or when the
  user asks to pick up, continue, or resume earlier work.
argument-hint: "[path to a handoff file]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/latest_handoff.py)
---

## What this skill does

Reads the current handoff, compares it with the git state, and reports each
difference. Then lists the next steps and waits for the user to pick one.

---

## Step 1 — Find the handoff

Arguments: $ARGUMENTS

- If the user passed a path, use that file. Skip the lookup, even if a newer
  handoff exists.
- Otherwise run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/latest_handoff.py`. It
  prints the path of the newest handoff whose `branch` matches the current
  branch and whose `status` is not `done`.
- If it prints nothing, tell the user that no open handoff matches this branch.
  Ask for a path. Stop here.

Read the whole file.

## Step 2 — Check for drift

Compare the handoff frontmatter with git. Run `git fetch --quiet` first if the
branch has an upstream.

| Check | Command | Report when |
|---|---|---|
| Branch | `git branch --show-current` | It differs from `branch` |
| HEAD | `git rev-parse HEAD` | It differs from `head` |
| New commits | `git log --oneline <head>..HEAD` | Any line is printed |
| Lost commits | `git merge-base --is-ancestor <head> HEAD` | Exit is not 0 |
| Uncommitted changes | `git status --short` | Any line is printed |
| Remote | `git rev-list --left-right --count @{u}...HEAD` | Either count is not 0 |

Report each difference as one plain sentence. For example:

- "HEAD moved by 1 commit since the handoff: `a1b2c3d fix: handle empty input`."
- "The handoff `head` is not in the current history. A rebase or reset is likely."
- "The branch is 2 commits behind its upstream."

If nothing differs, say "No drift since the handoff."

## Step 3 — Confirm before you continue

List the handoff's next steps as a numbered list. Mention open questions that
block a step. Ask the user which step to start.

**Do not start any step until the user confirms.**

---

## Constraints

- Never commit, push, or post to GitHub as part of a pickup.
- Do not edit the handoff file.
