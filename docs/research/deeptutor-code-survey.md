# DeepTutor Learning-Subsystem Survey

- **Repo:** `HKUDS/DeepTutor` (surveyed at `~/workspace/deeptutor-survey/DeepTutor`)
- **Commit:** `17b3aaf60c1a7c2fcddbe9936c4c9ec7900650f0` (`docs: sync 40k milestone and badges across README translations`)
- **Survey date:** 2026-09-21
- **Method:** read-only code survey. Every behavioral, default, and threshold claim cites `file:line` relative to the repo root. Docstring claims were verified against code; divergences are listed explicitly. Genuinely empty areas are reported as empty, not padded.
- **Scope:** learning/cognitive/scheduling/memory/assessment/sequencing mechanisms only. Excluded: chat UI, IM integrations, Docker/deployment, visualizers, RAG internals, `video_learning` — except where they touch the mechanisms below.

## Executive summary

**Headline: DeepTutor implements no standard learning-science algorithm.** There is no FSRS, no SM-2, no Leitner, no BKT, no IRT, no PFA, no KST, and no Elo anywhere in the codebase. What exists is a small set of hand-rolled deterministic mechanisms:

1. **`SpacedRepetitionScheduler`** (`deeptutor/learning/scheduler.py`) — a custom hybrid: Leitner-like fixed interval ladders per knowledge type + an exponential-forgetting layer that borrows FSRS's *vocabulary* (stability S, difficulty D, retrievability R, desired retention 0.9) but none of its fitted update equations. Its own protocol docstring says verbatim: *"The default baseline is exponential forgetting with type-specific cold-start priors — not a calibrated FSRS fit."* (`deeptutor/learning/scheduler.py:43-46`)
2. **SM-2-style practice scheduler** (`deeptutor/services/practice/scheduler.py`) — a separate, real deterministic SRS for the standalone practice feature (ease factor 2.5→1.3 floor, 4-rating scale, 365-day cap). Its docstring: *"This is an SM-2-style cold-start policy, not a fitted FSRS model."* (`deeptutor/services/practice/scheduler.py:1-4`)
3. **Recency-weighted mastery score** (`deeptutor/learning/mastery.py`) — weighted accuracy over the last ≤5 attempts with a confidence cap; the docstring names IRT/BKT only as *future replacements*.
4. **Deterministic mastery-gate routing policy** (`deeptutor/learning/policy.py`) — 0.9 quantitative gate for MEMORY/PROCEDURE, qualitative Feynman gate for CONCEPT/DESIGN, strict `next_objective` precedence.
5. **Deterministic string-match grading** (`deeptutor/learning/grading.py`) — no LLM scoring, no rubric weights.

The two "FSRS references" in the repo are both disclaimers, not implementations: the marginnote4 one (`deeptutor/capabilities/marginnote4/models.py:140-141`) is a docstring noting that DeepTutor tracks mastery *"without touching MN4's private FSRS scheduling data"* — i.e. the external app's scheduler, deliberately not replicated.

Architecturally, the design axiom is stated in `deeptutor/capabilities/mastery/capability.py:38-45`: *"the intelligence lives at the loop's exit — the model decides what to teach and how to question — while the gate that decides whether the learner may advance is a deterministic engine call."* The LLM does pedagogy; the engine does gating, scheduling, and state.

---

## 1. Algorithm inventory (every mechanism, with formulas)

### M1. Per-type fixed interval ladders (Leitner-like, custom)

Static review-interval ladders (days) per `KnowledgeType`, used to seed the first due date, hydrate legacy states, and snap computed intervals back to a ladder index (`deeptutor/learning/scheduler.py:11-16`):

```python
INTERVAL_SEQUENCES = {
    KnowledgeType.MEMORY:    [0, 1, 3, 7, 14, 30, 60],
    KnowledgeType.CONCEPT:   [3, 7, 14, 30],
    KnowledgeType.PROCEDURE: [3, 7, 14],
    KnowledgeType.DESIGN:    [14, 28],
}
```

- `get_initial_state` sets `next_review_at = now + intervals[0]` days (`deeptutor/learning/scheduler.py:158`).
- After every update, `_snap_interval_index` snaps the computed interval to the nearest rung (`deeptutor/learning/scheduler.py:192, 305-308`).
- Invoked when a KP is first reviewed (`deeptutor/learning/service.py:321` in `_apply_grade`; `deeptutor/learning/service.py:1150` in `record_qualitative`).

### M2. Exponential-forgetting retention layer (custom; FSRS vocabulary, not FSRS math)

Memory decay modeled as `R(t) = e^(−t/S)` with stability S in days (`deeptutor/learning/scheduler.py:117-128`):

```python
def _stability_from_interval(interval_days, desired_retention):
    return max(_MIN_STABILITY_DAYS, interval_days / -math.log(retention))   # S = I / −ln(r)

def _interval_from_stability(stability, desired_retention):
    return max(_EPS, max(stability, _EPS) * -math.log(retention))            # I = S · −ln(r)

def retrievability(self, state, *, now=None):
    return min(1.0, max(0.0, math.exp(-elapsed_days / stability)))           # R = e^(−t/S)
```

With `r = 0.9`, `I = S · ln(1/0.9) ≈ 0.1054·S`.

Defaults (`deeptutor/learning/scheduler.py:36-39`): `DEFAULT_DESIRED_RETENTION = 0.9`, `_MIN_STABILITY_DAYS = 0.5`, `_FAIL_QUALITY = 0.5`, `_EPS = 1e-6`. Type priors (`deeptutor/learning/scheduler.py:22-34`): priority `{MEMORY:2, CONCEPT:3, PROCEDURE:4, DESIGN:5}`; difficulty `{MEMORY:0.3, CONCEPT:0.4, PROCEDURE:0.5, DESIGN:0.6}`.

**Difficulty is a static cold-start prior only.** It is assigned at init (`deeptutor/learning/scheduler.py:163`) and in `hydrate` (`deeptutor/learning/scheduler.py:142-145`); nothing in `schedule_review` ever updates `state.difficulty` — unlike real FSRS, where D is recomputed on every grade.

### M3. Success/failure update rule (`schedule_review`)

Driven by a resolved quality in [0,1] (`deeptutor/learning/scheduler.py:296-299`): `evidence.quality` if set, clamped; else `1.0` if `result == "correct"` else `0.0`.

- **Fail, `quality < 0.5`** (`deeptutor/learning/scheduler.py:199-207`): `stability = max(0.05, stability × 0.5)`; `retrievability = max(quality, 0.2)`; `consecutive_wrong += 1`, `consecutive_correct = 0`, `lapse_count += 1`; counter resets at ≥2. Next interval forced down: `min(interval, max(interval × 0.5, 0.1))` days (`deeptutor/learning/scheduler.py:225-228`) — failures return no sooner than 0.1 day (≈2.4 h).
- **Success, `quality ≥ 0.5`** (`deeptutor/learning/scheduler.py:208-217`): `growth = 1.2 + 1.5·q`; ×1.15 extra if `q ≥ 0.8` and `consecutive_correct ≥ 2`; `stability = max(0.5, stability × growth)`; `retrievability = 1.0`. So a clean pass (q=1.0) multiplies stability ×2.7 (×3.105 with streak bonus); a borderline pass (q=0.6) ×2.1.

