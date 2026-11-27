# Vision & Non-Negotiables

## The Vision

> Every day, LifeKit gives you one exercise to do and one idea to remember.

LifeKit sits on top of the books you care about, surfaces the right exercise or idea at the right time, and gives you a place to do the work and talk it through.

LifeKit is a personal-coach app — an accountability partner for turning what you read into what you do. It is **not** a learning platform. The distinction is deliberate:

- DeepTutor is a tutor that checks what you learned. LifeKit is a coach that checks what you did.
- LifeKit never quizzes, never shows grades, retention percentages, or mastery gates. Completion is self-declared.

## Non-Negotiables (binding)

| # | Non-negotiable | Rationale |
|---|---------------|-----------|
| N1 | **Deep book model, shallow user model.** All modeling investment goes into the book. User model = durable important facts only. | Psychological profiling would kill the product. |
| N2 | **Venue, not menu.** The app is where exercises are performed, not browsed. No dashboards, no browsing surfaces. | The opening: almost no book app is the venue. |
| N3 | **Deterministic runtime, generative surface.** Scheduling, surfacing, and state are code. The LLM owns conversational prose only. | Correctness, auditability, minimal-code. |
| N4 | **No quiz framing, ever.** No quizzes, visible grades, retention percentages, or mastery gates. Completion is self-declared. | LifeKit is a coach, not a tutor. |
| N5 | **Local-first, single user.** Localhost only. No auth, no cloud, no sync. | Simplicity, privacy, Step 0 lock. |
| N6 | **Minimal code.** Do not write a single line of code that isn't necessary. | The smallest diff that satisfies the spec. |
| N7 | **Plain English first.** Explain like a person, not a spec sheet. | The product is for humans. |
| N8 | **Never build:** deep user modeling beyond important facts, knowledge graphs, external-app dependencies, BKT/IRT/KST cognitive machinery, managed memory layers, notifications/nudges (until core loop proven), streak gamification beyond a plain count, social features, manual scheduling UI, Agent Skills export, reflective work placed in todo lists or calendars. | Explicit rejection list from the vision. |

## Stage Definitions

| Stage | Name | Status | Gate |
|-------|------|--------|------|
| 1 | Book pipeline (PDF to validated, quote-grounded exercises + key ideas in SQLite) | **Done** | Eval-gated per stage (split, extract, reduce/dedupe, validate) |
| 2 | Deterministic runtime (coach tools, multi-book registry, FSRS resurfacing) | **Done** | 49/49 tests green |
| 3 | Venue (Next.js feed + conversations web UI) | **Done 2026-09-24** | `lifekit ui` boots both services; 112/112 tests green |
| 4 | Dogfood & harden | **Current** | **Exit criterion undecided** |
| 5 | Program layer (coaching sessions, momentum, interviewer, invite-to-coach) | **Proposed** | Unlocked only after Stage 4 proves the loop |
| — | Notifications/nudges | **Deferred** | Until core loop is proven with real use |

## Stage 4 Exit Criterion (UNDEFINED — blocks Stage 5)

The single most important open decision. Without it, the program layer cannot be gated, and the transition from "works" to "proven" is undefined.

**Candidate dimensions for the exit criterion** (to be decided by Swapnil):

- **Usage:** N consecutive days of real use (e.g., 14 days)
- **Completion rate:** >= X% of surfaced exercises marked done
- **Signal quality:** User reports the surfaced items feel relevant (subjective)
- **Technical stability:** Zero data-loss incidents, zero pipeline re-runs needed
- **Coverage:** Second book ingested and surfaced alongside the first

**Recommendation:** Define this as a one-page `docs/product/DOGFOOD-EXIT.md` with 3-5 measurable criteria. This unblocks Stage 5.

## Stage 5 Build Order (proposed, not committed)

| Step | Feature | Depends on | Proposal |
|------|---------|-----------|----------|
| 8 | Coaching session model (durable sessions, events, if-then intentions, Markdown memory) | — | `openspec/changes/step-8-coaching-sessions/` |
| 9 | Momentum decay engine (deterministic score, motivation briefs, nudge policy) | Step 8 | `openspec/changes/step-9-momentum-decay/` |
| 10 | User interviewer (scripted elicitation to learner profile) | Step 8 | `openspec/changes/step-10-user-interviewer/` |
| 11 | Invite-to-coach UI (static-site export for external coach) | Steps 8, 9, 10 | `openspec/changes/step-11-invite-to-coach/` |

## Deliberately Undecided

Anything beyond Stage 5 (program layer). Not designed until Stage 4 dogfood exit is achieved.
