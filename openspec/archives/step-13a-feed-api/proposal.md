# Step 13a: Feed API — proposal

## Why

The Next.js UI (13b/13c) needs a stable local HTTP contract to build
against. This slice creates it — no UI, just the deterministic backend:
schema + endpoints + tests.

## What changes

- **Schema migration:** `conversations` and `messages` tables per the
  umbrella contract (`../step-13-ui-feed-conversations/proposal.md`).
- **New module** (e.g. `lifekit/serve/`): minimal localhost-only HTTP API
  exposing exactly the umbrella's endpoint list — briefing, completions,
  idea signals, conversations, messages. Reuses the Step 5 coach tools and
  Step 7 scheduler; no new scheduling logic.
- **Chat reply path:** `POST /conversations/:id/messages` retrieves book
  context via the existing retrieval and calls the configured LLM
  (`lifekit/llm/`, Ollama default). The endpoint owns turn structure and
  persistence; the LLM only writes prose.

## Done criterion

1. `pytest` green — new tests cover the migration, every endpoint's happy
   path, and rejection of malformed input.
2. Against the dogfood DB (`~/.lifekit/lifekit.db`, book `dyl`): `GET
   /api/briefing/today` returns a real exercise + idea; POST completions and
   idea-signals persist; a conversation round-trips (create → message →
   reply → reload).
3. API binds `127.0.0.1` only — verified it refuses non-local connections.

## Non-goals

- Any UI (13b/13c). The `lifekit ui` command (13d). RAG upgrades.