Invoked: (1) after every graded answer via `LearningService._apply_grade` (`deeptutor/learning/service.py:321`); (2) after qualitative Feynman assessment in `record_qualitative` — **only if a state exists and is already due** (`deeptutor/learning/service.py:1147-1149`); (3) from `replay` (`deeptutor/learning/scheduler.py:288`). `schedule_next(state, type, is_correct)` is a boolean convenience wrapper (`deeptutor/learning/scheduler.py:169-179`).

Grade→SRS quality mapping (`deeptutor/learning/service.py:344-349`, `1137-1145`): quiz correct → 1.0 (0.6 if retrying an active error); quiz wrong → 0.0; qualitative pass → 1.0/0.9; qualitative fail → 0.2 (which is < `_FAIL_QUALITY`=0.5, i.e. a fail branch).

### M4. Forgetting-risk score + review queue (custom heuristic)

Composite risk used to order the review queue; sort key `(-forgetting_risk, -overdue, priority)` (`deeptutor/learning/scheduler.py:87-91`). Exact formula (`deeptutor/learning/scheduler.py:243-262`):

```python
risk = 1.0 - recall                                   # base forgetting probability
if moment > state.next_review_at:
    risk += min(overdue_days / 7.0, 0.25)             # overdue bonus, capped +0.25
if kp_id in _error_kp_ids(progress):
    risk += 0.2                                       # active/retrying error record
if state.lapse_count:
    risk += min(0.1 * state.lapse_count, 0.2)         # lapse history, capped +0.2
return min(1.0, max(0.0, risk))
```

Queue rebuilt after every graded answer (`deeptutor/learning/service.py:323`) and every qualitative assessment (`deeptutor/learning/service.py:1151`). "Due" = `task.due_at <= now` (`deeptutor/learning/scheduler.py:266`); `get_due_tasks` serves max 5 per call (`deeptutor/learning/scheduler.py:264-270`); `policy.due_reviews` is uncapped (`deeptutor/learning/policy.py:134-140`). DEBUG mode (`LEARNING_DEBUG=1/true/yes`) switches the time unit from days to seconds (`deeptutor/learning/scheduler.py:109-115`).

### M5. Mastery score — recency-weighted accuracy with confidence cap

`compute_mastery(correctness: list[bool]) -> float` (`deeptutor/learning/mastery.py:30-45`): weighted mean over the last ≤5 attempts, weights `(0.5, 0.7, 0.85, 0.95, 1.0)` oldest→newest (`deeptutor/learning/mastery.py:16`), capped at 0.5 with 1 attempt / 0.8 with 2 attempts (`_CONFIDENCE_CAP`, `deeptutor/learning/mastery.py:20`). **Consequence: with the 0.9 gate, an objective cannot be mastered in fewer than 3 attempts** — even two perfect answers cap at 0.8 < 0.9 (confirmed by tests, e.g. `deeptutor/learning/tests/test_grading.py:288-296`).

Not BKT/IRT — no latent trait, no slip/guess parameters, no Bayesian update. The docstring explicitly frames IRT/BKT as *future* alternatives: *"To plug in a richer model (e.g. an IRT/BKT estimate or a tuned spec), replace `compute_mastery` alone"* (`deeptutor/learning/mastery.py:7-10`). Callers: `LearningService.calculate_mastery` → `compute_mastery` (`deeptutor/learning/service.py:211-216`), called from `_apply_grade` after every graded answer (`deeptutor/learning/service.py:312-314`); result stored in `progress.mastery_levels[kp_id]`.

### M6. Mastery gate / pass thresholds (policy)

- Quantitative: `QUANTITATIVE_GATE = {MEMORY: 0.9, PROCEDURE: 0.9}` — comment cites Alpha School's "90% before you advance" (`deeptutor/learning/policy.py:31-39`). Unknown types fall back to 0.9 (`deeptutor/learning/policy.py:87-91`).
- Qualitative: CONCEPT/DESIGN have no numeric bar; mastery is the boolean `progress.qualitative_mastery[kp.id]` set by `record_qualitative` (LLM-judged Feynman explanation); display maps pass → 1.0 (`deeptutor/learning/policy.py:40-46, 55`).
- `is_assessed_mastered`: quantitative `mastery_levels[kp] >= 0.9`, else qualitative boolean (`deeptutor/learning/policy.py:95-100`). `is_mastered` additionally passes on an explicit learner claim (`learner_mastery_overrides`), with `"learner"` vs `"system"` provenance (`deeptutor/learning/policy.py:103-126`).
- Qualitative side effects (`deeptutor/learning/service.py:1131-1132`): on fail, `mastery_levels[kp] = min(current, 0.4)` (hard cap); on pass, `max(current, 1.0)`.
- `LearningModule.pass_threshold = 0.7` (`deeptutor/learning/models.py:95`) exists but is **not consulted** by any gate function read — inert/vestigial.
- `next_objective` precedence (`deeptutor/learning/policy.py:246-312`): `answer_pending` → `review` (due SR items, highest forgetting risk first) → `probe` (untouched) / `assess` (qualitative below gate) / `practice` (quantitative below gate) → `complete`. Advancement is computed, never tracked — "the gate is the cursor."

### M7. Deterministic grading (`deeptutor/learning/grading.py`)

`grade_answer(user, expected, question_type) -> bool` — pure string match, no LLM (`deeptutor/learning/grading.py:11-51`):

| `question_type` | Rule |
|---|---|
| `choice` | case/space-insensitive exact match |
| `short` | exact match, else `SequenceMatcher.ratio() >= 0.85` **iff** `len(expected) <= 30` (long answers get no fuzzy match) |
| `open` | ≥60% of expected keywords (split on `,;，；。\n`) present as substrings |
| any | empty/blank expected → always `False` (fail-closed); unknown type → `False` |

Error classification (`deeptutor/learning/grading.py:54-66`): blank answer → `METACOGNITIVE`; any non-blank wrong answer → `APPLICATION_ERROR` (the richer four-type taxonomy is assigned later by the LLM). Grading is fail-closed end-to-end: `is_correct = bool(expected_answer) and grade_answer(...)` (`deeptutor/learning/service.py:284-286`).

### M8. Assessment persistence (`deeptutor/learning/assessment.py`)

Not item generation — `record_assessment` persists one graded attempt into the unified Question Notebook (`deeptutor/learning/assessment.py:234-269`). Items are authored/selected by LLM tools outside this module. Result vocab (`deeptutor/core/assessment.py:9`): `"correct" | "incorrect" | "partial" | "ungraded"`; **only `"correct"` maps to `is_correct=True` — `"partial"` counts as wrong** (`deeptutor/learning/assessment.py:38-41`). Identity: `assessment_id = sha1(session_id|turn_id|question_id)` (`deeptutor/learning/assessment.py:176-179`); `mastery_path_id`/`knowledge_point_id` linkage kept only for `source="mastery_path"` (`deeptutor/learning/assessment.py:202-215`). No numeric scoring in this module.

