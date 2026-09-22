# LifeKit docs

Map of the documentation, organized by domain. Start here.

| Domain | What's in it |
|--------|--------------|
| [product/](product/) | Vision, planning, and standing truth: roadmap, backlog, assumptions, status, philosophy, intents, MVP scope, user manual |
| [ux/](ux/) | UI direction: the feed + conversations interface |
| [backend/](backend/) | Pipeline, storage, and serving: extraction → book model → coach tools → scheduling |
| [arch/](arch/) | Architecture: pillar blocks, connections, and the daily-loop data flow |
| [algorithms/](algorithms/) | The math that picks what resurfaces: FSRS adaptation, dedupe, chunking |
| [integrations/](integrations/) | Model providers (Ollama/OpenRouter) and what's deliberately not integrated |
| [research/](research/) | Landscape surveys and borrow reports (tutor-mcp, DeepTutor) that informed the design |

Change mechanics (not docs, but adjacent):

- [`intent/`](../intent/) — per-change proto-specs. Every change starts as an intent: no spec without an approved intent, no code without a spec. The standing contract is [`intent.md`](../intent.md).
- [`openspec/`](../openspec/) — `changes/<step-slug>/` holds proposal → tasks → implement; finished work moves to `archives/`.

**Docs stay true:** whoever merges a change updates `product/STATUS.md`, `product/ROADMAP.md`, `product/ASSUMPTIONS.md`, and `product/BACKLOG.md` in the same commit.
