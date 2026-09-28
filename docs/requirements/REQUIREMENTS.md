# LifeKit — Requirements

## Functional Requirements

### Book Pipeline (FR-PIPE)

| ID | Requirement | Priority | Status |
|----|------------|----------|--------|
| FR-PIPE-01 | System accepts text-layer PDFs with embedded TOC; refuses image-only PDFs with a clear error | Must | Shipped |
| FR-PIPE-02 | Chapter splitter: TOC-first, heading-heuristic fallback, fixed-size final fallback | Must | Shipped |
| FR-PIPE-03 | Per-chapter extraction via Ollama, strict Pydantic schema (Exercise, KeyIdea) | Must | Shipped |
| FR-PIPE-04 | Oversized chapters split via Chonkie RecursiveChunker into per-section extractions | Must | Shipped |
| FR-PIPE-05 | Reduce/dedupe: merge chapter outputs, normalized-title keying, fuller record wins | Must | Shipped |
| FR-PIPE-06 | Validation harness: verbatim-quote grounding (exact-substring with whitespace normalization), zero-extraction flags, 10% judge sample | Must | Shipped |
| FR-PIPE-07 | Every extracted item carries at least 1 verbatim quote; items without quotes are rejected | Must | Shipped |
| FR-PIPE-08 | Multi-book registry with stable IDs; per-book pipelines; cross-book search | Must | Shipped |
| FR-PIPE-09 | Full-book extraction recall eval >= 90% against 20-exercise ground truth | Must | Conditional pass (95%, 19/20) |

### Deterministic Runtime (FR-RUN)

| ID | Requirement | Priority | Status |
|----|------------|----------|--------|
| FR-RUN-01 | Coach tools: list_exercises, get_exercise, log_completion, next_exercise, search_exercises, due_exercises, list_key_ideas, book_progress | Must | Shipped |
| FR-RUN-02 | FSRS-style spaced repetition over completion history; due list ordered | Must | Shipped |
| FR-RUN-03 | Completion is self-declared; no quiz, no grade, no follow-up test | Must | Shipped |
| FR-RUN-04 | Daily briefing: today's exercise, resurfaced idea, fading ideas | Must | Shipped |
| FR-RUN-05 | Idea signals ("Still with me") feed the resurfacing schedule | Must | Shipped |
| FR-RUN-06 | User never sees a number, percentage, or grade | Must | Shipped |
| FR-RUN-07 | Briefing generation is deterministic from completion history; LLM only phrases it | Must | Shipped |

### Venue UI (FR-UI)

| ID | Requirement | Priority | Status |
|----|------------|----------|--------|
| FR-UI-01 | Feed: "Today" header, stage strip, today's-exercise card, resurfaced-idea card, fading-ideas card, conversations list, master composer | Must | Shipped |
| FR-UI-02 | Exercise card: "Mark done" + "Talk about this" | Must | Shipped |
| FR-UI-03 | Resurfaced-idea card: "Still with me" + "Talk about this" + why-it-resurfaced note | Must | Shipped |
| FR-UI-04 | Every card carries "Talk about this", opens conversation seeded on that card | Must | Shipped |
| FR-UI-05 | Conversation view: back-to-feed button, message list, chat input (pinned bottom, optimistic rendering) | Must | Shipped |
| FR-UI-06 | Conversations list on feed; reopen where they left off | Must | Shipped |
| FR-UI-07 | Master composer at bottom of feed opens new conversation | Must | Shipped |
| FR-UI-08 | `lifekit ui` boots feed API (:8765) + Next.js production server (:3000), localhost only | Must | Shipped |
| FR-UI-09 | Visual design: platform.claude.com flat design system | Must | Shipped |

### Program Layer (FR-PROG) — Proposed, gated behind Stage 4

| ID | Requirement | Priority | Status |
|----|------------|----------|--------|
| FR-PROG-01 | Durable coaching sessions: planning, in_session, review, closed; server-enforced state machine | Must (if built) | Proposed |
| FR-PROG-02 | Session events: exercise_presented, attempt_recorded, affect_checkin, brief_shown, reflection | Must (if built) | Proposed |
| FR-PROG-03 | Gollwitzer if-then intentions: pending, honored, missed, cancelled | Must (if built) | Proposed |
| FR-PROG-04 | Markdown session memory alongside DB (inspectable narrative layer) | Must (if built) | Proposed |
| FR-PROG-05 | Momentum score: exponential decay, bumped by completions, penalized by misses | Must (if built) | Proposed |
| FR-PROG-06 | Motivation brief engine: priority-ordered (milestone, reactivation, plateau, consistency_reframe, value_recall, open_loop) | Must (if built) | Proposed |
| FR-PROG-07 | Nudge policy: quiet hours, daily cap, polled get_due_nudges() | Must (if built) | Proposed |
| FR-PROG-08 | User interviewer: scripted 5-7 question elicitation to structured learner profile | Must (if built) | Proposed |
| FR-PROG-09 | Book-goal linking biases exercise selection | Must (if built) | Proposed |
| FR-PROG-10 | Invite-to-coach: static-site export, no hosted service, no auth | Must (if built) | Proposed |

## Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR-01 | **Local-first:** all data on localhost; no network calls except LLM provider | Enforced |
| NFR-02 | **Single user:** no auth, no multi-tenant anything | Enforced |
| NFR-03 | **Minimal code:** smallest diff that satisfies the spec; no speculative generality | Enforced |
| NFR-04 | **Test coverage:** all tests green (currently 112/112); zero tests exercise a real LLM | Enforced |
| NFR-05 | **Portability:** eval scripts use flags, not hardcoded paths; tests skip gracefully when fixtures absent | Enforced |
| NFR-06 | **Determinism:** briefing output is a pure function of completion history | Enforced |
| NFR-07 | **LLM independence:** product works with any provider implementing the protocol (Ollama, OpenRouter) | Enforced |
| NFR-08 | **Recovery:** SQLite WAL mode; versioned migrations with checksum drift detection | Enforced |
| NFR-09 | **Performance:** briefing endpoint responds < 2s on dogfood DB | Target |
| NFR-10 | **Availability:** `lifekit ui` starts both services; clean shutdown via SIGTERM/SIGINT | Enforced |

## Constraints

- **PDF only.** No EPUB, audio, YouTube (A1).
- **Text-layer PDFs only.** Scanned/image PDFs refused (A2).
- **English-language self-help books** (A4).
- **Single user, local machine** (A5, A24).
- **Home Ollama** for long evals; sandbox runs only the eval harness (A22).
- **No auth, no cloud, no sync** (A24).