### M9. Question card (`deeptutor/learning/question_card.py`)

`build_question_card` (`deeptutor/learning/question_card.py:63-84`) produces `{question_id, prompt, question_type, objective{id,name}, difficulty, attempt, options[{label,body}], allow_free_text=True}` — **deliberately withholding `expected_answer`/`explanation`** until graded (`deeptutor/learning/question_card.py:68-69`). Pose event key `"mastery_question"`, graded verdict key `"mastery_grade"` (`deeptutor/learning/question_card.py:42,46`). `attempt_number` is 1-based, counted from the durable attempt log (`deeptutor/learning/question_card.py:51-59`). No item-selection algorithm (no difficulty targeting, no IRT matching) exists in these files.

### M10. SM-2-style practice scheduler (`deeptutor/services/practice/scheduler.py`)

A separate, real deterministic SRS for the standalone practice/review feature. `schedule()` (`deeptutor/services/practice/scheduler.py:32-62`): state `{interval_days, ease (start 2.5), streak, lapses, due_at, last_review_at, review_count, version}`; ratings `again|hard|good|easy` (Anki-like 4-button scale); `again` → 10-min interval, `ease − 0.2` (floor 1.3), streak reset, lapses+1; `hard` → interval ×1.2, `ease − 0.15`; `good` → 3.0 days first review else interval × ease; `easy` → ×1.3, `ease + 0.15` (cap 3.0); interval capped at 365 days. Also `day_bounds(timezone, now)` (DST-aware day boundaries, lines 15-27). Called from exactly one place: `deeptutor/services/practice/storage.py:272` (SQLite review transaction); `day_bounds`/`Rating` used by `deeptutor/api/routers/practice.py` and `deeptutor/services/practice/analytics.py`. Not SM-2 proper (no 0–5 scale, no SM-2 easiness formula) and explicitly not FSRS.

---

## 2. Learner state: schema, persistence, identity, migration

### 2.1 Schema (`deeptutor/learning/models.py`)

All models are Pydantic `BaseModel` with `extra="ignore"` (verified at `deeptutor/learning/models.py:81,90,107,…`) — unknown/retired fields deserialize silently. Enums with legacy `_missing_` hooks: `KnowledgeType` (`memory|concept|procedure|design`, `models.py:24`), `ErrorType` (`structural|deviation|application|metacognitive`, `models.py:36`), `LearningStage` (`diagnostic|explain|feynman_check|practice|error_diagnosis|review|completed`, `models.py:61`), `InteractionStatus` (`registered|awaiting_input|answered|graded|abandoned`, `models.py:275`), `TopicSourceKind` (9 values, `models.py:334`).

Aggregate root **`LearningProgress`** (`deeptutor/learning/models.py:456-505`): `book_id: str` (required); `learner_profile: LearnerProfile | None`; `name: str = ""`; `diagnostic: DiagnosticResult | None`; `modules: list[LearningModule]`; `current_module_id`; `current_stage = DIAGNOSTIC`; `current_kp_index`; `mastery_levels: dict[str,float]`; `qualitative_mastery: dict[str,bool]`; `knowledge_types`; `quiz_attempts: list[QuizAttempt]`; `error_records: list[ErrorRecord]`; `learning_evidence: list[LearningEvidence]`; `repetition_states: dict[str,RepetitionState]`; `review_queue: list[ReviewTask]`; `learner_mastery_overrides: dict[str,LearnerMasteryOverride]`; `pending_question: PendingQuestion | None`; `feynman_retries`, `feynman_explanations`, `stage_failure_counts`, `stage_failure_notes` (dicts); `version: int = 0`; `created_at`/`updated_at`.

Key state models:
- `RepetitionState` (`models.py:174-190`): `interval_index=0`, `consecutive_correct/wrong=0`, `next_review_at` (required), `difficulty=0.3`, `stability=0.0`, `retrievability=1.0`, `desired_retention=0.9`, `review_count=0`, `lapse_count=0`, `last_review_at=None`.
- `LearningEvidence` (`models.py:151-171`): durable review event — `knowledge_point_id`, `timestamp`, `source="mastery_path"`, `assessment_type ∈ {quiz, qualitative, review}`, `result ∈ {correct, incorrect, partial}` (default `"incorrect"`), `quality: float|None`, `hints_used=0`, `attempt_count=1`, `confidence?`, `response_time?`, `session_id`, `turn_id`. Quality is "inferred from the outcome (not a learner self-rating)" (`models.py:152-155`).
- `QuizAttempt` (`models.py:114-125`): `question_id`, `knowledge_point_id`, `is_correct` (required); `module_id=""`, `user_answer`, `error_type?`, `self_attribution=""`, `mastery_estimate=0.0`, `timestamp`.
- `ErrorRecord` (`models.py:136-149`): `id`, `question_id`, `knowledge_point_id`, `module_id`, `error_type` (required); `self_attribution=""`, `ai_confirmation=""`, `retry_history: list[RetryAttempt]`, `status ∈ {active, retrying, review, graduated} = "active"`.
- `PendingQuestion` (`models.py:224-273`): single outstanding slot — `question_id`, `knowledge_point_id` (required); `module_id=""`, `prompt=""`, `question_type="short"`, `expected_answer=""`, `options`, `explanation=""`, `difficulty=""`. A `@field_validator("options", mode="before")` (`models.py:254`) converts legacy `["A: body", …]` string rows into `PendingOption`s.
- `LearnerProfile` (`models.py:410-443`): five free-text fields (`prior_knowledge`, `target_level`, `time_budget`, `preferences`, `notes`), all `""`; merge-only, 600-char cap per field (`deeptutor/learning/service.py:39-56`).
- `MasteryInteraction` (`models.py:291-306`), `MasteryEvent` (`models.py:308-321`), `MasteryPathLease` (`models.py:323`), `TopicMetadata` (`models.py:378-391`, default emoji `🧭`), `MasteryTopic` (`models.py:393`).
- Content: `KnowledgePoint{id, name, type, module_id}` (`models.py:80-87`); `LearningModule{id, name, order, pass_threshold=0.7, objective="", knowledge_points=[]}` (`models.py:89-103`).

### 2.2 Persistence (`deeptutor/learning/storage.py`)

**SQLite**, one file `mastery.sqlite3` (`LearningStore._DB_FILENAME`, `storage.py:321`) under `<workspace>/learning/mastery/` (app default) or an explicit root. Legacy `<path-id>.json` files are lazily imported once then archived under `.legacy/` (`storage.py:697-800`). No JSON/in-memory primary store remains.

Tables (DDL `storage.py:376-540`): `mastery_paths` (`path_id` PK, whole-`LearningProgress` `state_json`, `revision`, `owner_session_id`); `mastery_path_sessions` ((path_id, session_id) PK + unique index on `session_id` alone → one conversation on at most one path); `mastery_interactions` (partial unique index → **at most one active question per path**); `mastery_events` (append-only audit); `mastery_learning_evidence` (flattened projection, wholesale re-synced per commit, `storage.py:627-666`); `mastery_schema_migrations`; `mastery_path_leases` (one mutating turn per path); `mastery_topic_meta`; `mastery_topic_sources`.

