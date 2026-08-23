# LIFEKIT: The Bridge Between Consuming Knowledge and Living It

## The Problem

We are consuming more content than ever—books, audiobooks, videos—but applying very little of it. Today's tools fall into one of two traps:

1.  **"Dumb" Trackers:** Habit apps (like Todoist or Notion) track *what* you need to do, but not *how* to think about the process. They offer no coaching.
2.  **Passive Bots:** Generic LLM chatbots give information on demand, but they lack long-term memory and don't know your specific context or goals.

There is a massive gap between "learning something" (consuming a highlight from Chapter 4 of *Atomic Habits*) and "doing something" (actually applying the concept). **LifeKit lives in that gap.**

---

## MVP Scope

**Current MVP delivers:** Book ingestion (PDF) → Ollama-powered SMART plan generation → SQLite persistence → MCP tools for task management. Everything else below arrives in Phase 1.

---

## The Solution: LifeKit

LifeKit is an **Active AI Thought Partner**. 

Unlike a chatbot that waits for you to type, LifeKit knows your library, tracks your effort through scientific algorithms, and actively invites you into specific learning exercises. It bridges the gap between your reading list (books, YouTube, PDFs) and actionable self-improvement using an "Invite-to-Coach" architecture.

---

## How It Works (The User Journey)

LifeKit doesn't start with a blank text box. Every interaction is intentional:

1.  **Context Injection (Tiered Awareness):** When you open the interface, LifeKit layers whatever data is available — no forced baseline:
    *   **Fresh user (no interview, no habits yet):** Invitations are generated purely from books/highlights/documents in your knowledge store. Example: *"Atomic Habits Chapter 3 introduces a principle about small wins. Want to try a concept check on it?"*
    *   **Interviewed user (bio exists + docs in store):** Invitations combine interview responses with stored documents. Example: *"You said you want to build a personal brand AND 'Deep Work' is flagged for review. Shall we start there?"*
    *   **Returning user (history + bio + docs):** Invitations cross-reference exercise history, knowledge store relevance, and behavioral patterns. Example: *"Last session you completed a Feynman exercise on Chapter 3 — the concept needs reinforcement within 3 days to stick."*
2.  LifeKit doesn't ask *"What do you want to do?"* Instead, it says: *"Based on Chapter 3 of Atomic Habits, we haven't reviewed the 'Habit Loop' in 4 days."*
2.  **The Invitations:** You are presented with specific interaction cards (invitations) rather than a long list of chores:
    *   `[Concept Check]` Explain this principle in your own words.
    *   `[Action Log]` Mark today's habit as complete.
    *   `[Journal Prompt]` "How was your day?" vs "What blocked you today?"
3.  **Coach State:** When you click a card, the AI shifts roles. If you selected `[Concept Check]`, LifeKit switches into "Tutor Mode" to evaluate your answer and fill in gaps using its stored knowledge of your books.

---

## The Moat (Why it's better)

*   **Momentum-Based Algorithms:** We don't just track streaks. We use **decay rates**. If you miss a habit, the system automatically scales back your load until you are ready for "warm-up" exercises (Revival Mode), preventing burnout and guilt.
*   **Living Memory:** Connects directly to Kindle, Goodreads, and Libby. It ingests your highlights and automatically generates exercises from them. You don't type; the book is always on the desk.
*   **Structured Learning Taxonomy:** Explicit logic for different interaction types—Feynman technique, guided journaling, and unidirectional learning with spaced repetition—ensures you aren't just "chatting," you are actually retaining knowledge.

---

## Technical Foundation

*   **Frontend (MVP):** OpenWebUI Pipes acting as the gateway to a custom agent logic.
*   **Backend:** FastAPI + SQLite (with FTS5 for semantic search) running the core state machine.
*   **Brain:** Local Ollama integration (`qwen3.6:latest`) for private, low-latency reasoning.

---

## The Vision

LifeKit is the operating system for your second brain. It takes the scattered noise of consumed media and structured thoughts into a cohesive, scientifically-backed path toward personal mastery.

**"Don't just read it. Live it."**