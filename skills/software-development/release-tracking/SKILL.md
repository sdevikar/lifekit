---
name: release-tracking
description: Use when closing an OpenSpec change or completing a phase — updates README status, archives specs, creates release notes, and commits atomically to maintain current lifecycle documentation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [release, tracking, docs, openspec, lifecycle]
    related_skills: [hermes-agent-skill-authoring, plan]
---

# Release Tracking for OpenSpec Change Closure

## Overview

Provides a repeatable process for documenting lifecycle state after closing OpenSpec proposals. After every major feature or phase closeout, this skill ensures the project has accurate release documentation — updated README status tables, archived specs, release notes, and an internal release ledger for future sessions to reference.

## When to Use

- After completing a Phase or major feature set that closes an OpenSpec change
- Before starting a new Phase so current status is documented
- Whenever you need a changelog-style summary of what shipped in each release

**Don't use for:** minor fixes (typos, doc tweaks), ongoing feature work that isn't ready to ship yet.

## Workflow

### Step 1 — Verify Completion State

Before closing anything, confirm all required deliverables are built and verified:
- All Python files compile (`py_compile` or import tests pass)
- Database schema exists at the expected path with correct tables/columns
- No pending TODO items remain within scope (deferred → documented explicitly)

**Verification:** Run `find <project>/lifekit -name "*.py" | xargs python3 -m py_compile 2>&1` — all must succeed.

### Step 2 — Update tasks.md with Actuals

Read the change's `tasks.md`:
- Mark completed items with `[x]`, append brief actuals (file names, line counts, key features shipped)
- Keep unfinished items as `[ ]` but mark explicitly DEFERRED with reason (e.g., `**DEFERRED**: No test files yet; running py_compile as interim validation`)
- Add a final summary paragraph: "Current state: N files compiled, tables exist (empty data), next step: Phase N"

### Step 3 — Archive the Completed Change

Once tasks.md is full-closed:
```bash
mkdir -p openspec/archives/old-change-name
mv openspec/changes/old-change-name/* openspec/archives/old-change-name/
echo "# ARCHIVED $(date +%Y-%m-%d)" >> openspec/archives/old-change-name/proposal.md
rmdir openspec/changes/old-change-name/
```

### Step 4 — Update README.md Release Log

Add a new row to `## Release Log` (or create the section if absent):
```markdown
## Release Log
| Version | Date | Summary |
|---------|------|---------|
| v0.Y.Z  | YYYY-MM-DD | Phase N: <one-line feature summary> |
```

Also add a "### Current Status" subsection near the top of README describing what's built vs not-yet-built (tables, files, features).

### Step 5 — Update pyproject.toml Version

Bump `version` in `[project]` section:
- PATCH (0.1.0 → 0.1.1): bugfixes only
- MINOR (0.1.0 → 0.2.0): new features, non-breaking
- MAJOR (1.0.0 → 2.0.0): breaking changes

### Step 6 — Write Internal Release Note

Create ledger entry for future sessions:
```bash
mkdir -p .hermes/cron/releases/
cat > .hermes/cron/releases/release-vX.Y.Z.md << EOF
# Release: vX.Y.Z - YYYY-MM-DD

## What Ships
- Feature 1 description
- Files: N files, ~K lines total

## Caveats / Known Issues  
- None (or list them explicitly)

## Next Up
- Phase N+1 items or pending backlog
EOF
```

### Step 7 — Commit Atomically

```bash
git add openspec/archives/ README.md pyproject.toml .hermes/cron/releases/
git commit -m "docs(vX.Y.Z): release — <one-line summary>"
```

**IMPORTANT:** Must be atomic — all related changes in one commit. Never split docs, versions, and archives across commits.

## Verification Checklist

- [ ] `tasks.md` uses `[x]` for completed items (not `-` or blank); deferred items have explicit reasons
- [ ] README release log has new version entry with date + summary
- [ ] pyproject.toml version bumped to match the release
- [ ] Archive directory exists at `openspec/archives/<old-change-name>/`; source removed from `changes/`
- [ ] Internal release note written to `.hermes/cron/releases/release-vX.Y.Z.md`
- [ ] README "Current Status" section accurately reflects what exists on disk vs roadmap
- [ ] `git add . && git diff --cached --stat` shows only the 5 expected changed files/dirs
- [ ] Commit message follows convention: `docs(vX.Y.Z): release — <summary>`

## Common Pitfalls

1. **Leaving deferred items as blank `[ ]`** — always add **DEFERRED** with reason; blank implies still-pending which confuses future status checks.

2. **Archiving tasks.md before closing it** — the archive must contain a fully-closed tasks.md (all items marked [x] or DEFERRED). Update first, then move.

3. **Forgetting to bump pyproject.toml version** — the version field is the source of truth for what's shipped; mismatched versions break downstream expectations.

4. **Not writing internal release notes** — without a `.hermes/cron/releases/` entry, future sessions can't determine from docs alone what changed between phases. Most-skipped step and most common re-entry confusion.

5. **Splitting the commit across multiple `git add`** — always batch all file changes into one atomic commit. Split commits make it impossible to see what shipped together.

6. **Updating README without updating tasks.md** — both must match at closure time. If tasks say "Deferred" but README says "Complete", future agents will believe the wrong state.

7. **Writing vague release summaries** — instead of "Phase done," write "Phase 0: scaffold, DB schema, PDF ingestion, plan forge with teaching methods, MCP server — 11 files ~1059 lines." Specificity prevents re-work later.

## One-Shot Commands

```bash
# Quick archive + status update for any open change (assuming tasks are already closed):
cd /path/to/project && mkdir -p openspec/archives
mv openspec/changes/<name> openspec/archives/
echo "# ARCHIVED $(date +%Y-%m-%d)" >> openspec/archives/<name>/proposal.md

# Add release to README (append this block):
cat >> README.md << EOF
## Release Log  
| Version | Date | Summary |
|---------|------|---------|
| vX.Y.Z | $(date +%Y-%m-%d) | <one-line summary> |
EOF

# Commit atomically:
git add openspec/archives/ README.md pyproject.toml .hermes/cron/releases/
git commit -m "docs(v$(python3 -c 'import tomllib; print(tomllib.load(open(\"pyproject.toml\"))["project"]["version"]))): release — <short summary>"

# Write internal release note:
cat > .hermes/cron/releases/release-vX.Y.Z.md << EOF
# Release: vX.Y.Z - $(date +%Y-%m-%d)
## What Ships  
- <feature descriptions>

## Caveats / Known Issues  
- <none or list them>

## Next Up  
- <next phase items>
EOF
```
