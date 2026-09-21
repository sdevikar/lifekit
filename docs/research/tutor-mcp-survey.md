# tutor-mcp Learning/Cognitive Subsystem Survey

**Repository:** `arnaudguiovanna/tutor-mcp`
**Commit surveyed:** `221b57e6a1927c8509051322fed531205d2b7ea9` (Merge PR #178, `staging`)
**Survey date:** 2026-09-21
**Method:** read-only source inspection. Every behavioral/default/threshold claim cites `file:line` relative to repo root.
**Language:** Go (`go.mod` module `tutor-mcp`). SQLite via `modernc.org/sqlite` (CGo-free) per CHANGELOG.

> Scope note: this survey covers the learning/cognitive/scheduling/memory/assessment/sequencing mechanisms only. OAuth/auth internals, admin API, Docker/deploy, webhooks, CLI plumbing, and certification are excluded except where they touch the learning mechanisms.

---

## 1. Cognitive algorithms inventory

The runtime ships **five** cognitive algorithms plus one removed calibration signal:

| # | Algorithm | Implementation | Status |
|---|-----------|----------------|--------|
| 1 | BKT (Bayesian Knowledge Tracing) | `algorithms/bkt.go`, `algorithms/individual_bkt.go`, `algorithms/bkt_info_gain.go` | Active |
| 2 | FSRS (spaced repetition) | `algorithms/fsrs.go` | Active — FSRS-5 |
| 3 | IRT (Item Response Theory, 2PL) | `algorithms/irt.go` | Active (online MAP update) |
| 4 | PFA (Performance Factor Analysis) | inline in `tools/interaction_apply.go` (+ migration in `db/migrations.go`) | Active — **not** in `algorithms/` |
| 5 | KST (Knowledge Space Theory) | `algorithms/kst.go` | Active — frontier/status computation |
| 6 | Rasch/Elo calibration signal | — | **REMOVED** — see §1.6 divergence |

There is **no separate sequencing algorithm** beyond the regulation pipeline (§3) + KST frontier + FSRS due-dates; see §1.7.

### 1.1 BKT — `algorithms/bkt.go` (114 lines)

State struct (`algorithms/bkt.go:9-15`): `BKTState{PMastery, PLearn, PForget, PSlip, PGuess float64}`.

Update split into observation + transition (deliberate; `algorithms/bkt.go:29-50`):

- `BKTObserve(state, correct)` — Bayesian posterior from the response alone:
  - correct: `pMasteryGivenObs = (1-PSlip)·PMastery / pCorrect`, where `pCorrect = (1-PSlip)·PMastery + PGuess·(1-PMastery)` (`algorithms/bkt.go:36-46`)
  - incorrect: `pMasteryGivenObs = PSlip·PMastery / pIncorrect`, where `pIncorrect = PSlip·PMastery + (1-PGuess)·(1-PMastery)` (`algorithms/bkt.go:47-57`)
  - Degenerate-denominator guard: `bktEpsilon = 1e-9` clamp (`algorithms/bkt.go:22`)
- `BKTTransition(state)` — `PMastery = PMastery·(1-PForget) + (1-PMastery)·PLearn`, clamped [0,1] (`algorithms/bkt.go:64-68`). **Note:** `PForget` is a per-transition probability, not elapsed-time forgetting (`algorithms/bkt.go:62-63`).
- `BKTUpdate = BKTTransition(BKTObserve(...))` (`algorithms/bkt.go:29-31`); "Measurement-only callers must use BKTObserve" — omitting the transition for assessment is the runtime's explicit measurement policy (`algorithms/bkt.go:36-38`).

**Project-specific heuristic** `BKTUpdateHeuristicSlipByErrorType` (`algorithms/bkt.go:86-118`) — explicitly flagged in-code as NOT canonical BKT:
- `SYNTAX_ERROR` (careless): `PSlip += 0.15`, clamped [0, 0.5]
- `KNOWLEDGE_GAP` (genuine gap): `PGuess -= 0.10`, clamped [0.05, 0.5]
- `LOGIC_ERROR`/empty: standard update.

Mastery predicate: `BKTIsMastered` ⇔ `PMastery >= MasteryBKT()` (`algorithms/bkt.go:120-122`).

### 1.2 Individualized BKT — `algorithms/individual_bkt.go` (226 lines)

`BKTUpdateIndividualized(state, profile, correct, errorType)` (`algorithms/individual_bkt.go:96-106`) adjusts P(Learn)/P(Slip)/P(Guess) from an `IndividualBKTProfile` before the standard update:

Profile fields (`algorithms/individual_bkt.go:58-67`): `Observations int`, `SuccessRate`, `ErrorRate`, `AvgConfidence`, `HintsRate`, `OverconfidenceRate`, `Stability`, `AvgResponseTimeSecs` (all float64, expected [0,1] except response time).

Hand-tuned delta coefficients (`algorithms/individual_bkt.go:23-55`): learn ±(0.04–0.07), slip ±(0.04–0.06), guess ±(0.02–0.06) per saturated signal — "deliberately gentle so individualization refines rather than overrides". Evidence weight ramps linearly `obs/20`, saturating at 20 observations (`individualBKTEvidenceRamp = 20`, `algorithms/individual_bkt.go:55`); overconfidence proxy saturates at avg-confidence 0.75 + 0.25 margin (`individualBKTConfidenceThreshold = 0.75`, `individualBKTOverconfidenceScale = 4`, `algorithms/individual_bkt.go:51-53`); slip/guess caps 0.5 (`algorithms/individual_bkt.go:9-11`).

### 1.3 BKT info gain — `algorithms/bkt_info_gain.go` (96 lines)

`BKTInfoGain(cs *models.ConceptState)` (`algorithms/bkt_info_gain.go:50-92`): expected entropy reduction (bits) of P(L) after the next response, `H(pL) − E[H(post)]`, peak near P(L)=0.5. Used by **[4] ConceptSelector in PhaseDiagnostic** (`algorithms/bkt_info_gain.go:48-49`). `BinaryEntropy` is also used by `engine/phase_fsm.go` for the mean-entropy DIAGNOSTIC criterion (`algorithms/bkt_info_gain.go:97-99`).

### 1.4 FSRS — `algorithms/fsrs.go` (283 lines) — FSRS-5

Version constant `FSRSVersion = "FSRS-5"`, matching `open-spaced-repetition` spec and go-fsrs v3.3.1 parameters (`algorithms/fsrs.go:28-36`).

Key constants (`algorithms/fsrs.go:37-46`):
- `FSRSDesiredRetention = 0.9`
- `fsrsDecay = -0.5`, `fsrsFactor = 19.0/81.0` (forgetting curve `R(t,S) = (1 + FACTOR·t/S)^DECAY`, `Retrievability`, `algorithms/fsrs.go:76-91`)
- `fsrsMaximumInterval = 36500` days (100-year ceiling)
- 19 default weights `defaultWeights` (`algorithms/fsrs.go:48-53`): `0.40255, 1.18385, 3.173, 15.69105, 7.1949, 0.5345, 1.4604, 0.0046, 1.54575, 0.1192, 1.01925, 1.9395, 0.11, 0.29605, 2.2698, 0.2315, 2.9898, 0.51655, 0.6621`

Card struct `FSRSCard` (`algorithms/fsrs.go:55-64`): `Stability, Difficulty float64; ElapsedDays, ScheduledDays, Reps, Lapses int; State CardState; LastReview time.Time`. States: `new/learning/review/relearning` (`algorithms/fsrs.go:21-26`); ratings `Again=1..Easy=4` (`algorithms/fsrs.go:13-18`).

`ReviewCard(card, rating, now)` (`algorithms/fsrs.go:227-282`):
- New card: `Stability = InitialStability(rating)` (weight[rating-1]), `Difficulty = InitialDifficulty(rating)` (`w[4] − e^(w[5]·(rating−1)) + 1`, clamped [1,10]); `Again` → `learning` state, interval 0; else → `review` with `NextInterval(S, 0.9)`.
- Recall: `nextRecallStability` (`algorithms/fsrs.go:160-171`); lapse (`Again`): `nextForgetStability` capped at `S/e^(w[17]·w[18])` so a relearning `Good` can't exceed pre-lapse S (`algorithms/fsrs.go:262-265`); same-day re-review (<24h): `nextShortTermStability` (`algorithms/fsrs.go:175-180`).
- Scheduling adapter keeps **whole-day intervals** and immediate relearning after Again; does **not** implement Anki's minute learning steps (`algorithms/fsrs.go:33-35`).
- `NextInterval(S, R) = S·((R^(1/DECAY) − 1)/FACTOR)`, min 1 day (`algorithms/fsrs.go:206-220`).

### 1.5 IRT — `algorithms/irt.go` (108 lines) — online 2PL MAP update

`IRTProbability(θ, b, a) = 1/(1+e^(−a(θ−b)))` (`algorithms/irt.go:25-27`).

`IRTUpdateThetaCumulative(theta, priorObservations, items, responses)` (`algorithms/irt.go:40-94`): regularized online update — Newton-Raphson (≤8 iterations, `irtMaxNewtonStep = 1.0`, `algorithms/irt.go:21`) maximizing new-item likelihood under Gaussian prior N(θ, 1/precision), `priorPrecision = 1.0 + 0.25·priorObservations` (`irtBasePriorPrecision = 1.0`, `irtInformationPerObservation = 0.25`, `algorithms/irt.go:13-20`). θ clamped to [−4, 4]. "Runtime-generated tasks no longer use this update because their item parameters have not been calibrated" (`algorithms/irt.go:18-19`).

`IRTIsInZPD(pCorrect)`: legacy band **[0.55, 0.80]**, explicitly "not an empirically established zone of proximal development" (`algorithms/irt.go:99-102`).

`FSRSDifficultyToIRT`: **deprecated** — "must not feed a live learner model or pedagogical decision; remains only for compatibility with old replays" (`algorithms/irt.go:104-108`).

### 1.6 PFA — inline in `tools/interaction_apply.go` (NOT in `algorithms/`)

PFA appears in only three non-test sources: `tools/interaction_apply.go`, `db/migrations.go`, `db/migrations_test.go` (grep §0). **Divergence from release notes:** the CHANGELOG/v0.3.0-alpha.1 blurb lists "PFA (plateau detection)" among "five complementary cognitive algorithms ... in `algorithms/`-style packaging", but PFA has no file in `algorithms/` — it is implemented inline at the interaction-application site. (Details in §2.3 after reading `tools/interaction_apply.go`.)

### 1.7 KST — `algorithms/kst.go` (50 lines)

`KSTGraph{Concepts []string, Prerequisites map[string][]string}` (`algorithms/kst.go:9-12`).
- `ComputeFrontier(graph, mastery)` (`algorithms/kst.go:14-30`): concepts below `MasteryKST()` whose prereqs all meet `MasteryKST()` → the learnable frontier.
- `ConceptStatus(graph, mastery, concept)` (`algorithms/kst.go:32-44`): `done` / `locked` / `current`.

### 1.8 Rasch/Elo calibration signal — REMOVED (docs-vs-code divergence #1)

Release notes v0.3.0-alpha.1 claim "a separate Rasch/Elo calibration signal for learner ability vs. exercise difficulty" as shipped. The code disagrees:
- `CHANGELOG.md:164`: "MAP estimate and **remove the unused Rasch/Elo path**."
- `tools/interaction_test.go:551-552,569-571`: test asserts the `rasch_elo` signal is non-persistent and **must not be exposed** in observations or snapshots.
- Grep for `rasch`/`elo` (case-insensitive) across all `.go`/`.md`/`.sql` returns only `CHANGELOG.md` and `tools/interaction_test.go` — no implementation remains.

**Divergence:** release notes advertise Rasch/Elo as a live pillar; the shipped code removed it.

### 1.9 Mastery thresholds — `algorithms/thresholds.go` (90 lines)

Bascule `REGULATION_THRESHOLD` env (`algorithms/thresholds.go:70-88`): default **unified** profile `BKT=KST=Mid=0.85`; legacy (`REGULATION_THRESHOLD=off`) gives `BKT=0.85, KST=0.70, Mid=0.80` (`algorithms/thresholds.go:12-15`). `MasteryBKT()` always 0.85 (`algorithms/thresholds.go:37-44`).

FSRS retrievability bands (`algorithms/thresholds.go:23-35`): FORGETTING warning `< 0.40` (`RetentionAlertWarningThreshold`), critical `< 0.30` (`RetentionAlertCriticalThreshold`), recall-routing `< 0.50` (`RetentionRecallRoutingThreshold`).

## 2. Learner model — state schema, persistence, snapshot pattern

### 2.1 Per-learner/concept state schema — `models/learner.go:29-52`

One `ConceptState` row per (learner, domain, concept) — concept labels are unique only *inside* a domain (`models/learner.go:56-61`). Fields:

| Field | Type | Role |
|---|---|---|
| ID / TenantID / EnrollmentID / FormationConceptID / LearnerID / DomainID / Concept | int64/string | identity & scoping |
| Stability, Difficulty | float64 | FSRS memory parameters |
| ElapsedDays, ScheduledDays, Reps, Lapses | int | FSRS scheduling counters |
| CardState | string | `new`/`learning`/`review`/`relearning` |
| LastReview, NextReview | *time.Time | FSRS schedule |
| PMastery, PLearn, PForget, PSlip, PGuess | float64 | BKT parameters |
| Theta | float64 | **legacy IRT estimate — preserved, never updated** (see §2.3) |
| UpdatedAt | time.Time | bookkeeping |

Bootstrap defaults — `NewConceptStateInDomain` (`models/learner.go:63-77`): `Stability=1.0, Difficulty=0.3, CardState="new", PMastery=0.1, PLearn=0.15, PForget=0.05, PSlip=0.1, PGuess=0.2, Theta=0.0`. (Note: default `Difficulty=0.3` is below FSRS's [1,10] range; `fsrsDifficulty` clamps finite values into [1,10] — `algorithms/fsrs.go:183-188`.)

Interaction rows — `models/learner.go:79-113` (`Interaction`): learner/session/concept/activity, success, response time, confidence, error type, hints, misconception fields (failures only), `BKTSlip`/`BKTGuess` *float64 pointers recording the exact slip/guess fed into the BKT update for deterministic replay (`models/learner.go:97-106`), rubric JSON, timestamps.

### 2.2 The update chain & call hierarchy

**Entry point:** `applyInteraction` (`tools/interaction_apply.go:69-351`) — "persists the interaction and updates the learner's cognitive state (BKT, FSRS) for the concept". Called by the `record_interaction` MCP tool path (`tools/interaction.go`) and assessment flows. Non-cognitive activity types are rejected up front (`isCognitiveEvidenceActivity`, `tools/interaction_apply.go:353+`).

**The snapshot pattern** (`tools/interaction_apply.go:168-191`): before any update, all prior fields are copied into `prior*` locals — "All downstream algorithm steps read from this snapshot, never from `cs` directly, to keep the BKT and FSRS updates commutative. See doc comment above and issue #53." One merged write-back at the end (`tools/interaction_apply.go:288-330`), inside a serializable transaction (`deps.Store.WithTx` → `BEGIN IMMEDIATE` on SQLite, `tools/interaction_apply.go:90-97`).

**Per-interaction chain** (all inside the tx):
1. **BKT** (`tools/interaction_apply.go:193-220`): profile built from last 20 interactions (`buildIndividualBKTProfile`, `GetRecentInteractionsInDomain(..., 20)`); mode from `engine.BKTUpdateModeForActivity` (`engine/bkt_policy.go:11-20`): **learning opportunity** (full update incl. transition) for `new_concept, practice, recall, debugging_case, debug_misconception, feynman_prompt`; **observation-only** (no transition) for `diagnostic_assessment, mastery_challenge, transfer_probe` and everything else.
2. **Interaction row persisted** with effective slip/guess (`tools/interaction_apply.go:222-276`); `IsProactiveReview` flag if `NextReview` was in the future (`tools/interaction_apply.go:250-252`).
3. **FSRS** (`tools/interaction_apply.go:259-280`): rating mapped from outcome — `Again` on failure; on success `Easy` if confidence ≥ 0.9, `Hard` if confidence < 0.5, else `Good` (`tools/interaction_apply.go:260-266`). Update applied only if `priorLastReview` is zero, the observation is newer, or legacy protocol (`tools/interaction_apply.go:278`).
4. **IRT: skipped** — `newTheta = priorTheta`; "Preserve the legacy estimate. Updating it from FSRS would treat a learner/concept memory parameter as the difficulty of this task. Resume IRT only with an explicit, independently calibrated item model." (`tools/interaction_apply.go:282-286`).
5. **PFA: excluded** — "PFA is not part of the learner-model update or alert policy." (`tools/interaction_apply.go:63-68`).
6. **Pedagogical snapshot** persisted per interaction: before/observation/after/decision JSON (`tools/interaction_apply.go:310-328`) — full decision trace for replay.

### 2.3 Divergences: IRT and PFA do not update the learner model

Release notes claim "BKT × IRT × PFA, snapshot pattern keeps the update chain order-invariant" with all five algorithms "updating the learner model on every interaction". The code:

- **IRT**: theta is read from the snapshot and written back unchanged (`tools/interaction_apply.go:285`). The `IRTUpdateThetaCumulative` function exists (`algorithms/irt.go:40`) but is not called on the live path — "Runtime-generated tasks no longer use this update because their item parameters have not been calibrated" (`algorithms/irt.go:18-19`).
- **PFA**: `pfa_successes`/`pfa_failures` columns were **dropped** from `concept_states` by migration (`db/migrations.go:131-137`: "Issue #55: PFA persisted state was written but never consumed — engine/alert.go recomputes PFA in-memory from the interactions"). The plateau alert that consumed it is retired: "Historical PLATEAU alerts remain readable, but the runtime no longer infers stalled learning from saturation of a cumulative probability." (`engine/alert.go:142-143`).

**Net:** on the live path only **BKT and FSRS** mutate learner state per interaction. IRT is legacy-preserved, PFA is effectively retired, Rasch/Elo is removed (§1.8).

### 2.4 Storage location

SQLite via `modernc.org/sqlite`; `concept_states`, `interactions`, `pedagogical_snapshots` tables (schema §10). Postgres variant exists (`db/schema_pg.sql`, `db/postgres.go`) for SaaS deployments.

## 3. The 7-stage regulation pipeline

Canonical numbering comes from `docs/regulation-design/` (00–07); implementation order was 7→1→5→4→3→2→6 (`docs/regulation-design/01-goal-decomposer.md` §"Pourquoi ce composant en deuxième"). **Runtime execution order** in `engine.OrchestrateWithPhase` (`engine/orchestrator.go:107-221`) is:

1. Phase read (NULL → INSTRUCTION fallback, `engine/orchestrator.go:115-121`)
2. Fixtures fetch (states, misconceptions, recent, alerts — `engine/orchestrator.go:250`)
3. **[2] PhaseController** — `EvaluatePhase` FSM (`engine/orchestrator.go:137-159`; §4)
4. **[3] GateController** — `ApplyGate` (`engine/orchestrator.go:431-449`)
5. **[4] ConceptSelector** — `SelectConceptAt` on the gate's allowed pool (`engine/orchestrator.go:462-480`)
6. **[5] ActionSelector** — `SelectActionForPhaseAt` (`engine/orchestrator.go:483-486`, via `selectActionForSelection` `engine/orchestrator.go:580-612`)
7. Post-decision **[6] FadeController** — runs strictly *after* `engine.Orchestrate`, in `tools/activity.go`, only when `REGULATION_FADE=on` (default OFF) (`engine/fade_controller.go:22-25`; `tools/prompt.go:42`)

with **[7] ThresholdResolver** as a non-runtime accessor API (`algorithms/thresholds.go`) and **[1] GoalDecomposer** as an upstream LLM-written signal (see below).

### [7] ThresholdResolver — `algorithms/thresholds.go`
Not a decision stage: three exported accessors (`MasteryBKT`, `MasteryKST`, `MasteryMid`) plus the `REGULATION_THRESHOLD` bascule (default unified 0.85/0.85/0.85; `=off` → legacy 0.85/0.70/0.80). Also owns the FSRS retrievability bands 0.40/0.30/0.50 (§1.9). (Design doc `docs/regulation-design/07-threshold-resolver.md` describes legacy-as-default — stale; code promoted unified to default per `algorithms/thresholds.go:28-33`. Non-normative archive per `docs/regulation-design/README.md`.)

### [1] GoalDecomposer — goal_relevance vector
The runtime does **not** generate the vector. It is: a versioned JSON column on `domains`; written by the LLM via the `set_goal_relevance` MCP tool after reading `personal_goal`; read at runtime via `Domain.ParseGoalRelevance()` with uniform fallback when absent/stale (`docs/regulation-design/01-goal-decomposer.md` §1). Consumed by [4] ConceptSelector and the phase transition (`GoalRelevantCutoff=0.0`, `engine/phase_config.go:88-96`). `init_domain`/`add_concepts` instruct the LLM to call `set_goal_relevance` asynchronously.

### [2] PhaseController — `engine/phase_fsm.go` + `engine/phase_config.go`
See §4.

### [3] GateController — `engine/gate.go:ApplyGate`
Runs before concept/action selection (`engine/gate.go:8-13`): filters the candidate pool, restricts allowed actions per concept (e.g. misconception lock), and can short-circuit with an escape action (OVERLOAD → close session). `DefaultAntiRepeatWindow = 3` (`engine/gate.go:59`): the N most-recent concepts are excluded. Unknown phase → explicit error, no silent fallback (`engine/gate.go:26-28`).

Two bypasses run between gate and concept selection (`engine/orchestrator.go:450-468`): **critical-forgetting bypass** (FORGETTING at critical urgency jumps straight to review of the lowest-retention concept) and **recall-need selection** (goal-relevant concept with retrievability < `RetentionRecallThreshold` = 0.50).

### [4] ConceptSelector — `engine/concept_selector.go:SelectConcept`
Dispatches on phase (`engine/concept_selector.go:51-57`): DIAGNOSTIC maximizes `BKTInfoGain` (§1.3); INSTRUCTION works the KST frontier (`algorithms.ComputeFrontier`, §1.7); MAINTENANCE serves due/recall concepts. Returns `Selection{Concept, Score, NoFringe, Rationale}`; `NoFringe` is a *signal* (not error) that can trigger a one-shot phase fallback (`engine/orchestrator.go:162-193`; `noFringeFallbackPhase`, `engine/orchestrator.go:399`).

### [5] ActionSelector — `engine/action_selector.go:SelectActionForPhaseAt`
Given the chosen concept + state (+ active misconception, capped action history of 50), picks the activity type. Misconception takes priority; gate `ActionRestriction` can override the pick (`engine/orchestrator.go:492-499`). `REGULATION_CONCEPT`/`REGULATION_GATE` env flags only toggle system-prompt documentation appendices — the stages run regardless (`engine/concept_selector.go:22-24`; `engine/gate.go:16-18`).

### [6] FadeController — `engine/fade_controller.go`
Pure function `Decide(autonomy_score, AutonomyTrend) → FadeParams{HintLevel, WebhookFrequency, ZPDAggressiveness, ProactiveReviewEnabled}` (`engine/fade_controller.go:119`; struct `engine/fade_controller.go:70-80`). Opt-in: `REGULATION_FADE=on`, default OFF (`engine/fade_controller.go:25`; `tools/prompt.go:42`). "The system makes itself progressively unnecessary": hint verbosity, Discord nudge cadence, ZPD aggressiveness, proactive FSRS review scheduling.

## 4. Phase FSM — `engine/phase_fsm.go:EvaluatePhase`

Pure function over `PhaseObservables` (`engine/phase_fsm.go:14-57`). Transitions (`engine/phase_fsm.go:75-82`):

| Transition | Condition |
|---|---|
| DIAGNOSTIC → INSTRUCTION | qualified distinct-concept coverage reaches `min(domain concepts, NDiagnosticMax)`; entropy reduction ≥ `DeltaHThreshold` is an additional sufficient-but-not-necessary criterion (coverage is mandatory) |
| INSTRUCTION → MAINTENANCE | all goal-relevant concepts have estimated PMastery above the routing threshold (`EstimatedGoalRelevant == TotalGoalRelevant > 0`) |
| MAINTENANCE → INSTRUCTION | at least one goal-relevant estimate below the acquisition routing threshold (forgetting alone does **not** flip phase — handled by recall selection) |

Defaults — `NewDefaultPhaseConfig` (`engine/phase_config.go:80-96`): `DeltaHThreshold=0.2` bits ("initial guess; revisit with E2E artifact data"), `NDiagnosticMax=8`, `RetentionRecallThreshold=0.50`, `GoalRelevantCutoff=0.0`, `AntiRepeatWindow=3`.

DIAGNOSTIC entry snapshots mean BKT entropy (`MeanBinaryEntropyOverGraph`, `engine/phase_fsm.go:177-204`); exit compares reduction vs entry. NULL stored phase → INSTRUCTION fallback (`engine/orchestrator.go:117-121`). `ReviewOnly` requests pin MAINTENANCE without advancing the FSM (`engine/orchestrator.go:140-142`). Persisted via `CompareAndSwapDomainPhase` (`engine/orchestrator.go:123-135`).

## 5. Motivation engine, metacognitive loop, alert engine

### 5.1 Motivation engine — `engine/motivation.go`

`MotivationEngine.Build` composes a `MotivationBrief` (instruction for the LLM, not learner-facing text) from `BriefInput` signals (`engine/motivation.go:86-107, 368-377`): domain, concept state, last failure (24h), latest affect, sessions-on-concept, self-initiated ratio, exercise count, plateau flag.

`SelectBrief` priority, first match wins (`engine/motivation.go:179-216`):
1. **milestone** — PMastery within ±0.02 of {0.85, 0.7, 0.5} (`crossedMilestone`, `engine/motivation.go:124-136`)
2. **competence_value** — first exercise of a session on a new concept, every 5th session on a concept, or milestone just crossed (`engine/motivation.go:138-154`)
3. **growth_mindset** — a failure on this concept within 24h
4. **affect_reframe** — latest affect negative within 24h (satisfaction ≤2, perceived_difficulty == 4, or energy ≤1; `affectIsNegative`, `engine/motivation.go:218-240`)
5. **plateau_recontext** — PLATEAU alert active (legacy path; plateau inference retired, §2.3)
6. **why_this_exercise** — utility-value fallback tied to `personal_goal` on new concepts / session start

Utility-value framing rotates over four axes — Financial, Employment, Intellectual, Innovation (`models.ValueAxes`; `nextValueAxis`, `engine/motivation.go:156-177`), preferring LLM-authored `DomainValueFramings` statements. Interest phase follows Hidi & Renninger (2006) four-phase model (`InferInterestPhase`, `engine/motivation.go:101-122`); the 0.85 individual-interest bound deliberately bypasses `MasteryBKT()` (`engine/motivation.go:103-108`).

### 5.2 Metacognitive loop — `engine/metacognition.go`

**Autonomy metrics** — `ComputeAutonomyMetrics` (`engine/metacognition.go:35-168`): four *descriptive* components, explicitly "not a validated autonomy scale" and must not determine pedagogical support (`engine/metacognition.go:30-34`):
1. initiative rate (% self-initiated sessions; 2h session gap default),
2. calibration accuracy (1 − mean |prediction error|),
3. hint independence (% hint-free responses on concepts with PMastery ≥ MasteryMid()),
4. proactive review rate (% of recall interactions flagged proactive).
Score = mean over *observed* components only; `ScoreStatus` ∈ {unavailable, partial, descriptive}.

**Mirror** — `DetectMirrorPattern` (`engine/metacognition.go:273-364`): descriptive observations for a generative dialogue after ≥3 sessions; `Confidence: "descriptive_only"` — "does not diagnose dependency, assume why a session started, or author the learner-facing message" (`engine/metacognition.go:273-276`). Dispatched by the `mirror` cron job; dedup'd at the alert layer (`MIRROR_MESSAGE`).

**Calibration** — shared policy `calibrationBiasIsActionable` (`engine/calibration_policy.go:16-18`): actionable iff ≥5 samples and |bias| ≥ 0.25. Feeds `CALIBRATION_DIVERGING` alerts, OLM, and mirror.

**OLM (Open Learner Model)** — `engine/olm.go:BuildOLMSnapshot`: mastery buckets per concept via `NodeClassify` (`engine/olm.go:56-75`): `new` → not_started; retrievability < 0.50 or PMastery < 0.30 → fragile; PMastery ≥ MasteryKST() → estimated; else in_progress. Focus concept = highest-priority alert (FORGETTING-critical > ZPD_DRIFT > PLATEAU; `engine/olm.go:353-385`). Served by `get_olm_snapshot` and the daily OLM webhook.

### 5.3 Alert engine — `engine/alert.go`

`ComputeAlertsWithEvidenceAt` (`engine/alert.go:38-148`) — pure, clock-injected:
- **FORGETTING** — `CurrentRetrievability < 0.40` (warning), `< 0.30` (critical); critical suppresses same-concept MASTERY_READY/ZPD_DRIFT (`engine/alert.go:54-76`).
- **MASTERY_READY** — `AssessMasteryStatus` + evidence quality + uncertainty + transfer profile (`engine/alert.go:150-167`); high BKT alone insufficient.
- **ZPD_DRIFT** — 3+ consecutive failures on one concept, with error-type-specific recommendations (KNOWLEDGE_GAP/LOGIC_ERROR/SYNTAX_ERROR × 3; `engine/alert.go:109-137`). (IRT-based ZPD deliberately not used: "Generated items have no calibrated IRT difficulty" — `engine/alert.go:139-141`.)
- **OVERLOAD** — session > 45 min (`engine/alert.go:145-148`).
- **PLATEAU** — retired: "the runtime no longer infers stalled learning from saturation of a cumulative probability" (`engine/alert.go:142-143`); historical alerts still readable.

Metacognitive alerts — `ComputeMetacognitiveAlerts` (`engine/alert.go:206-306`): **CALIBRATION_DIVERGING** (shared ≥5-sample/0.25 policy), **AFFECT_NEGATIVE** (satisfaction ≤2 or perceived_difficulty == 1 on 2 consecutive sessions), **TRANSFER_BLOCKED** (PMastery ≥ 0.85 but transfer score < 0.50 in 2+ contexts → "feynman challenge recommande"). Legacy autonomy composite "no longer produces a pedagogical alert" (`engine/alert.go:216-218`).

### 5.4 Mastery adjudication & assessment scoring

**Mastery verdict** — `AssessMasteryStatus` (`engine/mastery_status.go:68-130`): staged, conservative. Stages: not_started → developing → estimated (PMastery ≥ MasteryBKT()) → retained → demonstrated → transferred. `Retained` requires an observed successful retrieval after a ≥24h delay (`minimumDelayedRecallGap = 24h`, `engine/mastery_status.go:16`) with retrievability ≥ 0.50; `Demonstrated` requires a trusted *passed* assessment whose task+rubric were frozen before the response; `Transferred` additionally requires broad transfer records linked to trusted transfer assessments (`engine/mastery_status.go:60-67`). "Model probability and host-authored observations alone can never create those claims."

**Mastery-challenge eligibility** — `ReadyForMasteryChallenge` (`engine/mastery_status.go:380-385`): `Estimated && Retained && evidence.Quality != Weak && Confidence != Low && TransferReadiness != Blocked`. Uncertainty from `ComputeMasteryUncertainty` (`engine/uncertainty.go:62`): evidence staleness, diversity, error rate, near-threshold margin.

**Transfer profile** — `BuildTrustedTransferProfile` (`engine/transfer_model.go:229-238`): readiness labels from transfer records linked to trusted assessments only.

**Assessment scoring** — `assessment.Evaluate` (`assessment/score.go:38`): "requires all and only frozen criterion IDs, each exactly once"; arithmetic in exact rationals (`big.Rat`, `assessment/score.go:175`); evidence is required prose, "not a semantic entailment check of the response" (`assessment/score.go:35-37`).

**Affect** — `record_affect` (`tools/affect.go`): end-of-session satisfaction / perceived difficulty / energy; feeds AFFECT_NEGATIVE alerts and motivation reframing.

## 6. Scheduled jobs — `engine/scheduler.go:Start` (`engine/scheduler.go:831-907`)

robfig/cron/v3 with panic recovery and SkipIfStillRunning (`engine/scheduler.go:136-140`); distributed lease support. Release notes claim 6 cron jobs; the code registers **8** (+ SaaS-only jobs):

| Job | Schedule (UTC) | Function | Purpose |
|---|---|---|---|
| `olm` | `0 13 * * *` daily | `sendOLM` | daily Open Learner Model webhook (`engine/scheduler.go:844-846, 1695-1702`) |
| `consolidation` | `30 13 * * *` daily | `runConsolidationCycle` | memory consolidation prep (`memory/consolidator.go:PrepareJobs`) |
| `requeue_stale` | `*/5 * * * *` | `requeueStaleConsolidations` | requeue timed-out consolidation jobs |
| `motivation` | `0 8 * * *` daily | `sendDailyMotivation` | dispatch queued daily motivation webhooks |
| `recap` | `0 21 * * *` daily | `sendDailyRecap` | end-of-day recap webhooks |
| `mirror` | `0 12 * * *` daily | `sendMirrorMessages` | metacognitive mirror nudges (dedup'd per learner/day) |
| `cleanup` | `0 * * * *` hourly | `cleanupExpiredData` | expire old data |
| `metacog_alerts` | `*/30 * * * *` | `dispatchMetacognitiveAlerts` | metacognitive alerts; each kind fires ≤ once per learner per UTC day (`WasAlertSentToday`) |

**Divergence:** release notes list 6; code has 8 — `consolidation` + `requeue_stale` are unmentioned. (SaaS outbox/async/entitlement jobs also exist but are out of scope.)

## 7. MCP tool inventory — 46 tools, not 28

`tools/tools_register_test.go:221-222` asserts 46 registered tools. **Divergence:** release notes claim 28.

| # | Tool | One-line purpose | Implementation |
|---|---|---|---|
| 1 | start_learning_session | open a durable learning session | `tools/session.go` |
| 2 | get_pending_alerts | read computed alerts | `tools/alerts.go` |
| 3 | get_next_activity | run regulation pipeline → next activity | `tools/activity.go` |
| 4 | record_interaction | log graded response; drives BKT/FSRS chain | `tools/interaction.go` + `tools/interaction_apply.go` |
| 5 | record_learning_event | record instruction/feedback exposure; does NOT advance BKT/FSRS | `tools/learning_event.go` |
| 6 | prepare_assessment_attempt | create frozen assessment attempt | `tools/assessment.go` |
| 7 | submit_assessment_attempt | submit attempt for evaluation | `tools/assessment.go` |
| 8 | cancel_assessment_attempt | cancel pending attempt | `tools/assessment.go` |
| 9 | check_mastery | mastery verdict for a concept | `tools/mastery.go` |
| 10 | get_learner_context | learner profile/context summary | `tools/context.go` |
| 11 | get_availability_model | read notification availability windows | `tools/availability.go` |
| 12 | update_availability_model | set availability windows | `tools/availability.go` |
| 13 | get_olm_snapshot | open learner model snapshot | `tools/olm.go` |
| 14 | get_pedagogical_snapshots | decision-trace snapshots (before/observation/after) | `tools/pedagogical_snapshots.go` |
| 15 | get_decision_replay_summary | replay summary for audit | `tools/decision_replay.go` |
| 16 | init_domain | create domain: concept/prerequisite graph | `tools/domain.go` |
| 17 | add_concepts | extend domain graph | `tools/domain.go` |
| 18 | get_curriculum_snapshot | read immutable curriculum revision | `tools/curriculum.go` |
| 19 | publish_curriculum_revision | publish new curriculum revision (optimistic concurrency) | `tools/curriculum.go` |
| 20 | validate_domain_graph | graph quality validation | `tools/domain_graph_quality.go` |
| 21 | update_learner_profile | update profile fields | `tools/profile.go` |
| 22 | record_affect | record end-of-session affect | `tools/affect.go` |
| 23 | calibration_check | start a calibration prediction | `tools/calibration.go` |
| 24 | record_calibration_result | record prediction outcome | `tools/calibration.go` |
| 25 | get_autonomy_metrics | autonomy metrics | `tools/autonomy.go` |
| 26 | get_metacognitive_mirror | metacognitive mirror message | `tools/mirror.go` |
| 27 | feynman_challenge | teach-back challenge | `tools/feynman.go` |
| 28 | transfer_challenge | transfer probe challenge | `tools/transfer.go` |
| 29 | record_transfer_result | record transfer probe outcome | `tools/transfer.go` |
| 30 | learning_negotiation | negotiate learning plan with prereq sanity | `tools/negotiation.go` |
| 31 | set_domain_priority | set domain priority rank | `tools/domain_priority.go` |
| 32 | mark_domain_high_stakes | flag conservative evidence policy (one-way) | `tools/domain_safety.go` |
| 33 | update_learner_memory | update narrative memory | `tools/learner_memory.go` |
| 34 | read_raw_session | read raw session transcript | `tools/learner_memory.go` |
| 35 | get_memory_state | read consolidated memory state | `tools/learner_memory.go` |
| 36 | archive_domain | archive a domain | `tools/manage_domain.go` |
| 37 | unarchive_domain | unarchive a domain | `tools/manage_domain.go` |
| 38 | delete_domain | logical delete (tombstone) | `tools/manage_domain.go` |
| 39 | get_misconceptions | active misconceptions | `tools/misconceptions.go` |
| 40 | record_session_close | close session with intention | `tools/session_close.go` |
| 41 | list_implementation_intentions | list implementation intentions | `tools/session.go` |
| 42 | update_implementation_intention | update an intention | `tools/session.go` |
| 43 | queue_webhook_message | queue a Discord nudge | `tools/queue_webhook.go` |
| 44 | get_dashboard_state | cockpit aggregations | `tools/get_dashboard_state.go` |
| 45 | set_goal_relevance | LLM writes goal_relevance vector | `tools/activity.go` |
| 46 | get_goal_relevance | read goal_relevance (+ staleness) | `tools/goal_relevance.go` |

Tool-name → file mapping verified by grep over `tools/*.go` (registration sites).

## 8. Concept/domain graph

- **Model:** `models.KnowledgeSpace{Concepts []string, Prerequisites map[string][]string}` (`models/domain.go:162-165`); persisted as `domains.graph_json` (`db/schema.sql:19-33`).
- **init_domain** (`tools/domain.go:246+`): validates name/personal_goal/concepts, then `validateConcepts` (`tools/domain.go:43-99`): ≤500 concepts/call, names ≤200 chars (`tools/domain.go:27-29`), no duplicates, every prerequisite key/value must reference a declared concept, ≤20 prereqs/node.
- **Cycle detection:** `findPrereqCycle` — iterative DFS with white/gray/black coloring (`tools/domain.go:101-187`); cycles rejected up front because "every node in the cycle is `locked`... and learners can never make progress" (issue #62; `tools/domain.go:90-97`).
- **Graph quality gate:** `engine.EvaluateGraphQuality` blocks `init_domain` on critical issues (`tools/domain.go:293-297`; `engine/graph_quality.go:70`).
- **KST consumption:** `algorithms.ComputeFrontier` / `ConceptStatus` (§1.7) drive INSTRUCTION-phase concept selection and prerequisite gating; gate filters prereqs to the allowed pool (`engine/orchestrator.go:614-626`).
- **Curriculum revisions:** `publish_curriculum_revision` — immutable snapshots with optimistic concurrency; definition changes reset estimates and invalidate old evidence for routing (`tools/curriculum.go:129-133`).

## 9. Content ingress path

There is **no content-ingestion pipeline** (no RAG, no document import feeding the cognitive loop). Content enters in two LLM-mediated ways:
1. **Domain graph authoring** — the driving LLM calls `init_domain`/`add_concepts` with concept names + prerequisites it devised; the runtime validates structure (DAG, caps, quality gate) but never sees lesson content.
2. **Curriculum snapshots** — `publish_curriculum_revision` stores concept outcomes/criteria/provenance as immutable revisions (`tools/curriculum.go:66-69`); `ValidateCurriculumFindings` (`assessment/curriculum.go:16`) parses LLM-produced findings.

The runtime's "content" is the graph + thresholds + goal_relevance + value framings — all authoring stays with the LLM ("LLM = content engine" guardrail, `docs/regulation-design/01-goal-decomposer.md` §1). Assessment rubrics/evidence arrive via `prepare/submit_assessment_attempt` with evaluator provenance (`tools/interaction_apply.go:17-50`).

## 10. Persistence

- **Engine:** SQLite via `modernc.org/sqlite` (CGo-free); Postgres variant (`db/schema_pg.sql`, `db/postgres.go`) for SaaS.
- **Learning-relevant tables** (`db/schema.sql`): `domains` (graph_json, goal_relevance_json, phase, phase_changed_at, phase_entry_entropy — phase columns added by migration, `db/migrations.go:104-106`), `concept_states` (BKT params p_mastery/p_learn/p_forget/p_slip/p_guess, FSRS stability/difficulty/elapsed/scheduled/reps/lapses/card_state/last_review/next_review, legacy theta), `interactions` (incl. bkt_slip/bkt_guess replay columns, domain_id, misconception fields), `pedagogical_snapshots` (via `db/evidence_snapshot.go`; before/observation/after/decision JSON per interaction), `affect_states`, `calibration_records`, `transfer_records`, `scheduled_alerts`, `webhook_message_queue`.
- **Migrations:** versioned, idempotent CREATE/ALTER pipeline with **SHA-256 checksum drift detection** (`db/migrations_checksum.go:30-35`); learning-relevant migrations: phase columns (`db/migrations.go:104-106`), `interactions.domain_id` (`db/migrations.go:116`), `bkt_slip/bkt_guess` (`db/migrations.go:129`), **PFA column drop** (`db/migrations.go:131-137`).
- **Minor divergence:** `db/schema.sql:48` defaults `p_learn` to 0.3, but Go bootstrap `NewConceptStateInDomain` sets `PLearn: 0.15` (`models/learner.go:70`). Effective default is 0.15 (rows are created through Go).
- **Concurrency:** read-modify-write of concept state under serializable tx (`WithTx` → `BEGIN IMMEDIATE` on SQLite; `tools/interaction_apply.go:90-97`); phase transitions via `CompareAndSwapDomainPhase` (`engine/orchestrator.go:123-135`).

## 11. Docs-vs-code divergences (verified)

| # | Release-note / doc claim | Code reality | Evidence |
|---|---|---|---|
| D1 | "a separate Rasch/Elo calibration signal" shipped | **Removed** — "remove the unused Rasch/Elo path"; tests assert it must not be exposed | `CHANGELOG.md:164`; `tools/interaction_test.go:551-552,569-571`; zero impl hits repo-wide |
| D2 | "BKT × IRT × PFA ... updating the learner model on every interaction" | Only **BKT + FSRS** mutate state. IRT theta preserved (`newTheta = priorTheta`); PFA excluded from learner-model update and alert policy | `tools/interaction_apply.go:63-68,282-286` |
| D3 | "PFA (plateau detection)" as live algorithm | PFA columns dropped (issue #55, never consumed); plateau inference retired | `db/migrations.go:131-137`; `engine/alert.go:142-143` |
| D4 | "28 MCP tools" | **46** tools registered (test asserts 46) | `tools/tools_register_test.go:221-222` |
| D5 | "6 cron jobs" | **8** jobs: + `consolidation` and `requeue_stale` unmentioned | `engine/scheduler.go:844-899` |
| D6 | `docs/regulation-design/07-threshold-resolver.md` describes legacy thresholds as default | Code default is **unified** 0.85 (promoted after eval); legacy only via `REGULATION_THRESHOLD=off` | `algorithms/thresholds.go:28-33` (design dir is a non-normative archive per its README) |
| D7 | `p_learn` default | schema.sql says 0.3; Go bootstrap says 0.15 (effective) | `db/schema.sql:48` vs `models/learner.go:70` |

## 12. Explicitly empty / not present

- **No separate sequencing algorithm** beyond: regulation pipeline (§3) + KST frontier (§1.7) + FSRS due-dates + recall-need/critical-forgetting bypasses. There is no SM-2, no Leitner, no independent scheduler module.
- **No live IRT item calibration** — item parameters are never estimated (`algorithms/irt.go:18-19`); `FSRSDifficultyToIRT` deprecated.
- **No PFA implementation file** — the "algorithm" is an in-memory recomputation that was retired with its alert.
- **No Rasch/Elo code** — removed (D1).
- **No content pipeline** — graph/curriculum are LLM-authored (§9).
- **No per-learner FSRS weight fitting** — the 19 weights are global constants; no `--optimize`-style personalization.
- **No deep learner profile** — `Learner` row holds identity + objective + profile JSON only (`models/learner.go:9-18`); no psychological profiling machinery (mirror/autonomy outputs are explicitly descriptive-only).

---

*End of survey. Commit `221b57e6a1927c8509051322fed531205d2b7ea9`.*


