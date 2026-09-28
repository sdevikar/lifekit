# LifeKit — Design Decisions & Open Questions

## Decided (binding)

| Decision | Rationale | Source |
|----------|-----------|--------|
| PDF only, text-layer only | Simplicity; scanned PDFs refused | A1, A2 |
| Ollama default, OpenRouter optional | Local-first; no cloud | A5, A21 |
| SQLite + FTS5 | Local; zero-config; WAL | A24 |
| `fsrs` library for scheduling | Real FSRS-5, not hand-rolled | Step 7 spec |
| Next.js for venue UI | Approved framework; component model | A24 |
| Feed + conversations UI | Venue, not menu | Intent |
| No quiz framing | Coach, not tutor | Intent |
| Deep book model, shallow user model | The boundary is hard | Intent |

## Open Questions (blocking)

| # | Question | Blocks | Recommended Action |
|---|----------|--------|-------------------|
| Q1 | **What is the dogfood exit criterion?** | Stage 5 unlock | Define 3-5 measurable criteria; write `docs/product/DOGFOOD-EXIT.md` |
| Q2 | **Evolve `lifekit/mcp/server.py` in place, or second server?** | Stage 5 implementation | Decide when Step 8 is drafted |
| Q3 | **Who is the external coach?** | Step 11 scope | Open question in coaching plan section 6; may reduce Step 11 to "won't build" |
| Q4 | **Book model: one `items` table or per-type?** | Book model finalization | Draft schema migration for human review |
| Q5 | **Mental models coaching feature** | Post-Stage 5? | On the concept pool; not committed |

## Rejected (binding — do not revisit without human approval)

| Rejected | Rationale |
|----------|-----------|
| BKT / IRT / KST | Exercises are practices, not prerequisites; latent-trait inference |
| Knowledge graphs | Against minimal-code; deep book model is enough |
| External app dependencies (Anki bridges) | Against local-first venue |
| Notifications/nudges | Deferred until core loop proven |
| Streak gamification | Plain count only; no guilt language |
| Social features | Single-user local |
| Manual scheduling UI | Deterministic runtime owns scheduling |
| Agent Skills export | LifeKit is an off-the-shelf app, not an agent skill |
| Reflective work in todo lists/calendars | Venue, not menu |
