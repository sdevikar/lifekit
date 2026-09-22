# Architecture

How LifeKit's pillars connect, and how data flows through them at runtime.

The pillar definitions live in the UI intent
(`../../intent/ui-feed-and-conversations.md`, Pillars section); this page draws
them. The contract behind every arrow: local-first, single user, localhost,
no auth / no cloud / no sync (A24). Deterministic runtime owns scheduling,
surfacing, and state; the LLM owns conversational prose.

## Pillar blocks and connections

```mermaid
flowchart TB
    subgraph P1["1 · Book pipeline (intake)"]
        direction LR
        SPLIT[Chapter splitter]
        EXTRACT[Extractor]
        REDUCE[Reduce / dedupe]
        VALIDATE[Validation harness]
        SPLIT --> EXTRACT --> REDUCE --> VALIDATE
    end

    subgraph P2["2 · Book store & model"]
        DB[(SQLite store)]
        REG[Book registry]
    end

    subgraph P3["3 · Resurfacing engine"]
        FSRS[FSRS scheduler]
        BRIEF[Daily briefing]
        FSRS --> BRIEF
    end

    subgraph P4["4 · Coach actions"]
        TOOLS[MCP tools<br/>list / get / log / next]
    end

    subgraph P5["5 · Retrieval (RAG)"]
        RAG[Chunk + retrieve]
    end

    subgraph P6["6 · Grounded chat"]
        direction LR
        CHAT[Coach conversation]
        LLM[LLM provider<br/>Ollama default]
        CHAT <--> LLM
    end

    subgraph P7["7 · Feed UI (Node.js)"]
        direction LR
        FEED[Feed cards]
        CONVV[Conversation view]
        FEED <--> CONVV
    end

    P8["8 · Program layer (future)<br/>sessions · momentum · interviewer"]

    P1 -->|"validated book (book_id):<br/>chapters · sections · exercises · key ideas"| P2
    P2 <-->|"completions + signals in<br/>briefing out"| P3
    P2 <-->|"read exercises<br/>log completions"| P4
    P2 -->|"book content"| P5
    P5 -->|"grounded context"| P6
    P2 <-->|"conversations table"| P6
    P3 -->|"today's exercise · resurfaced idea · fading ideas"| P7
    P4 <-->|"GET briefing · POST Mark done / Still with me"| P7
    P6 <-->|"open seeded chat · messages"| P7
    P8 -.->|"future reads/writes"| P2
```

Reading notes:

- The **store (2)** is the hub: every pillar reads from or writes to it, and
  nothing talks behind its back. That is what makes the pillars independently
  workable — each one's contract is "this shape in, that shape out" of the store.
- The **UI (7)** never touches scheduling or the LLM directly. It calls the
  briefing (3), the actions (4), and the chat (6) — the deterministic runtime
  owns all decisions.
- **Chat (6)** is a thin surface over retrieval (5) + the LLM: it adds
  conversation state and card seeding, not new knowledge.
- The **pipeline (1)** runs offline, before any of this. It never sees the
  user.

## Data flow: the daily loop

The observable loop from the intent — open feed, do the exercise, Mark done,
talk about it, start a chat, back to feed — wired end to end:

```mermaid
sequenceDiagram
    participant U as Swapnil
    participant UI as Feed UI (Node.js)
    participant ENG as Resurfacing engine (3)
    participant ACT as Coach actions (4)
    participant DB as SQLite store (2)
    participant CH as Grounded chat (6)
    participant RAG as Retrieval (5)
    participant LLM as LLM provider

    U->>UI: opens feed
    UI->>ENG: GET /briefing/today
    ENG->>DB: read completions + idea signals
    DB-->>ENG: history
    ENG-->>UI: today's exercise · resurfaced idea · fading ideas
    UI-->>U: feed cards

    U->>UI: Mark done (exercise card)
    UI->>ACT: POST log_completion(exercise_id)
    ACT->>DB: write completion + provenance

    U->>UI: Still with me (idea card)
    UI->>ACT: POST idea signal(idea_id, remembered)
    ACT->>DB: write signal → feeds FSRS

    U->>UI: Talk about this (card)
    UI->>CH: open conversation seeded on card
    CH->>DB: load conversation + card context

    U->>CH: message
    CH->>RAG: retrieve(query, book_id)
    RAG->>DB: read chunks
    DB-->>RAG: passages
    RAG-->>CH: grounded context
    CH->>LLM: reply with context
    LLM-->>CH: prose
    CH->>DB: persist turn
    CH-->>UI: message
    U->>UI: ‹ Feed (back to home)
```

Design rules the wiring enforces:

- **No arrow from UI to LLM.** The UI never prompts the model directly; all
  prose goes through the chat pillar, which the runtime supervises.
- **No arrow from chat to scheduling.** A conversation can log what the user
  did (via coach actions), but it cannot change what resurfaces — only the
  FSRS engine decides that, from recorded signals.
- **Signals, not grades.** "Still with me" and completions flow into the
  store as plain facts; no probabilities or mastery states ever reach the UI.
