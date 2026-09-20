# LifeKit Philosophy & Tech Stack

**Status:** Draft for review — 2026-09-20
**Replaces:** the three-pillar sketch from 2026-09-19. Correction folded in:
"human-like" does **not** mean deep user modeling — that path would kill the
project. The user model stays deliberately shallow (important facts only);
the modeling investment goes into the **book**.

## Why not "glorified RAG with UI"

RAG retrieves passages. It does not understand the book, and it does not run
a learning loop. Every RAG project converges on the same shape, so retrieval
quality can never be the moat — it is substrate, to be borrowed (BACKLOG
F9–F11), not built. LifeKit's product is the **loop**: understand the book
structurally, surface the right thing at the right time, and be the place
where the user actually does the work.

## Pillars

### 1. Knowledge-first intelligence: deep book model, shallow user model

The intelligence investment goes into understanding the **book**, not the
person. Each book gets a **book model**: summary + structure tree
(parts → chapters → sections) + typed actionable items (exercises, decision
rules, anti-patterns, key ideas) + relations between items (prerequisite-of,
reframes, feeds-into). Think of it as a **code index for books** — symbols
and call graphs, but for ideas and practices. This is what the coach
*reasons over*. RAG answers "what did the book say?"; the book model answers
"what should this person do now?"

