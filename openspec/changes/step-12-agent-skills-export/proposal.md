# Step 12: Agent Skills export — proposal

## Why

LifeKit's extraction pipeline produces a validated, quote-grounded exercise
corpus per book. That corpus is valuable beyond LifeKit's own runtime — as an
**Agent Skill** (Anthropic's Agent Skills format: `SKILL.md` + supporting
files), any agent can coach the book's exercises without LifeKit running.
This is the "distribute the extraction" play: the book becomes a portable
coaching artifact. (Built before Step 11 because it's high-leverage,
mostly reads existing tables, and doesn't depend on the coach relationship
being defined.)

## What Changes

- **New**: `lifekit export skill --book <id> --out ./skills/designing-your-life/`
  generates:
  - `SKILL.md` — frontmatter (`name`, `description`) + coaching instructions: how to run an exercise, how to log outcomes, the FSRS cadence guidance, when to use the momentum briefs
  - `exercises.md` — the full exercise catalog with steps, materials, source quotes
  - `key-ideas.md` — the book's key ideas as coaching context
  - `routines/` — optional per-routine files for multi-day practices (e.g. the 5-day Designing Your Life sprint)
- **Guardrail**: skill content is generated from the validated extraction
  tables — export **refuses** with a clear error unless the book's validation
  status is `passed` (ties directly into the Step 4 harness and the
  whitespace-normalization fix).
- **Versioning**: skill frontmatter records the LifeKit commit + extraction
  timestamp; re-export overwrites.
- **Reuse:** the Agent Skills spec itself (SKILL.md frontmatter convention);
  existing extraction/validation tables as the single source of truth.
  Richer once Steps 8–10 exist (sessions/intentions/profile can seed the
  skill's coaching instructions), but not dependent on them.

## Capabilities

### New Capabilities

- `skill-export`: validated book → portable Agent Skill directory.

## Impact

- New `../../../lifekit/export/skill.py` + CLI `lifekit export skill`. No schema
  changes. No new dependencies (Markdown generation via templates).

## Done criterion

1. Export for Designing Your Life produces a valid skill directory from the
   eval's extraction tables.
2. An independent agent session (no LifeKit MCP) can coach an exercise from
   the skill files alone (manual acceptance).
3. Export refuses unvalidated books with a clear error (tested).

## Non-goals

- Publishing skills anywhere. Export only.
- Re-export diffing (overwrite is fine for now).
