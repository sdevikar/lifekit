# Algorithms

The math LifeKit uses — and deliberately doesn't. Plain-English version; the borrow rationale lives in [research/lifekit-borrow-report.md](../research/lifekit-borrow-report.md).

## What we use

- **FSRS-style resurfacing (Step 7):** each idea/exercise carries a fading priority; the deterministic runtime picks which previously-seen idea returns today. Adapted from tutor-mcp's FSRS-5: we keep the ranking/scheduling math and drop the flashcard test framing. The user never sees retention percentages, grades, or Again/Hard/Good/Easy — they just get one well-timed old idea in the daily briefing.
- **Embedding dedupe (Step 3):** merges duplicate exercises across chapters so the same practice doesn't appear twice.
- **Chunking:** Chonkie `RecursiveChunker` splits oversized chapters before extraction; sentence-boundary chunking at ingest.

## What we reject

BKT/KT prerequisite graphs (exercises are practices, not prerequisites), learner-as-latent-profile modeling (the user model stays facts-only — completion history, nothing inferred), string-match grading, standalone SM-2 drills, and DeepTutor's pseudo-FSRS scheduler. See the Rejected section of [the roadmap](../product/ROADMAP.md).

## Honest signals

FSRS normally learns from quiz grades; LifeKit has no quizzes. Scheduling signals are: completion, remembered-status ("Still with me"), discussion/revisit, and completion provenance (self-declared vs. assessed). The exact signal set for resurfacing is still an open intent — it needs Swapnil's explicit request before it's drafted.
