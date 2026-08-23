# LifeKit: Self-help AI Assistant Bridge Between Consuming Knowledge and Living It

## The Problem
We are consuming more content than ever but applying very little of it. Today's tools fall into two traps: dumb trackers that don't coach, or passive bots without context-aware invitations. LifeKit lives in that gap.

---

## MVP Scope
Current MVP delivers: Book ingestion (EPUB/PDF) -> Ollama-powered SMART plan generation -> SQLite persistence -> MCP tools for task management. Everything else below arrives in Phase 1+.

---

## Architecture
**Core:** FastAPI + SQLite (with FTS5 for semantic search) on localhost running `qwen3.6:latest` via Ollama.
**Frontend (MVP):** OpenWebUI Pipes acting as the gateway to a custom agent logic.
**Frontend (Production):** React/Tailwind SPA in Phase 3 when the algorithm is proven and verified.

---

## Tiered Invocation Logic — Foundational to Everything
Invitations are drawn from different data layers depending on user state:
- **Fresh User** (no interview, no habits yet): Invitations generated purely from knowledge store docs only.
- **Interviewed User** (bio exists + docs in store): Invitations combine interview responses with stored documents.
- **Returning User** (history + bio + docs): Invitations cross-reference exercise history, knowledge store relevance, and behavioral patterns.

---

## Phase 0: Paper Intelligence PoC (~1-2 weeks)

### Step P0-A: The Interviewer
**Deliverable:** `lifekit/core/poc/interviewer.py` — Interactor script that interviews user (goals, habits, time commitments) and saves to SQLite.

```sql
CREATE TABLE user_bios (
    goals TEXT jsonb NOT NULL,
    primary_motivation TEXT,
    habits JSON[] null,
    preferred_checkin_time TEXT,
    weekly_time_budget_minutes INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Testing:** `python core/poc/interviewer.py` on disk. Provide sample inputs. Verify SQLite contains structured bio on disk.

### Step P0-B: Smart Plan Generation (Ollama)  
**Deliverable:** `lifekit/core/plan_forge/forge_plan.py` — Takes user bio + selected book/goal from knowledge store, prompts Ollama (`qwen3.6:latest`) to generate SMART decomposition plan with day-by-day exercises and estimated time commitments.

```json
{
  "weekly_plan": [
    { 
      "task": "Define core modules for knowledge-store schema", 
      "estimated_time": 90, 
      "exercise_type": "planning_session",
      "context_source": "Atomic Habits Chapter 3"
    }
  ]
}
```

**Testing:** Call the script standalone with a mock bio + book selection. Verify Ollama response includes SMART breakdown, actionable next steps, and time allocations.

### Step P0-C: Momentum Tracker (Algorithm only — not visual dashboard)
**Deliverable:** `lifekit/core/momentum_tracker.py` — Core persistence math (decay rates, intervals) that determines task urgency scores 0-1 based on last engagement and completion history.

**Testing:** Write unit tests for three scenarios: day-old goal (low urgency), goal missed 5 days (high urgency -> revival mode triggered), consistent 14-day engagement (longer intervals). Use pytest `assert` on returned scores.

#### Testing Scenarios
Run the pipe into existing OpenWebUI instance. Simulate 2-3 days of check-ins. Verify:
- The system extracts all highlights as individual searchable chunks in `knowledge_store`.
- Highlights auto-linked to goals or topics where relevant (via keyword matching).

---

## Phase 0: Paper Intelligence PoC (continued)

### Step P0-D: Context Injection Layer
**Deliverable:** `lifekit/core/context_injector.py` — Module that runs at the start of every session to set the "thought partner" tone before generating exercises or plans.

```python# Example flow on pipe opening_context = context_injector.fetch_and_format_opening(goal_id=\"goal_1\")
# Returns: "# Context from Atomic Habits Chapter 5\n\n[summary]\n\nAtomic habit is a small behavior...\n\"response = generate_next_exercise(opening_context, user_bio)
```**Testing**: Load sample PDF/EPUB into the knowledge store. Call `context_injector.fetch_and_format_opening(goal_id=...)`. Verify returns relevant content with citations (book title, chapter number). Confirm OpenWebUI shows this opening context before exercises.

#### Step P0-E: Exercise Taxonomy & Logging Schema
**New Architecture Concept - Invite-to-Coach Pattern**:Instead of generating answers/upfront plans via the pipe, LifeKit now generates **invitation bubbles/cards/prompt suggestions** for the user to interact with. When the user clicks or responds to one of these invitations, the system uses the specific exercise type and context to guide the next coaching step (e.g., "explain in your own words..." / "what did you do this week...").

#### Exercise Type Definitions
1. **Concept Check (Feynman Explain):** User explains a concept from books/highlights in their own words. System evaluates understanding and provides clarification/refinement if needed.
2. **Habit Log (Action Logger):** Simple check-in: "Did you do X today?" Tracks completion/no-completion for momentum decay calculation.3. **Daily Journal (Open Reflection):** Unprompted or semi-prompts for user to journal about their progress, feelings, and challenges. System performs `tone_analysis` (e.g., "Stressed", "Productive")4. **Content Digest (Unidirectional Learning):** System presents key content/insights for the user to consume. Logs when user marks as "Read/Consumed". Triggers a quiz or reflection exercise later to evaluate retention.**Deliverable:** `lifekit/core/exercise_types.py` with definitions and schemas for all four exercise types, plus corresponding database logging schema.

```sql-- Stores the specific instance of an exercise (e.g., Atomic Habits Chapter 5 review session)CREATE TABLE exercise_instances (
    id INTEGER PRIMARY KEY, 
    goal_id TEXT REFERENCES goals(id),
    type TEXT CHECK(type IN ('journal', 'feynman', 'action_log', 'content_digest')),    
    intent_id TEXT REFERENCES intents(id), -- Links to invitation bubble that started this session
    context_blob JSON -- Stores the book excerpts/highlights injected for this exercise);-- Stores the user's actual response and progress logCREATE TABLE exercise_logs (
    id INTEGER PRIMARY KEY,   instance_id INTEGER REFERENCES exercise_instances(id),
    "response TEXT", 
    metadata JSON  -- e.g., {"action_completions": ["goal_x"]} or {"quiz_grade": 85}
    tone_analysis TEXT, -- From Daily Journal logs (e.g. "Stressed", "Productive")
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP); 

