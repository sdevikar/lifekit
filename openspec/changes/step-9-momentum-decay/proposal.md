# Step 9: Momentum decay engine — proposal

## Why

Consistency is the product. LifeKit logs completions but has no model of the
learner's momentum — so it can't tell a 30-day streak from a 3-week silence,
or choose what to say about either. Step 9 adds a deterministic, auditable
momentum model plus a motivation-brief engine, following tutor-mcp's
motivation-brief + alert-engine pattern: the server computes signals and
picks one angle by priority; it never sends pre-written text — it emits
signals + instructions for the host LLM to phrase.

## What Changes

- **Model** (`lifekit/momentum/`):
  - `momentum_state(exercise_id/book_id/global, momentum float 0..1, streak_days, last_completed_at, decay_rate)` — exponential decay `m = m_prev * e^(-λΔt)`; bumped by completions (+Δ per outcome grade), penalized by misses and ignored intentions.
  - **Momentum brief engine** — priority order, first match wins (adapted from tutor-mcp's `SelectBrief`):
    1. `milestone` — streak crossed 3/7/14/30 days
    2. `reactivation` — momentum < 0.2 after ≥7 days silence (non-blaming welcome-back)
    3. `plateau` — repeated `partial` outcomes on one exercise → suggest a different angle
    4. `consistency_reframe` — negative affect within 24 h → validate emotion, then reframe
    5. `value_recall` — tie the exercise to the goal from the user interviewer (Step 10)
    6. `open_loop` — an honored/missed intention is due today → resurface it
  - **Struggle-driven rescheduling** (from interview-forge): a `partial`/`skipped` outcome feeds FSRS a lower rating, pulling the next review sooner — automatic via the rating mapping, no special code path.
  - **Nudge policy**: nudges carry `why_now / momentum_signal / next_action`; delivery respects quiet hours + daily cap (stored in profile). No push infra — `get_due_nudges()` is polled by existing runtime cron (the book-sync cron pattern).
- **MCP tools**: `get_momentum(book_id?)`, `get_momentum_brief(exercise_id)`,
  `get_due_nudges()`, `update_nudge_policy(quiet_hours, daily_cap, enabled)`.
- **Reuse:** tutor-mcp's brief priority-selection logic and brief schema;
  decay math is ~30 lines (no library). Document the FSRS-over-practices
  rating mapping as a design note (no peer project does FSRS on real-world
  exercises — this is a genuine novelty).

## Capabilities

### New Capabilities

- `momentum-engine`: decay scores, briefs, policy-filtered nudges.

## Impact

- New package `lifekit/momentum/`; `momentum_state` table; depends on Step 8
  sessions + existing FSRS scheduler. No new dependencies.

## Done criterion

1. Simulated histories produce the correct brief-kind selection in priority
   order; decay math verified against hand-computed fixtures.
2. Reactivation briefs are non-blaming in instruction text (asserted in tests).
3. Nudges respect quiet hours + daily cap in tests.

## Non-goals

- Real-time push delivery (Discord/SMTP). Polled lists only.
- Canned motivational text — signals + instructions only.
