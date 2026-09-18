# Step 8: Coaching session model — proposal

## Why

LifeKit's MCP tools are thin wrappers over tables — there is no notion of a
coaching *session*. Every post-MVP feature (momentum, interviewer, coach UI,
skill export) reads or writes session-scoped data. Following tutor-mcp's
architecture (deterministic engine owns state; host LLM owns prose) and
interview-forge's key insight (the **server** enforces session coherence, not
the agent's goodwill), Step 8 gives LifeKit durable coaching sessions: a
session opens, surfaces the next exercise with context, records attempts and
affect, and closes with a recap plus an optional Gollwitzer if-then intention.

## What Changes

- **Schema** (new tables):
  - `sessions(id, book_id, status /* planning|in_session|review|closed */, started_at, closed_at, open_affect_json, close_affect_json, recap_text)` — status transitions enforced server-side; a session cannot receive attempts before `in_session` or after `closed`.
  - `session_events(id, session_id, kind, exercise_id, at, payload_json)` — kinds: `exercise_presented`, `attempt_recorded`, `affect_checkin`, `brief_shown`, `reflection`.
  - `intentions(id, session_id, trigger_text, action_text, scheduled_for, status /* pending|honored|missed|cancelled */, resolved_at)` — Gollwitzer if-then commitments.
- **Markdown memory alongside the DB** (inspectable narrative layer; DB is the
  algorithmic layer): `memory/sessions/YYYY-MM-DD-<sessionid>.md` (YAML
  frontmatter: session_id, book, exercises, affect) + `memory/MEMORY.md`
  (stable learner facts).
- **MCP tools** (session grammar generalized from flashcard-mcp's card tools
  to exercises):
  - `start_coaching_session(book_id?)` — idempotent open/resume → `in_session`
  - `get_coaching_context` — session-start brief: active book, FSRS-due exercises, recent sessions, open intentions, momentum snapshot
  - `next_coached_exercise` — {exercise, fsrs_state, motivation_brief (signal+instruction), episodic_context, why_this_exercise}
  - `record_attempt(exercise_id, outcome /*completed|partial|skipped*/, reflection?, affect?)` — updates FSRS; rejected outside `in_session`
  - `end_coaching_session(implementation_intention?)` — → `review`: recap brief, Markdown session note, optional if-then intention
  - `list_intentions(status?)` / `resolve_intention(id, status)` — intention lifecycle
- **Reuse:** tutor-mcp's session/close/intention/memory patterns;
  interview-forge's server-enforced state machine; flashcard-mcp's session
  tool taxonomy; existing FSRS scheduler and completion log. No new
  dependencies.

## Capabilities

### New Capabilities

- `coaching-sessions`: durable sessions, attempts, affect, intentions, Markdown memory.

## Impact

- New package `lifekit/sessions/`; new tables; new MCP tools (server wiring
  per BACKLOG H1 — this step lands the coach tools on the MCP server for real).
- CLI: `lifekit session start/end` for manual use.

## Done criterion

1. A full simulated session (open → 2 exercises with attempts → close with
   intention) persists correct rows + Markdown note; intentions transition
   pending→honored when the linked exercise completes.
2. Attempts outside `in_session` are rejected (tested).
3. pytest fixtures simulate the loop — no live LLM required.

## Non-goals

- Momentum scoring (Step 9), interviewer (Step 10), any UI.