Write discipline: WAL mode (`storage.py:376`); `timeout=30.0`, `busy_timeout=30000` (`storage.py:602-608`); **every writer takes `BEGIN IMMEDIATE`** (`storage.py:772,901,996,1102,1375`); optimistic compare-and-swap on `revision` (`UPDATE … WHERE path_id=? AND revision=?`) raising `LearningConflictError` on stale writes (`storage.py:80-91, 916-943`); no data caching (fresh connection per op, `storage.py:601-612`); no write batching. `transaction()` commits one revision **only if `tx.changed`** (`storage.py:1022-1062`); every committed write publishes a wake-up signal to the process-local event hub (`storage.py:974-981`). ID validation rejects path traversal (`_validate_id`, `storage.py:355-359`).

### 2.3 Identity (`deeptutor/learning/identity.py`)

**No user id / account id / tenant key exists anywhere in the learning package.** Learner = resolved `path_id`, priority: explicit `configured_path_id` → first book reference → the `session_id` itself as scratch fallback (`resolve_mastery_path_binding`, `identity.py:28-49`). `sanitize_mastery_path_id` keeps `[A-Za-z0-9_-]`, falls back to `"default"` (`identity.py:16-19`). Sessions are conversation ids with exclusive one-path-per-session membership; multiple sessions may share a path; `owns_path` is separate permanent creator tracking (`storage.py` `owner_session_id`). The store is workspace-scoped — whoever shares a workspace shares `mastery.sqlite3`.

### 2.4 Migration (`deeptutor/learning/migration.py`)

One-way V1 (`<workspace>/learning/`) → V2 (`<workspace>/learning/mastery/`) workspace migration, run on `LearningStore()` construction (`storage.py:324-331`; `migration.py:33-34, 174-196`): cross-process file lock → stage to `learning/archive/.v1-migration-in-progress/` → WAL-checkpoint + copy V2 DB (existing V2 DB always wins) → archive live JSONs then import via `import_legacy_json` (corrupt → `archive/failed/`) → write `migration.json` (`format_version: 2`, DB sha256, row counts) → remove V1 artifacts → rename staging to `learning/archive/v1-<stamp>`. Archives are never read. In-DB: `mastery_schema_migrations` tracks `learning_evidence_projection_v1`; schema init converges single-session-membership (`storage.py:541-599`) and backfills neutral topic metadata (deterministic `sha256(path_id)` `map_seed`, `🧭`). No down-migration.

---
## 3. Policy, navigation, pending queue, events, service

### 3.1 Policy — every decision rule (`deeptutor/learning/policy.py`, 488 lines, pure logic, no I/O)

Inputs: a `LearningProgress` (+ optional `now`, `pending_session_id`). Outputs: gate booleans, floats, `NextStep(action ∈ {answer_pending, review, probe, practice, assess, complete})`, render dicts.

| # | Condition → Action | Cite |
|---|---|---|
| 1 | `MEMORY`/`PROCEDURE` → threshold **0.9** (`QUANTITATIVE_GATE`) | `policy.py:36-39` |
| 2 | `CONCEPT`/`DESIGN` → qualitative gate: recorded boolean pass in `qualitative_mastery` | `policy.py:43-46, 95-100` |
| 3 | Unknown type → `gate_threshold` falls back to **0.9** | `policy.py:87-91` |
| 4 | `mastery_levels[kp] (default 0.0) >= 0.9` → assessed-mastered (quantitative) | `policy.py:95-100` |
| 5 | `is_mastered` = assessed-mastered **OR** learner override (`mastery_source` → `"system"`/`"learner"`/`""`) | `policy.py:103-126` |
| 6 | `objective_status`: mastered → `"mastered"`; any attempt or qualitative entry → `"learning"`; else `"new"` | `policy.py:138-145` |
| 7 | `display_mastery`: qualitative pass → **1.0** (`_QUALITATIVE_PASS_DISPLAY`); else `mastery_levels[kp]` (default 0.0) | `policy.py:55, 129-135` |

`next_objective` precedence (`policy.py:246-312`): (1) `answer_pending` — posed question awaiting grade; (2) `review` — due SR items, first by `(-forgetting_risk, -overdue, priority)`; (3) `probe` (untouched) / `assess` (qualitative below gate) / `practice` (quantitative below gate) — first non-mastered KP in module order; (4) `complete`. `due_reviews`: `due_at <= now`, `now` defaults to `time.time()` (`policy.py:148-156`). `gate_kind(kp)` → `"qualitative"` for CONCEPT/DESIGN, `"quantitative"` otherwise (`policy.py:219-227`). `path_display_name` precedence: stripped `progress.name` → first module name → `book_id` (`policy.py:58-78`).

### 3.2 Navigation (`deeptutor/learning/navigation.py`, 348 lines — read-only, non-teaching)

Walks the store for the topic atlas; never touches leases, pending questions, or mastery levels. `topic_cards(query="")` → active topics newest-first with gate-accurate counts (`navigation.py:87-150`); `resolve_module` matches by exact id → exact name → substring/fuzzy → position incl. Chinese numerals 一..十 (`navigation.py:188-246`); `topic_sessions` joins mastery store with session store (`navigation.py:249-307`).

Payload caps: `TOPIC_LIMIT=20` (`navigation.py:30`), `MODULE_LIMIT=14` (`navigation.py:32`), `SESSION_LIMIT=20` (`navigation.py:34`), `LAST_MESSAGE_CHARS=160` (`navigation.py:36`); every cap reports what it clipped (`topics_omitted` etc., `navigation.py:54-59`).

### 3.3 Pending (`deeptutor/learning/pending.py`) — a single slot, not a queue

`LearningProgress.pending_question` holds **at most one** posed-but-unanswered question. `pending.py` projects it to `PublicPendingQuestion{question_id, prompt, question_type, options}` excluding the answer key (`pending.py:237-281`).

Lifecycle (`InteractionStatus`: `registered → awaiting_input → answered → graded`/`abandoned`, `models.py:275-288`): `register_question` is atomic — an already-active question is returned instead of overwritten (`created=False`, `service.py:383-456`); `grade_interaction` is idempotent (re-grading a GRADED interaction returns the stored result with `replayed=True`; superseded ids raise `StaleInteractionError`; nothing outstanding raises `NoPendingInteractionError`, `service.py:571-676`). Slot cleared on grade, `clear_pending_question`, `abandon_active_question`, module replacement dropping the objective, or `reset_path` (`service.py:362-365, 678-682, 830-836, 954-989, 1005`).