-- Store the "invitations" (bubbles/suggestions/cards) generated at session startCREATE TABLE intents (
    id INTEGER PRIMARY KEY,  user_id TEXT REFERENCES users(id),
    goal_id TEXT REFERENCES goals(id),
    type TEXT CHECK(type IN ('concept_check', 'habit_log', 'journal', 'content_digest')),
    invitation_text TEXT NOT NULL, -- The text shown as the bubble/card    
    context_snapshot JSON, -- Snapshot of what was injected at creation time
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);-- Stores each exercise session instanceCREATE TABLE exercise_logs (
    id INTEGER PRIMARY KEY,  instance_id INTEGER REFERENCES exercise_instances(id),
    response TEXT, 
    metadata JSON, -- e.g., {"action_completions": ["goal"]}
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);```

### Step P0-F: Full OpenWebUI Integration with "Invite-to-Coach" LogicDeliverable:** `lifekit/poc/full_integration.py` (OpenWebUI pipe script) that now implements the full invite-to-coach flow.
User messages -> Pipe checks `user_bio_exists()` -> Calls interviewer  \nBio found -> **Context Injection fires**: queries the knowledge store, formats relevant content excerpt3. Generates 3 "invitation bubbles" (cards/suggestions) based on intent types (e.g., "[Concept Check] [Log Habit] [Journal]"
4. Displays these with opening context to user in OpenWebUI5. User chooses one -> System starts that specific exercise type and logs it via `exercise_instances`6. Generates coaching response (e.g., "Let's start by having you explain this concept back...\")

**Testing:** Load the pipe into existing OpenWebUI instance. Simulate 2-3 days of check-ins. Verify:
- Interview happens once, context injection fires every time
- Plan/generation updates correctly across sessions
- Invitation bubbles/cards generated properly
- Logging tracks each session/exercise type accurately---

## Phase 1: The Living Core (~3-4 weeks) ### Step P1-A: Knowledge Store Layer**Deliverable:** Standardized parsers for ingestion into SQLite + vector embeddings:  
* `epub_parser.py` — Extract highlights/notes/metadata from epub files
* `pdf_extractor.py` — PDF text extraction via Ollama summarization or `PyPDF2` 
* `youtube_transcript_parser.py` — Download transcript via `pytube` or similar

**Testing:** Run each parser against sample files. Verify it stores structured content (chunks, citations, metadata) in SQLite and generates searchable embeddings for FTS5/FAISS search.### Step P1-B: OpenWebUI MCP Server (Tool Layer)**Deliverable:** `lifekit/mcp/server.py` — Exposes LifeKit capabilities as tools OpenWebUI agents can invoke via Model Context Protocol:- `/momentum_score(goal_id)` -> return urgency score + state  \n- `/checkin(goal_id, result)` -> record progress update with timestamp- `/list_goals()` -> active goals + revival status
- `/search_knowledge(query)` -> retrieve relevant chunks from knowledge store--`/generate_invitations(goal_id, user_bio)` **-> fetch context & return 3-4 invitation bubbles** (uses momentum tracker + knowledge store)- `/format_opening_context(goal_id)` -> fetch + format step P0-D (context injection)**Testing:** Register MCP server in OpenWebUI config. Use agent to call tools directly in chat (e.g., "Show my momentum score"). Verify backend returns accurate data.### Step PAI-C: Momentum Engine Improvements  
**Deliverable:** Enhanced `momentum_tracker.py` with:* Per-goal decay profiles based on user engagement patterns (learned over time)
* Automatic weekly review scheduling based on momentum scores 
* "Warm-up" exercise recommendations for revival-state goals

**Testing:** Write unit tests (pytest):   \n- Test A: Goal engaged daily -> verify interval increases gradually  
- Test B: Goal abandoned for 7 days -> triggers revival and recommends warm-up exercise  
- Test C: User changes time availability during onboarding -> recalculates plan accordingly---

## Phase Directory Layout
- `lifekit/core/` — Interviewer, plan forge, momentum tracker, exercise types/context injection — core logic for PoC
- `lifekit/knowledge-store/` — Parsers for books/media, indexing, search and storage layer- `lifekit/mcp/` — Server-side tool definitions for OpenWebUI pipes
- `lifekit/frontend/` — UI implementation (OpenWebUI pipe first then React later)---

## Timeline Overview
| Phase | Feature | Duration |
|-------|--------|----------|
| P0 | PoC: Interviewer -> Plan Generation -> Context Injection and Exercise Taxonomy | 1-2 weeks |
| P1 | Living Core: Knowledge Store Layer, MCP Server, Momentum Enhancements | 3-4 weeks |
| P2+ | Production: React SPA Dashboard And Full Knowledge Store | TBD (Phase 3+) ---

### **Note:** The Dashboard and UI layer for momentum visualization is built **absolutely last**, only after the algorithm, data model, and all core exercise loops are tested and proven working without visuals. It's Phase 3+ ONLY.