The **user model is intentionally shallow**: durable important facts only
(goals, constraints, preferences, what's been tried). No psychological
profiling, no inferred persona — explicitly out of scope. "Human-like" means:
conversational, grounded in the book's structure, remembers the facts that
matter, explains like a coach.

### 2. Venue, not menu

The app is where exercises are **performed**, not browsed. Listing content is
the menu; doing the exercise, reflecting, and being rescheduled is the venue.
Almost no book app is the venue — that is the opening. Consequence: **UI
design is a first-class investment**, not scaffolding. (Streamlit was
scaffolding; the venue needs a real design pass.)

### 3. Algorithmic coaching via a deterministic learning runtime

Surfacing of ideas and lessons is offloaded to a **learning runtime** in the
tutor-mcp shape: the server is deterministic (scheduling state, surfacing
decisions, evidence), the LLM is the generative surface (prose, phrasing).
The runtime never writes canned coaching text — it emits signals +
instructions; the LLM phrases them.

Core mechanics:
- **Decay scheduling** — FSRS over exercises *and* teach-backs (already in
  use for exercises; extend the rating mapping).
- **Feynman teach-backs** — "explain this idea in your own words." The
  explanation is graded (LLM judge against the book model) and the grade maps
  to an FSRS rating (≥0.8 Easy … <0.4 Again), which reschedules the concept.
  This tests *understanding*, which is the point of pillar 1.
- **Motivation briefs** — one angle per surfacing, priority-ordered
  (milestone → reactivation → plateau → value-recall …); signals +
  instruction, never canned text.

Notifications/nudges are **deferred** — revisit only after the core loop is
proven with real use.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Conversational venue (UI)             │
│         chat-first; where exercises are performed        │
└────────────────────────┬────────────────────────────────┘
                         │ MCP tools
┌────────────────────────▼────────────────────────────────┐
│                   Learning runtime (MCP)                 │
│  deterministic: surfacing decisions, FSRS state, briefs, │
│  session/intention lifecycle. LLM owns prose.            │
└───┬──────────────┬───────────────┬──────────────────────┘
    │              │               │
┌───▼────┐   ┌─────▼──────┐   ┌────▼─────────┐
│  Book  │   │ RAG corpus │   │  User facts  │
│ model  │   │ (chunks +  │   │ (durable,    │
│(code   │   │  FTS5 now, │   │  shallow)    │
│ index  │   │  hybrid    │   └──────────────┘
│for the │   │  later)    │
│ book)  │   │ grounding, │
└────────┘   │ citations, │
             │ deep dives │
             └────────────┘
```

- **Book model** — built, not borrowed: nothing off-the-shelf *is* a book
  model. It grows out of the existing extraction pipeline + structuring
  passes (BACKLOG F1 decision rules, F2 anti-patterns, F12 FAQ shape, F14
  auto-tagging, plus a relations pass). No knowledge graph (still rejected).
- **RAG corpus** — substrate for grounding, citations, deep dives.
- **User facts** — start minimal (SQLite table + Markdown mirror, tutor-mcp's
  episodic-memory pattern). No Mem0 until dedup/conflict resolution is a real
  problem.
- **Learning runtime** — new Python MCP server (FastMCP, evolving the
  existing `lifekit/mcp/server.py` or beside it — open question), mirroring
  the tutor-mcp split.

## Tech stack (draft)

| Layer | Choice | Status |
|---|---|---|
| Extraction | PyMuPDF TOC-first → per-chapter Ollama structured extraction → Pydantic → SQLite + FTS5 | Built, eval-conditional-pass |
| Book model | Extraction tables + structuring passes (F1/F2/F12/F14 + relations) | To design |
| Retrieval | FTS5 now; F9 hybrid + rerank later | FTS5 live |
| Scheduling | `fsrs` library over exercises and teach-backs | Live for exercises |
| Learning runtime | Python FastMCP server; tutor-mcp split, srs-mcp tool taxonomy | To design |
| User facts | SQLite + Markdown mirror | To design |
| Venue UI | Chat-first; framework TBD (Streamlit is scaffolding) | To decide |
| LLM | Home Ollama (qwen3.8:27b-q8_0) for extraction/eval; product LLM TBD | — |

## Borrow / build / reject

| Source | Take | Verdict |
|---|---|---|
| tutor-mcp (ArnaudGuiovanna, Go, MIT) | Deterministic-runtime/LLM split; motivation briefs (signals+instruction); Markdown episodic memory; if-then intentions | **Borrow the pattern**, mirror in Python — do not port Go |
| srs-mcp (klutometis, ~200 lines, FSRS MCP) | Minimal "card box + scheduler" tool taxonomy (`due`, `grade`, `suspend`, `stats`) | **Study closely** — closest borrowable shape |
| prometheus learn-retain | Feynman artifact → numeric grade → FSRS rating mapping | **Copy the mapping** for teach-backs |
| lucid / Feynman Reader | Teach-back UX mechanics, misconception diagnosis | Reference for venue UI design |
| book2anki (mdrcs) | Per-chapter checkpoints, depth-aware prompts | Borrow for extraction robustness |
| Mem0 (+ mem0-mcp, Apache-2.0) | Managed memory layer w/ MCP | **Reject for now** — facts-only model doesn't need it |
| BKT / IRT / KST (tutor-mcp's cognitive core) | Mastery modeling, prerequisite graphs | **Reject** — exercises are practices, not prerequisites; FSRS + facts suffices |
| Anki bridges (anki-mcp ×3) | AnkiConnect wrappers | **Reject** — external app dependency, against local-first venue |

## Moat, restated

Not retrieval, not scheduling, not UI polish — all commodity. The moat is the
integration of three things, none defensible alone: the **book model per
book** (structured, relational, quote-grounded — the proprietary layer);
the **venue** (where doing happens, with accrued completion/reflection
history); and the **accrued facts + history** that make leaving costly. The
longer it is used, the more it knows *this* book through *your* practice —
and that compound is not replicable by ChatGPT + a PDF.

## Open questions

1. Venue UI framework: what replaces Streamlit, and when? (Design investment
   is pillar 2 — needs a real decision, not drift.)
2. Learning runtime: evolve `lifekit/mcp/server.py` in place, or a second
   server beside it?
3. Teach-back grading: LLM judge against the book model — which model, and
   what rubric keeps it honest (no grade inflation)?
4. What is the dogfood exit criterion for the core loop? (Needed before any
   F-item or runtime work is unlocked.)