Multiple-choice resolution (`pending.py:16-236`): `positional_label(i)` → A..Z then 27, 28…; `resolve_choice_submission` accepts exact label, labelled prefix, exact body match, or exactly one mentioned label (CJK-aware, e.g. `选C`); ambiguous input → `""` treated as **unreadable, never wrong**; `is_readable_choice_answer` additionally refuses interrogatives ("why is B wrong?" used to resolve to B and freeze the gate — stall #1004, `pending.py:183-236`).

### 3.4 Event hub (`deeptutor/learning/event_hub.py`, 140 lines)

Low-latency **wake-up channel**; "SQLite remains the replay authority" (module docstring). Signal = `{path_id, revision, reason, sequence}` (frozen dataclass, `event_hub.py:17-21`); `reason` is a **free-form string** (no enum), default `"topic.changed"`. Producer: `LearningStore` publishes synchronously after every commit (reason strings like `interaction.registered/answered/graded`, `attempt.recorded`, `mastery.assessed`, `path.reset`, `topic.deleted`, `session.bound/released`). Consumer: WebSocket atlas endpoint in `deeptutor/api/routers/mastery_path.py:680-745` replays the durable SQLite event tail from its cursor, then forwards. **Delivery is not guaranteed**: each subscription queue is `asyncio.Queue(maxsize=1)` with newest-wins coalescing (`event_hub.py:24-31, 98-103`); missed revisions are recovered only by consumer replay. Publish is synchronous and thread-safe under a `threading.RLock`, crossing into the uvicorn loop via `loop.call_soon_threadsafe` (`event_hub.py:75-103`); monotonic `sequence` from `itertools.count(1)` under the lock (`event_hub.py:49, 86-90`).

### 3.5 Service (`deeptutor/learning/service.py`, 1247 lines)

`LearningService` has two layers: in-memory mutators (caller saves) and durable path-keyed methods (run inside `store.mutate` transactions that emit events + hub signals).

Key entry points: `get_or_create(book_id)`; `init_modules`/`replace_modules` (purges per-KP state for removed KPs); `record_quiz_attempt` (wrong → open/update `ErrorRecord`; correct → graduate it); `calculate_mastery` (pure) / `update_mastery`; `grade_and_record` (legacy in-memory pipeline); `register_question` / `mark_question_awaiting` / `record_question_answer` / `grade_interaction` (idempotent, one-transaction grade path, `service.py:571-694`); `replace_modules_for_path` (append rebases ids `{book_id}_m{index}`/`{module_id}_kp{kp_index}`; replace preserves cursor/pending where objectives survive); `create_topic`; `rename_path`; `record_learner_profile` (merge-only, **600-char** field cap, `service.py:39-56`); `abandon_active_question`; `reset_path` (wipes state, keeps modules); `set_learner_mastery_override` (note cap **500** chars); `record_qualitative[_for_path]` (pass: `qualitative_mastery=True`, `mastery_levels=max(current,1.0)`; fail: `min(current,0.4)`); read APIs `list_path_overviews` (gate-accurate counts) / `list_progress`.

Main flows: quantitative path `register_question → record_question_answer → mark_question_awaiting → grade_interaction` (grade → `record_quiz_attempt` → `update_mastery(calculate_mastery(...))` → `scheduler.schedule_review` + `build_review_queue` → clear pending → emit events); qualitative path `mastery_assess` tool → `record_qualitative_for_path`; spaced review via `policy.due_reviews` re-entering `_apply_grade`.

Constants: `_MAX_PATH_NAME_LEN = 200`, `_MAX_PROFILE_FIELD_LEN = 600` (`service.py:39-56`). Errors: `MasteryInteractionError`, `NoPendingInteractionError`, `StaleInteractionError` (`service.py:59-81`).

Mechanism-relevant notes from `prompts.py`/`topic_*.py`: prompts are a loader (`prompts/{en,zh}.yaml`, lru-cached maxsize 8, locale fallback, `prompts.py:21-39`) — no decision logic. Outline generation (`topic_generation.materialize_modules`, `topic_generation.py:308-455`): modules numbered by `order = len(modules)`; module `objective` one sentence, clipped to **300** chars; KP names ≥2 chars, ≤200; invalid types default to `"concept"`; caps `DEFAULT_MODULE_LIMIT=8`, `MAX_MODULE_LIMIT=20` modules/route, `_MAX_OBJECTIVES_PER_MODULE=7` KPs/module (`topic_generation.py:30-35, 387-392`); IDs are durable identity — fresh builds get `{path_id}_m…`/`{module_id}_kp…`, regenerations get uuid-suffixed ids, so deleted objectives' evidence can't be reused (`topic_generation.py:298-306, 360-377`).

---

## 4. Capability layer (`deeptutor/capabilities/`)

### 4.1 Mode system (`deeptutor/capabilities/mastery/mode.py`, 177 lines)

Three session modes: `OUTLINE` ("designing the outline… the only one that may change the map"), `STUDY` ("working the agreed outline forward"), `REVIEW` ("re-testing what is already mastered, whether or not it is due") (`mode.py:44-53`). `DEFAULT_MODE = STUDY` (`mode.py:55-57` — preserves pre-modes semantics).

`TOOL_MODES` (`mode.py:63-76`):

| Tool | Allowed modes |
|---|---|
| `mastery_build`, `mastery_revise` | outline only |
| `mastery_quiz`, `mastery_grade`, `mastery_assess`, `mastery_skip_question` | study, review |

Everything else shared: `mastery_status`, `mastery_mode`, `mastery_profile`, `mastery_paths`, `mastery_switch`, `mastery_leave`.

**Why enforcement is at call time, not mount time** (module docstring, `mode.py:18-40`): a turn's tool schemas *and* system prompt are assembled once before the first round (`AgenticLoopPipeline.run`, `deeptutor/agents/loop/pipeline.py:392-426`), so a mid-turn mode switch would win no new tools until the next turn — "Call a tool to unlock that mode's tools" would be false for the turn that called it. So every mastery tool stays mounted and mode-owned tools refuse at call time via `ensure_mode`/`_wrong_mode_result`, naming the fix (`wrong_mode_message`, `mode.py:147-164` — "a refusal that only says 'no' is one the model retries verbatim"). `mastery_mode` returns the new mode's prompt block in its own result because the system prompt still frames the old mode (`mode.py:39-40`; `tools.py:1599-1608`).

`normalize_mode` = what to *show* (always a real mode, defaults study; `mode.py:82-90`) vs `enforced_mode` = what to *enforce* (returns `None` when unrecorded, so pre-modes/CLI turns enforce nothing; `mode.py:98-114`). The call site enforces on the **raw** value, never normalized (`tools.py:568-585`; `loop.py:204-208`). Single admission rule: study with no agreed outline is refused; review is never gated on due dates ("a due date is a reminder, not a permission"; `mode.py:124-139`), shared by the tool and the REST mode buttons.

### 4.2 Mastery tools (`deeptutor/capabilities/mastery/tools.py`, 2351 lines; mount set `MASTERY_TOOL_NAMES`, `tools.py:74-87`)

12 tools; all subclass `BaseTool` (`deeptutor/core/tool_protocol`, `tools.py:46`):

1. `mastery_status` — "Call FIRST every turn" (`tools.py:662-663`); read-only snapshot (gate, map, pending, profile); ungated. Reads via `_load_path` — "Reading must not create" (bug #909, `tools.py:454`).
2. `mastery_quiz` — register + pose a MEMORY/PROCEDURE question; **ends the turn** (`tools.py:755-1014`). Study/review only. `expected_answer`/`explanation` hidden from learner trace; `explanation` ≤2000 chars; difficulty enum easy/medium/hard (unrecognized dropped, not rejected, `tools.py:134-141`); one open question per path (`already_pending` re-presents, `tools.py:987-998`); review-scope refusal for unmastered KPs in review mode (`tools.py:500-531`); choice labels must be well-formed A,B,C…, duplicate bodies rejected.
3. `mastery_grade` — deterministic grading of the pending answer (`tools.py:1015-1236`). Study/review only. Unreadable answers returned as unreadable, **not graded wrong** (`tools.py:1083-1094`); idempotent; syncs attempts to the question bank with **5.0s timeout** (`tools.py:360`).
4. `mastery_assess` — record tutor judgement on CONCEPT/DESIGN after Feynman explanation (`tools.py:1237-1343`). Study/review only. Refuses quantitative objectives outright (`tools.py:1295-1302`).
5. `mastery_skip_question` — abandon open question, no grade, no credit (`tools.py:1344-1391`).
6. `mastery_build` — create/extend the skill map, **outline only** (`tools.py:1392-1519`). Modules `{name, objective (required one-sentence contract), knowledge_points[{name, type}]}`; mode `replace` (default)/`append`; server-generated ids `<path>_m<i>_kp<j>`; unknown types → `concept`; tolerant shape parsing for real model outputs (issue #1019, `tools.py:2086-2128`).
7. `mastery_mode` — switch mode; **shared, not in TOOL_MODES** (`tools.py:1521-1613`). Rebinds the live turn *and* persists to session (`tools.py:1593-1596`); reason ≤200 chars.
8. `mastery_profile` — merge learner intake (`tools.py:1615-1724`); ungated; at least one field required; reports `updated_fields`.
9. `mastery_revise` — reshape one module's KPs within its build-time `objective`, **outline only** (`tools.py:1725-1871`). Invariants: rewritten KP gets a **fresh id** (old evidence can't be claimed for new wording, `tools.py:2131-2146`); **mastered KPs are immutable** (`tools.py:2205-2214`); ≤7 KPs/module; module can't be left empty.
10. `mastery_paths` — list paths with objectives; hides empty paths (`tools.py:1872-1912`).
11. `mastery_switch` — rebind conversation to another path (`tools.py:1913-1975`); release-before-acquire, restores old lease on conflict (`binding.py:42-94`).
12. `mastery_leave` — detach to scratch path (`tools.py:1976-2033`).

Cross-cutting caps: `reason`/names ≤200 chars; module objective ≤300 (`_MAX_MODULE_OBJECTIVE`, `tools.py:2032`); KP names ≥2 chars.

### 4.3 `MasteryPathCapability` (`capability.py`, 112 lines)

Manifest `mastery_path`, `stages=["responding"]`, `tools_used=[*MASTERY_TOOL_NAMES, "rag", "read_source", "ask_user"]`, `cli_aliases=["mastery"]` (`capability.py:47-56`). `run()` resolves path binding (frontend `mastery_path_id` → book ref → session id), marks `metadata["mastery_mode"]`, takes the path lease for CLI/SDK (web turns use the runtime-managed lease, released by turn id in `finally` — since `mastery_switch` may have moved the turn), and runs `MasteryLoopPipeline` (`capability.py:59-110`). **Divergence:** the docstring's tool list (`capability.py:54-60`) omits `mastery_revise`, `mastery_mode`, `mastery_profile` and mislabels ungated `mastery_status` as a "gate tool" — code mounts all 12.

### 4.4 Loop & pipeline (`loop.py` 470 lines; `pipeline.py` 94 lines)

`MasteryLoopCapability` (a `LoopExtension`) is active when `metadata["mastery_mode"]` (`loop.py:144-146`). `owned_tools = (*MASTERY_TOOL_NAMES, "read_source")` (`loop.py:132`) — the tutor decides itself whether source text is worth reading KP-by-KP (`loop.py:112-129`). `rebinding_tools = {"mastery_switch", "mastery_leave", "mastery_mode"}` run first so the rest of the round lands on the new target (`loop.py:133-142`). `augment_kwargs` injects server-owned kwargs: `_mastery_path_id`, **raw un-normalized** `_mastery_session_mode`, `_session_id`, `_turn_id`, `_end_turn_on_card` (quiz), `_bind_active_mode`/`_bind_active_path` (`loop.py:172-238`). `pre_loop_seed` states an already-graded card verdict as fact (`loop.py:340-355`); `finish_instruction` blocks prose-quiz finishes (`loop.py:240-298`); `final_text_override` returns `""` so a posed card ends the turn — replaced the old `pause_for_user` lease-holding park (`loop.py:300-338`).

`MasteryLoopPipeline` (`pipeline.py`): same engine, tutor-protocol-first prompt — identity → `session.<mode>` block (via `normalize_mode`, `pipeline.py:43`) → policy → loop protocol → playbook. "A mastery turn mounts exactly what a chat turn would… plus the mastery tools" (`pipeline.py:20-25`). **Divergence:** `tools.py:8-9` still says tools mount "via the chat loop mastery capability" — stale vs the native pipeline.

### 4.5 `binding.py` / `choices.py`

`binding.py` (178 lines): three-place handoff — lease (per path, released by turn), session preference (next-turn resume), live turn (injected binder). `rebind_active_path` is release-before-acquire (`binding.py:42-94`); `leave_active_path` falls back to the conversation's scratch path with sticky ownership (`binding.py:96-135`); `remember_mode_on_session` persists mode best-effort (`binding.py:151-177`).

`choices.py` (273 lines): the multiple-choice data contract — translates model-registered option bodies → learner label answers → deterministic grading → question-bank persistence; re-exports pure primitives from `deeptutor.learning.pending` (`choices.py:42-52`), keeping the tool layer orchestration-only.

### 4.6 Capability protocol & registry (`protocol.py` 179 lines; `registry.py` 240 lines)

`LoopExtension` protocol (`protocol.py:48`): required `name`, `owned_tools` (static, for the settings UI; `protocol.py:84-86`), `is_active`, `system_block`, `augment_kwargs`, `pre_loop_seed`; optional `pre_loop`, `on_user_pause/on_user_resume`, `rebinding_tools`, `finish_instruction`, `tool_round_output_policy`/`final_text_override`. Invariant: a plain capability *augments* the full chat tool surface, never suppresses it (`protocol.py:53-58`); only `KnowledgeCapability` is exclusive (`protocol.py:128-149`).

Registry: 15 built-in loop capabilities as import-free `LoopCapabilitySpec` descriptors incl. `"mastery"` → `deeptutor.capabilities.mastery.loop:MasteryLoopCapability` (`registry.py:64-124`); `create()` raises on descriptor drift (`registry.py:50-58`); `all_loop_capabilities()` builds an isolated per-turn set (`registry.py:222-231`); external plugins via `deeptutor.extensions` entry points, built-ins shadow name conflicts (`registry.py:170-196`).

### 4.7 The seam: capability layer → `deeptutor/learning/`

Import discipline (`tools.py:50-70`): `learning.models`/`learning.policy` imported at load (pydantic-only, no cycle); `learning.service`/`storage`/`scheduler`/`assessment` imported **lazily inside call paths** to avoid closing an import cycle through the built-in registry. Path id is injected server-side (`_mastery_path_id` — "the model never supplies it", `tools.py:10-11`); each call constructs a fresh `LearningService(LearningStore())` so concurrent turns can't race (`tools.py:11-13, 112-116`). Engine calls observed: `service.store.load`, `service.register_question`, `service.mark_question_awaiting`, `service.grade_interaction(scheduler=SpacedRepetitionScheduler())`, `service.record_qualitative_for_path`, `service.replace_modules_for_path`, `service.record_learner_profile`, `service.abandon_active_question`, `store.bind_session`/`acquire_path_lease`/`release_leases_for_turn`; policy reads `is_mastered`, `gate_kind/threshold`, `next_objective`, `map_summary`, `display_mastery`; `learning.assessment.record_assessment` for best-effort question-bank sync. `deeptutor/tools/mastery_tool.py` is a pure compatibility re-export shim.

---
## 5. Content path (only as it feeds the mechanisms)

`deeptutor/knowledge/manifest.py` is a **document inventory** (`KbManifest`: name, provider, status, kb_type, total, `KbDocument{name, size}` list) for RAG/UX — **not consumed by the learning mechanisms**. The structures the tutor actually reads are in `deeptutor/learning/models.py`, generated LLM-side by `deeptutor/learning/topic_generation.py:materialize_modules`:

- `KnowledgeType`: `memory | concept | procedure | design` (`models.py:24-28`) — drives gate kind, interval ladders, difficulty priors.
- `KnowledgePoint{id, name, type, module_id}` (`models.py:80-87`); `LearningModule{id, name, order, pass_threshold=0.7, objective, knowledge_points[]}` (`models.py:89-103`) — `objective` is the module's one-sentence purpose.
- The full path state `LearningProgress` (§2.1) plus `LearningEvidence` review events (`models.py:151-171`), `RepetitionState` (`models.py:174-190`), `ReviewTask` (`models.py:193-204`), `QuizAttempt` (`models.py:114-125`), `ErrorRecord` (`models.py:136-149`).

Concept-graph format (book authoring layer, `deeptutor/book/models.py:250-279`, rendered by `deeptutor/book/blocks/concept_graph.py` — **not consumed by the schedulers**): `ConceptNode{id (short slug, e.g. "fourier_basis"), label, chapter_id, description?, weight (default 1.0)}`; `ConceptEdge{src, dst, relation: depends_on|extends|related, rationale}`; `ConceptGraph{nodes[], edges[]}`. Chapters anchor to sources via `SourceAnchor{kind: kb|notebook|chat|web|manual, kb_name, ref, snippet≤300 chars}` (`book/models.py:218-226`).

---

## 6. Docs-vs-code divergences (consolidated)

1. **"Not FSRS" is the honest label, but FSRS vocabulary invites misreading.** `scheduler.py:43-46` disclaims a calibrated fit, yet `RepetitionState` carries `difficulty`/`stability`/`retrievability`/`desired_retention` — FSRS terms with non-FSRS semantics (D never updated). Anyone skimming the schema will assume FSRS.
2. `storage.py:8-11` docstring says the store keeps `pending_question` synchronized — `pending_question` appears **zero times** in `storage.py` outside that docstring; the dual-write is done by `service.py` callers (`service.py:412, 444, 682, 806-811, 955-956, 981`).
3. `has_active_topics` docstring says "named, unarchived" (`storage.py:1341`) but the query checks only `status='active'` (`storage.py:1346-1349`).
4. `transaction()` docstring says "commit one revision" (`storage.py:979-988`) — it commits nothing when `tx.changed` is false (`storage.py:1022`).
5. Migration manifest `row_counts` covers only 5 of 9 tables (`migration.py:40-46`).
6. `policy.py` module docstring calls `is_mastered` the "HARD" gate — `is_mastered` also passes on learner override (`policy.py:112-126`); the hard gate is `is_assessed_mastered` (`policy.py:95-100`).
7. `grade_and_record` docstring claims "single source of truth" for grading (`service.py:230-240`) — the interactive path is the separate `grade_interaction`; two parallel implementations.
8. `LearningModule.pass_threshold = 0.7` is set everywhere (`models.py:95`; `topic_generation.py:436`) but read nowhere in the gate logic — inert.
9. `capability.py:54-60` docstring mislists the mounted tools (omits gated `mastery_revise`; mislabels ungated `mastery_status` as a "gate tool"; omits `mastery_mode`, `mastery_profile`) — code mounts all 12 (`capability.py:52`).
10. `tools.py:8-9` "chat loop mastery capability" phrasing is stale vs the native `MasteryLoopPipeline` (`pipeline.py:1-19`).
11. Repo `AGENTS.md` describes `mastery_path` as "chat loop + mastery tools" — under-describes the two-pipeline reality.
12. `build_review_queue` hydrates in place (`scheduler.py:280`) — a queue **read** has write side effects.
13. `record_qualitative` skips `schedule_review` when the state isn't due, and creates no state on a fail with no prior state (`service.py:1147-1150`).
14. `forgetting_risk` double-counts overdue days (decay in R plus the +0.25 overdue bonus), bounded by the 1.0 clamp (`scheduler.py:250-262`).
15. Stored `retrievability` is display-only — `retrievability()` recomputes from elapsed time anyway (`scheduler.py:215` vs `236-239`).
16. `LearningStage` cursor (`current_stage`, `current_module_id`, `current_kp_index`) is mutated by `advance_stage`/`switch_module` but ignored by `next_objective` — two parallel notions of "where am I" (`service.py:116-130`; `policy.py:246-312`).

---

## 7. Explicitly empty (no implementation found)

Searched case-insensitively across `deeptutor/` (implementation vs mention vs false-positive classified per hit):

- **FSRS**: no implementation. Three references, all disclaimers/mentions: `learning/scheduler.py:45` ("not a calibrated FSRS fit"), `services/practice/scheduler.py:1-4` ("not a fitted FSRS model"), `marginnote4/models.py:140-141` (external app's private scheduler, deliberately untouched). Dummy fixture strings in `tests/services/memory/*` are false positives.
- **BKT / Bayesian knowledge tracing**: one docstring name-drop as a *future* alternative (`learning/mastery.py:9`). No implementation.
- **IRT / item response theory**: one docstring name-drop (`learning/mastery.py:9`). No implementation. ("item response" phrase: zero hits; lightrag `IRTable` is Information Retrieval — false positive.)
- **PFA**: zero hits. **KST**: zero hits. **Elo**: zero true hits. **Leitner**: zero hits (the ladder in M1 is Leitner-*like* but never named or faithful). **SM-2**: one self-descriptive docstring ("SM-2-style"); no real SM-2 formula.
- **"knowledge tracing"**, **"forgetting curve"**/**`forgetting_curve`**, **"Ebbinghaus"**, **"half-life"**, **"mastery threshold"** (phrase), the word **"algorithm"** (in `learning/` and `services/practice/`), **interleaved practice** (all hits are thread/stream interleaving): zero.
- **Assessment item selection/generation algorithm**: none — items are authored by LLM tools; `assessment.py` only persists/normalizes; `question_card.py` only formats.
- **Adaptive difficulty**: none — `difficulty` is an LLM-supplied string badge on questions (normalized so it "never costs the learner a question") plus a static per-type cold-start prior; never estimated from responses.
- **State**: no encryption (plaintext SQLite/JSON), no TTL/expiry, no in-memory cache, no user/account scoping, no down-migration, no read audit, no soft-delete for paths.
- **Policy inputs**: no difficulty adaptation, streaks, time-of-day, or learner-skill inputs — only the progress aggregate and `now`.
- **Pending**: no TTL, no auto-abandon, no retry/backoff — an unanswered question stalls the path until graded or explicitly abandoned; single slot, no ordering.
- **Event hub**: no guaranteed/exactly-once delivery (maxsize=1 newest-wins coalescing); no closed event-type enum.

---

## 8. Consolidated numeric reference

| Constant | Value | Location |
|---|---|---|
| `INTERVAL_SEQUENCES` (days) | MEMORY `[0,1,3,7,14,30,60]`, CONCEPT `[3,7,14,30]`, PROCEDURE `[3,7,14]`, DESIGN `[14,28]` | `learning/scheduler.py:11-16` |
| `DEFAULT_DESIRED_RETENTION` | 0.9 | `learning/scheduler.py:36` |
| `_MIN_STABILITY_DAYS` | 0.5 | `learning/scheduler.py:37` |
| `_FAIL_QUALITY` | 0.5 | `learning/scheduler.py:38` |
| Type priority | MEMORY 2, CONCEPT 3, PROCEDURE 4, DESIGN 5 | `learning/scheduler.py:22-24` |
| Type difficulty prior (static) | 0.3 / 0.4 / 0.5 / 0.6 | `learning/scheduler.py:26-31` |
| Success growth | `1.2 + 1.5·q`; ×1.15 if `q≥0.8` and ≥2 consecutive correct | `learning/scheduler.py:210-213` |
| Failure update | stability ×0.5 (floor 0.05 d); next interval ≤½ formula interval, floor 0.1 d | `learning/scheduler.py:203, 227-228` |
| Forgetting risk | `(1−R) + min(overdue/7, 0.25) + 0.2·active_error + min(0.1·lapses, 0.2)`, clamp [0,1] | `learning/scheduler.py:250-262` |
| `get_due_tasks` cap | 5 per call | `learning/scheduler.py:264` |
| Mastery weights / caps | (0.5, 0.7, 0.85, 0.95, 1.0); caps {1:0.5, 2:0.8} | `learning/mastery.py:16,20` |
| Quantitative gate | ≥0.9 (MEMORY, PROCEDURE; fallback 0.9) | `learning/policy.py:31-39, 87-91` |
| Qualitative fail / pass | mastery pinned ≤0.4 / lifted to ≥1.0 | `learning/service.py:1131-1132` |
| `LearningModule.pass_threshold` | 0.7 — set, never read | `learning/models.py:95` |
| Short-answer fuzzy cutoff | `SequenceMatcher ≥ 0.85` iff `len(expected) ≤ 30` | `learning/grading.py:35-37` |
| Open-answer keyword cutoff | ≥0.6 matched | `learning/grading.py:44` |
| Evidence quality | correct 1.0 (0.6 on retry), wrong 0.0; qualitative pass 1.0/0.9, fail 0.2 | `learning/service.py:344-349, 1137-1145` |
| Assessment results | `correct/incorrect/partial/ungraded`; only `correct` ⇒ `is_correct=True` | `core/assessment.py:9`; `learning/assessment.py:38-41` |
| Profile field cap / override note cap | 600 / 500 chars | `learning/service.py:39-56`; `set_learner_mastery_override` |
| Outline caps | ≤20 modules/route (default 8); ≤7 KPs/module; module objective ≤300 chars; KP name 2–200 chars | `learning/topic_generation.py:30-35, 387-392`; `tools.py:2032, 2212` |
| Tool text caps | explanation ≤2000; reason/path_name/display names ≤200 | `capabilities/mastery/tools.py:919, 1609, 1490` |
| Question-bank sync timeout | 5.0 s | `capabilities/mastery/tools.py:360` |
| Atlas payload caps | 20 topics / 14 modules / 20 sessions / 160 chars last-message | `learning/navigation.py:30-36` |
| Practice scheduler | ease 2.5 start, floor 1.3, cap 3.0; interval cap 365 d; `again` → 10 min | `services/practice/scheduler.py:32-62` |

---

## 9. Call hierarchy (post-answer path)

```
LearningService.grade_and_record            (learning/service.py:222-242)
 └─ _apply_grade                            (learning/service.py:253-334)
     ├─ grade_answer                        (learning/grading.py:11-51)        → bool
     ├─ classify_error                      (learning/grading.py:54-66)        → ErrorType
     ├─ record_quiz_attempt → ErrorRecord open/graduate
     ├─ _record_quiz_evidence               (learning/service.py:336-353)    → LearningEvidence(quality)
     ├─ calculate_mastery → compute_mastery (learning/service.py:211-216; learning/mastery.py:30-45)
     │    → progress.mastery_levels[kp_id]
     ├─ scheduler.schedule_review           (learning/service.py:321; learning/scheduler.py:181-193)
     │    → state.{stability, retrievability, next_review_at, interval_index}
     └─ scheduler.build_review_queue        (learning/service.py:323; learning/scheduler.py:272-294)
          → progress.review_queue (sorted by review_sort_key)

Durable interactive path (separate implementation):
LearningService.grade_interaction           (learning/service.py:571-694)   [idempotent, one transaction]
 └─ same engine steps + MasteryInteraction lifecycle + question-bank sync

LearningService.record_qualitative[_for_path] (learning/service.py:1058-1149)  # Feynman pass/fail
 └─ qualitative_mastery[kp] = bool; mastery_levels cap/mirror
 └─ scheduler.schedule_review — ONLY if state exists AND next_review_at <= now
 └─ scheduler.build_review_queue

Assessment persistence (separate channel):
record_assessment → to_notebook_item → upsert_notebook_entries   (learning/assessment.py:234-269)

Per-turn gate reads (tutor loop):
policy.next_objective → pending → due_reviews → probe/practice/assess → complete
policy.is_mastered / is_assessed_mastered / gate_kind / gate_threshold / display_mastery
```

---

*End of survey. Raw per-area writeups: `~/workspace/deeptutor-survey/scratch/02_state.md`, `03_scheduling_assessment.md`, `04_policy_service.md`, `05_capability.md`, `06_fsrs_grep.md`.*
