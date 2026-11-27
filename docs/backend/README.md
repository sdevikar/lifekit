# Backend

How LifeKit turns a book PDF into a coaching surface. Built in Steps 1–7 (all
done); see [the tracker](../product/KANBAN.md) for status. The v1 slices 2–4
(`openspec/changes/book-model-v1`, `item-extraction-v2`, `card-generation`)
replace this pipeline with `structure → items → cards`.

## Key docs

- [`../product/ASSUMPTIONS.md`](../product/ASSUMPTIONS.md) — every consequential assumption with ID, status, and revisit trigger
- [`../product/KANBAN.md`](../product/KANBAN.md) — known defects, spec-vs-reality notes, and feature ideas
- [`../integrations/README.md`](../integrations/README.md) — model providers (Ollama/OpenRouter) and config resolution

## Constraints

Single user, local machine, localhost only. No auth, no cloud, no sync. See
[`.agents/intent.md`](../../.agents/intent.md) for the full non-negotiables.
