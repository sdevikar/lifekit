# Algorithms

The math LifeKit uses — and deliberately doesn't. Plain-English version; the
borrow rationale lives in
[research/lifekit-borrow-report.md](../research/lifekit-borrow-report.md).

## What we use

- **FSRS-style resurfacing (Step 7):** each idea/exercise carries a fading
  priority; the deterministic runtime picks which previously-seen idea returns
  today. Adapted from tutor-mcp's FSRS-5: we keep the ranking/scheduling math
  and drop the flashcard test framing. The user never sees retention
  percentages, grades, or Again/Hard/Good/Easy — they just get one well-timed
  old idea in the daily briefing.
- **Title dedupe (Step 3):** merges exercises whose normalized titles match,
  so the same practice does not appear twice. It compares titles only, so
  many repeats get through (KANBAN → v1 problem). `item-extraction-v2`
  replaces it with per-chapter consolidation.
- **Chunking:** Chonkie `RecursiveChunker` splits oversized chapters before
  extraction; sentence-boundary chunking at ingest.

## What we reject

See the borrow/reject table in
[research/lifekit-borrow-report.md](../research/lifekit-borrow-report.md).
BKT/KST prerequisite graphs, learner-as-latent-profile modeling, string-match
grading, standalone SM-2 drills, and DeepTutor's pseudo-FSRS scheduler are all
rejected.

## Honest signals

FSRS normally learns from quiz grades; LifeKit has no quizzes. Scheduling
signals are: completion, remembered-status ("Still with me"),
discussion/revisit, and completion provenance (self-declared vs. assessed).
The exact signal set for resurfacing is still an open intent — it needs
Swapnil's explicit request before it's drafted.
