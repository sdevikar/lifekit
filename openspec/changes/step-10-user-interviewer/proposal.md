# Step 10: User interviewer — proposal

## Why

Coaching without knowing the learner's goal is generic. Step 10 adds
structured goal/context elicitation — the "what are you working toward,
what's in the way, what has worked before" conversation — stored as a
durable learner profile that biases exercise selection and feeds the
momentum engine's `value_recall` brief. tutor-mcp has only
`update_learner_profile` (no interview flow); the interview protocol itself
is LifeKit-novel.

## What Changes

- **Interview protocol** (scripted, not open-ended chat): 5–7 questions
  (goal, timeframe, obstacles, available time/energy, prior attempts,
  preferred exercise styles, book preferences). Each answer stored as
  structured profile fields, never free prose.
- **Schema**: `profiles` table + `profile_goals`:
  `goal_text, timeframe, obstacles_json, time_budget_min, energy_pattern,
  tried_before_json, preferred_styles_json, why_matters` — `why_matters`
  feeds Step 9's `value_recall` brief and `why_this_exercise`.
- **MCP tools**: `interview_start` (returns question 1 + protocol),
  `interview_answer(question_id, answer)` (validates, stores, returns next
  question). Idempotent and resumable — the LLM conducts, the server owns the
  schema. `link_book_to_goal(book_id, goal_id, relevance_note)` biases
  `next_coached_exercise` ordering (scalar boost, the simplified form of
  tutor-mcp's goal-relevance vector).
- **Reuse:** tutor-mcp's "server owns schema, LLM conducts" split; Pydantic
  for the profile schema (already a dependency). No new dependencies.

## Capabilities

### New Capabilities

- `user-interviewer`: scripted elicitation, learner profiles, book-goal linking.

## Impact

- New package `../../../lifekit/interview/`; `profiles`, `profile_goals` tables;
  `next_coached_exercise` gains a goal-relevance boost. Depends on Step 8
  sessions.

## Done criterion

1. A scripted interview through the MCP tools yields a complete, validated
   profile row — no free-text fields.
2. Resumability tested: answer → crash → resume returns the next unanswered
   question.
3. `why_matters` flows into a momentum brief's `value_recall` instruction
   (integration test with Step 9).

## Non-goals

- Open-ended profiling chat. The protocol is fixed.
- Where the interview is conducted (side chat vs CLI wizard) — open question
  in the coaching plan §6; this step builds the engine either way.
