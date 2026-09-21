# LifeKit learning-mechanism borrow report: tutor-mcp × DeepTutor

**Date:** 2026-09-21
**Method:** read-only source inspection of both repositories. No code run, nothing installed, no LifeKit code touched.

## Sources

| Repo | Commit surveyed | Survey document |
|---|---|---|
| `arnaudguiovanna/tutor-mcp` (Go, MIT) | `221b57e6a1927c8509051322fed531205d2b7ea9` | `TUTOR_MCP_SURVEY.md` (389 lines) |
| `HKUDS/DeepTutor` (Python) | `17b3aaf60c1a7c2fcddbe9936c4c9ec7900650f0` | `DEEPTUTOR_SURVEY.md` (402 lines) |

Every behavioral, default, and threshold claim in the surveys cites `file:line` relative to the repo root. Docs-vs-code divergences are listed explicitly in each survey (7 for tutor-mcp, 16 for DeepTutor); genuinely empty areas are reported as empty, not padded.

## The reframing

tutor-mcp is a real cognitive-science runtime: **BKT + FSRS-5 live** on the update path, with IRT present-but-never-called, PFA retired, and Rasch/Elo removed — despite the changelog advertising "five cognitive algorithms updating the learner model on every interaction." DeepTutor, meanwhile, **implements no standard learning-science algorithm at all**: its scheduler borrows FSRS's vocabulary (stability / difficulty / retrievability, 0.9 retention target) over a custom Leitner-like ladder with static difficulty priors, and its own docstrings say so verbatim ("not a calibrated FSRS fit," `deeptutor/learning/scheduler.py:43-46`).

So the borrow question splits three ways: take the real algorithm (FSRS-5) from tutor-mcp; take architectural patterns (deterministic gating, scheduler seam) from DeepTutor; reject everything that models the learner as a latent psychological profile.

## Language note

tutor-mcp is Go, DeepTutor is Python, LifeKit is Streamlit/Python. Nothing below is a code drop-in. "Borrow as-is" therefore means *take the constants/parameters verbatim*; "Adapt" means *reimplement the mechanism in LifeKit's stack, reshaped to the mission*.

---

## Borrow as-is

**1. FSRS-5 default parameter set** — tutor-mcp `algorithms/fsrs.go`: 19 weights, decay −0.5, desired retention 0.9.
- *Why:* published, fitted defaults from the FSRS research program; re-deriving them is unnecessary work. Constants, not code — zero language friction.
- *LifeKit constraint:* minimal-code ("not a single line of code that wasn't necessary"); deterministic runtime owns scheduling — parameters are data the deterministic scheduler consumes.
- *Flag:* root `intent.md` already makes some FSRS details binding. This borrow must be checked against root intent at intent review, not silently reinterpreted here.

---

## Adapt

**1. FSRS-5 whole-day scheduling adapter** — tutor-mcp `algorithms/fsrs.go`: whole-day intervals (no Anki minute-steps), lapse-stability cap.
- *Why adapt:* LifeKit's rhythm is "one exercise + one idea per day" — day-granularity scheduling is exactly the right shape; minute-level steps are irrelevant.
- *Constraint fit:* deterministic runtime owns scheduling ✓; local-first ✓ (pure arithmetic, no network); facts-only user model ✓ — FSRS state is per-item memory state (difficulty/stability/retrievability *of an idea*), i.e. performance facts, not inferred persona. Keep it to item state; never extend to trait inference.
- *Adaptation note:* FSRS models retrievability of memory items. A Designing Your Life exercise is reflective, not a flashcard — map "recall probability" to "resurface priority" honestly; do not pretend a reflection is a flashcard.

**2. Deterministic gate/policy architecture** — DeepTutor `learning/policy.py`; axiom at `capabilities/mastery/capability.py:38-45`: *"the intelligence lives at the loop's exit… the gate that decides whether the learner may advance is a deterministic engine call."*
- *Why adapt:* this is LifeKit's own constraint verbatim — "deterministic runtime owns scheduling, surfacing, and state; LLM owns conversational prose." DeepTutor proves the shape: `next_objective` precedence (pending → due review → probe/practice/assess → complete) — the gate is the cursor. Learner-override provenance (`"learner"` vs `"system"`) fits the facts-only model: record what happened, not what it means.
- *Adapt the architecture, not the thresholds* — the 0.9 mastery gate and Feynman boolean are ITS-domain-specific.

**3. Staged mastery adjudication** — tutor-mcp: estimated → retained → demonstrated → transferred; challenge eligibility requires retained + non-weak evidence + non-low confidence + non-blocked transfer.
- *Why adapt (narrow):* gives LifeKit a principled answer to "when does an idea stop resurfacing" — staged verdicts instead of a single done-flag.
- *Constraint:* minimal-code — build stage machinery only when an approved intent calls for multi-stage completion. Until then it stays a reference.

---

## Reference only

Patterns to cite in specs, not to build now:

1. **Snapshot-pattern update chain** — tutor-mcp `applyInteraction`: BKT→FSRS read from one read-only snapshot, single write-back, serializable transaction; per-interaction pedagogical snapshots for replay. The correctness pattern for any multi-step learner-state update; the replay log is auditability, which suits spec-first development.
2. **Threshold bascule** — tutor-mcp `REGULATION_THRESHOLD`, default unified 0.85. The *idea* of a single tunable routing threshold is worth keeping; the value 0.85 is domain-specific — do not inherit it.
3. **RetentionScheduler protocol seam** — DeepTutor `learning/scheduler.py`: pluggable scheduler interface so scheduling policy swaps without touching callers. Good spec design for LifeKit's runtime.
4. **Recency-weighted mastery** — DeepTutor `learning/mastery.py`: weighted accuracy over the last ≤5 attempts, weights (0.5, 0.7, 0.85, 0.95, 1.0), confidence caps → ≥3 attempts required to clear the 0.9 gate. A simple, interpretable anti-fluke gate.
5. **KST prerequisite DAG + cycle detection at `init_domain`** — tutor-mcp `algorithms/kst.go`. Relevant only when LifeKit sequences across books; single-book v1 doesn't need it.
6. **Mode system** — DeepTutor `capabilities/mastery/mode.py`: OUTLINE/STUDY/REVIEW with enforcement at call time (turn schemas are assembled once pre-round). A session-mode concept may suit LifeKit's chat-first exercise sessions later.
7. **Local-first persistence discipline** — both repos: SQLite WAL + optimistic CAS on `revision` (DeepTutor `storage.py`); versioned migrations with SHA-256 checksum drift detection (tutor-mcp `db/migrations.go`). LifeKit already keeps `dogfood/lifekit.db` — adopt the migration discipline, not any specific schema.
8. **Forgetting-risk queue** — DeepTutor `scheduler.py:250-262`: `(1−R) + min(overdue/7,0.25) + 0.2·active_error + min(0.1·lapses,0.2)`. Keep as a contrastive reference — what a hand-rolled risk score looks like next to FSRS retrievability. Prefer FSRS.
9. **Frozen-criterion rubric evaluation in exact rationals** — tutor-mcp assessment scoring. Deterministic scoring discipline, if LifeKit ever scores anything.

---

## Reject — deliberately not borrowing

1. **BKT + individualized BKT** — tutor-mcp `algorithms/bkt.go`, `individual_bkt.go`. Latent-trait inference about the learner (per-signal P(Learn)/P(Slip)/P(Guess) deltas). Conflicts with the facts-only user model — no inferred persona. LifeKit exercises aren't right/wrong knowledge components anyway.
2. **IRT 2PL** — tutor-mcp `algorithms/irt.go`. Ability-parameter inference is deep user modeling; also dead on the live path (theta written back unchanged) — nothing to borrow even if we wanted it.
3. **PFA / Rasch-Elo** — tutor-mcp. Retired / removed upstream. Nothing to borrow.
4. **7-stage regulation pipeline** — tutor-mcp (Threshold Resolver → Goal Decomposer → Action Selector → Concept Selector → Gate Controller → Phase Controller → Fade Controller). Built for ITS activity selection across a concept graph. LifeKit is "venue, not menu" plus one exercise a day — over-engineering, violates minimal-code.
5. **Motivation engine** — tutor-mcp (6 brief kinds, 4-axis utility-value rotation, Hidi–Renninger interest phases). Affect/motivation inference; conflicts with the facts-only model; notifications are deferred regardless.
6. **Metacognitive loop** — tutor-mcp (mirror, calibration, autonomy metrics). Learner-modeling surface LifeKit doesn't need. (It is descriptive-only by design — the one modeling component that respects the facts-only line — but still unnecessary.)
7. **Alert engine** — tutor-mcp (FORGETTING at R<0.40/<0.30, ZPD_DRIFT, OVERLOAD, metacognitive alerts). Push-alert machinery; notifications deferred; the resurfacing need is covered by the FSRS-5 adapt.
8. **Tool fleets** — tutor-mcp's 46 MCP tools; DeepTutor's 12 mastery tools. LifeKit is not an MCP ITS and not a tool-driven tutor. Reject the surface; the deterministic-gate idea is already captured under Adapt.
9. **Cron fleet** — tutor-mcp's 8 jobs (olm, consolidation, requeue_stale, motivation, recap, mirror, cleanup, metacog_alerts). Server-side scheduling; LifeKit is local-first with a deterministic runtime. Cadence is covered by the FSRS-5 adapt.
10. **DeepTutor `SpacedRepetitionScheduler`** — `deeptutor/learning/scheduler.py`. Custom FSRS-vocabulary imitation: Leitner-like fixed ladders (MEMORY [0,1,3,7,14,30,60] days, etc.) with static difficulty priors (0.3–0.6) that are never updated. If LifeKit wants spaced repetition, take the real FSRS-5. The schema's difficulty/stability/retrievability columns invite misreading the custom model as FSRS (documented divergence).
11. **DeepTutor string-match grading** — `deeptutor/learning/grading.py` (exact / SequenceMatcher ≥0.85 / keyword ≥60%). Reflective exercises aren't string-match gradable; thresholds would be fake rigor.
12. **DeepTutor SM-2 practice scheduler** — `deeptutor/services/practice/scheduler.py` (ease 2.5→1.3 floor, 365-day cap). The standalone practice feature's cold-start policy. LifeKit has no drill surface.

---

## Suggested next step (no code, per the gates)

If the FSRS-5 adapt is wanted, the next artifact is `intent/<slug>.md` (e.g. `intent/retention-scheduling.md`) scoping: what gets scheduled (ideas? exercises?), what "resurface priority" means for reflective content, and what state the deterministic runtime owns. No spec without approved intent; no code without a spec. The root-intent FSRS binding gets reviewed there — not reinterpreted here.
