# LifeKit — Architecture

## System Context

```
+-------------------------------------------------------------+
|                        Swapnil (user)                       |
|                         opens browser                        |
+--------------------------+----------------------------------+
                           | localhost:3000
+--------------------------v----------------------------------+
|                  Next.js production server                   |
|              (feed UI + conversation view)                  |
|                  /api/* rewrites to :8765                    |
+--------------------------+----------------------------------+
                           | proxy
+--------------------------v----------------------------------+
|              Flask feed API (lifekit.serve.server)           |
|              localhost:8765                                  |
|  briefing . completions . idea-signals . conversations CRUD   |
+----------+---------------+---------------+------------------+
           |               |               |
    +------v------+ +------v------+ +------v------+
    |   SQLite    | |  FSRS sched | |  LLM provider|
    |  store      | |             | |  Ollama/OR  |
    |  (WAL)      | |             | |             |
    +-------------+ +-------------+ +-------------+
```

## Pillar Architecture

The system has 8 pillars. P1-P7 are shipped; P8 is proposed.

| Pillar | Name | Technology | Status |
|--------|------|-----------|--------|
| P1 | Book pipeline (intake) | PyMuPDF, Ollama, Pydantic, SQLite | Shipped |
| P2 | Book store & model | SQLite + FTS5 + registry | Shipped |
| P3 | Resurfacing engine | `fsrs` library + daily briefing | Shipped |
| P4 | Coach actions | FastMCP stdio server (7 tools) | Shipped |
| P5 | Retrieval (RAG) | SQLite FTS5 keyword search | Shipped |
| P6 | Grounded chat | Flask endpoint + LLM provider protocol | Shipped |
| P7 | Feed UI | Next.js 16.3.6 (App Router, TS, Tailwind) | Shipped |
| P8 | Program layer | Proposed: sessions, momentum, interviewer | Proposed |

## Data Flow: The Daily Loop

```
User opens feed
    |
    v
GET /api/briefing/today
    |
    v
FSRS scheduler reads completions + idea signals
    |
    v
Briefing assembled (deterministic)
    |
    v
Feed cards rendered
    |
    +-- Mark done -> POST /api/completions
    |
    +-- Still with me -> POST /api/idea-signals
    |
    +-- Talk about this -> open conversation seeded
    |       |
    |       v
    |   GET /api/conversations/:id
    |       |
    |       v
    |   User sends message
    |       |
    |       v
    |   Retrieval: FTS5 query -> grounded context
    |       |
    |       v
    |   LLM phrases reply (prose only)
    |       |
    |       v
    |   Persist turn -> return message
    |
    +-- back to feed (home)
```

**Design rules:**
- No arrow from UI to LLM directly. All prose goes through the chat pillar.
- No arrow from chat to scheduling. Only the FSRS engine decides what resurfaces.
- Signals, not grades. "Still with me" and completions are plain facts.

## Process Architecture

```
lifekit ui (CLI)
    +-- starts Flask feed API on :8765 (localhost)
    +-- starts Next.js production server on :3000 (localhost)
    +-- clean shutdown via SIGTERM/SIGINT

lifekit mcp (CLI)
    +-- starts FastMCP stdio server (7 coach tools)

lifekit config (CLI)
    +-- get/set/show LLM provider config

lifekit split/extract/reduce/validate (CLIs)
    +-- pipeline stages
```

## Deployment Topology

Single process tree on the user's home workstation:

```
home workstation
|-- lifekit ui
|   |-- Flask feed API (:8765)
|   +-- Next.js production server (:3000)
|-- Ollama (qwen3.8:27b-q8_0) -- local GPU
+-- ~/.lifekit/lifekit.db -- SQLite WAL

phone (Tailscale)
+-- browser -> workstation:3000
```
