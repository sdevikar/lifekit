# Backend

How LifeKit turns a book PDF into a coaching surface. Built in Steps 1–7 (all
done); see [the tracker](../product/KANBAN.md) for the step table and status.

## Key docs

- [`BOOK_MODEL.md`](BOOK_MODEL.md) — the book-model proposal: structure tree + typed items + relations + quote grounding, minimal v1 SQLite schema (awaiting review)
- [`../product/ASSUMPTIONS.md`](../product/ASSUMPTIONS.md) — every consequential assumption with ID, status, and revisit trigger
- [`../product/KANBAN.md`](../product/KANBAN.md) — known defects, spec-vs-reality notes, and feature ideas
- [`../integrations/README.md`](../integrations/README.md) — model providers (Ollama/OpenRouter) and config resolution

## Constraints

Single user, local machine, localhost only. No auth, no cloud, no sync. See
[`.agents/intent.md`](../../.agents/intent.md) for the full non-negotiables.
