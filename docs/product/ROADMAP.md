# LifeKit Roadmap — live document

This file is the single source of truth for where the LifeKit build stands.
We work spec-first: each step below is one OpenSpec change under
`../../openspec/changes/<step-slug>/` (proposal → tasks → implement → archive).
Update the status column as steps move.
Assumptions are tracked separately in `ASSUMPTIONS.md` — check there before
challenging a design decision.

## Step 0 — Simplifying assumptions ✅ LOCKED (2026-09-14)

Locked. Not revisited during MVP.

- PDF only. No EPUB, audio, YouTube.
- Text-layer PDFs only — scanned/image PDFs are refused with a clear error, never silently ingested.
- **PDF quality assumption:** PDFs are well-formed and carry an embedded table of contents. The chapter splitter reads the TOC first and falls back to heuristics only when it's missing. Pathological PDFs (corrupt files, no TOC + undetectable headings, exotic layouts) are out of scope for MVP.
- English-language self-help books.
- Single user, local machine, Ollama running (`qwen3.6:latest` or configured model).
- Chapter-detectable books; fixed-size sections as fallback when detection fails.
- Extraction doesn't need to be perfect — misses are fine; systemic failures get flagged, not silently shipped.
- No frontend — CLI + MCP tools are the interface.
- No auth, no cloud, no sync.

## Build sequence

| Step | Feature | Status | OpenSpec change |
|------|---------|--------|-----------------|
| 0 | Simplifying assumptions | ✅ Locked | — |
| 1 | Chapter splitter (TOC-first, heuristic fallback) → `chapters` table | ✅ Done (2026-09-15) | `../../openspec/archives/step-1-chapter-splitter/` |
| 2 | Extraction map: per-chapter Ollama call → strict Pydantic schema (Exercise, KeyIdea) | ✅ Done (2026-09-15, subset validation; full-book eval 2026-09-17 — qwen3.8:27b-q8_0, 17/17 ch, recall 19/20 (95%), conditional pass; see `../../evals/step2-recall-qwen3.8-27b-q8_0/`) | `../../openspec/archives/step-2-extraction-map/` |
| 3 | Reduce/dedupe: merge chapter outputs, embedding-dedupe exercises → `exercises`, `key_ideas` tables | ✅ Done (2026-09-15) | `../../openspec/archives/step-3-reduce-dedupe/` |
| 4 | Validation harness: verbatim-quote grounding check, zero-extraction flags, 10% judge sample | ✅ Done (2026-09-15) | `../../openspec/archives/step-4-validation-harness/` |
| 5 | Coach MCP tools: `list_exercises`, `get_exercise`, `log_completion`, `next_exercise` | ✅ Done (2026-09-15) | `../../openspec/archives/step-5-coach-tools/` |
| 6 | Multi-book: registry, per-book pipelines, cross-book search | ✅ Done (2026-09-15) | `../../openspec/archives/step-6-multi-book/` |
| 7 | Scheduling: FSRS-style spaced repetition over completion history | ✅ Done (2026-09-15) | `../../openspec/archives/step-7-scheduling/` |
| 13 | UI: feed + conversations web UI — daily briefing cards (one exercise, one resurfaced idea, fading list), per-card "Talk about this", master composer, conversation view with back-to-feed; builds on Steps 5 & 7, independent of proposed Steps 8–12 | ⬜ Queued — intent in draft | `../../intent/ui-feed-and-conversations.md` → `../../openspec/changes/step-13-ui-feed-conversations/` (proposal after intent approval) |

Each step ships with its test and done-criterion written before implementation.
Test one step at a time; don't start the next until the current one's done-criterion passes.

## Deferred (not blocking)

- Full-book extraction recall eval against the 20-exercise ground truth — runs on the user's local dev setup with their own model (decision 2026-09-15). Recorded as A20.

## Known issues

See `BACKLOG.md` — the living log of known defects and spec-vs-reality notes (D1/D2 fixed 2026-09-15; D3–D7, H1–H4, P1–P6 open).

## Future roadmap — proposed Steps 8–12 (charted 2026-09-17, NOT committed)

Candidate steps from the coaching plan (`~/workspace/self-help-exercises/lifekit-coaching-plan.md`, based on the tutor-mcp landscape review). Each is one OpenSpec change under `../../openspec/changes/<step-slug>/` — proposals drafted, implementation not started. Suggested build order: **8 → 9 → 10 → 11**.

| Step | Feature | Why this order | OpenSpec proposal |
|------|---------|----------------|-------------------|
| 8 | Coaching session model: durable sessions (planning→in_session→review→closed, server-enforced state machine), session events, Gollwitzer if-then intentions, Markdown session memory | Everything else reads/writes sessions — the foundation | `../../openspec/changes/step-8-coaching-sessions/` |
| 9 | Momentum decay engine: deterministic momentum score (exponential decay over session recency, completion rate, streaks, intention honor rate), motivation-brief engine (priority-ordered brief kinds), nudge policy (quiet hours, daily cap, `get_due_nudges`) | Needs sessions + completion history; feeds every brief | `../../openspec/changes/step-9-momentum-decay/` |
| 10 | User interviewer: scripted 5–7 question elicitation protocol → structured learner profile (`why_matters` feeds momentum's `value_recall` brief); book-goal linking biases exercise selection | Needs a memory profile to write into; personalizes Step 9's briefs | `../../openspec/changes/step-10-user-interviewer/` |
| 11 | Invite-to-coach UI: static-site export (`lifekit export coach-report`) — momentum, intentions, history for an external coach; no hosted service, no auth (per Step 0) | Least validated need — build only after the coach relationship is defined (open question in coaching plan §6) | `../../openspec/changes/step-11-invite-to-coach/` |

**Explicitly later (not in Steps 8–12):** RAG quality upgrade — concrete plan in BACKLOG F9 (hybrid dense+sparse → rerank → answer); F10–F11 chunking upgrades; EPUB / YouTube ingestion.

**Rejected (from the landscape review):** BKT/KST prerequisite graphs (exercises are practices, not prerequisites), multi-tenant SaaS/OAuth/Postgres (Step 0 locks single-user local), canned motivational text (brief engine emits signals + instructions; the LLM phrases), real-time push nudge delivery (polled `get_due_nudges` instead), knowledge-graph store, a second dedupe implementation (adopt the converged two-tier shape if dedupe is revisited), agent-skills export (product direction 2026-09-19: LifeKit is an off-the-shelf app, not an agent skill/harness add-on — borrow backend/UX/how-to ideas only).

## Shipped infra (not numbered MVP steps)

- LLM provider config (2026-09-16): pluggable model backends (`../../lifekit/llm/` — Ollama default, OpenRouter via `OPENROUTER_API_KEY`), layered config (CLI > env > `~/.lifekit/config.json` > defaults), `lifekit config` CLI, portable eval script. Archived spec: `../../openspec/archives/llm-provider-config/`.

## Already shipped (Phase 0 / v0.1.0)

PDF ingestion (pypdf, sentence-boundary chunking, SQLite + FTS5) · Ollama SMART plan forge with Pydantic validation · MCP server (`get_next_task`, `complete_task`, `get_plan_status`). Archived spec: `../../openspec/archives/lifekit-mvp-core-loop/`.
