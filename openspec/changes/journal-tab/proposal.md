# Journal Tab — Umbrella

**Status: deferred.** Do not implement from this file. It is split into
independently shippable slices below, per `AGENTS.md` ("one slice per proposal").

> **Intent note.** A free-writing journal is not part of the venue described in
> `.agents/intent.md` (today's exercise card, resurfaced idea, fading ideas,
> conversations). It is not a never-build item — it is not a todo list or a
> calendar — but it is a fourth surface. Approving it means amending
> `intent.md` in the same change, not drifting silently.

## Slices

| Slice | Proposal | Depends on |
|-------|----------|-----------|
| A — storage + API | `../journal-tab-a-storage-api/` | — |
| B — editor | `../journal-tab-b-editor/` | A |
| C — TOC + navigation | `../journal-tab-c-toc-navigation/` | B |

## Original scope (kept for reference)

The umbrella as approved in intent: a rich-text journal with auto-save,
auto-generated titles, and a TOC of recent entries in the sidebar panel, backed
by its own SQLite table and API, separate from conversations.

Explicitly out of scope, in any slice: entry deletion, entry search, LLM-generated
titles (first-line truncation until a cheap tasking model exists), image
embedding, mobile/responsive sidebar behavior, the Books tab.

## Open decision carried by slice B

TipTap (`@tiptap/react`, `@tiptap/starter-kit`, `@tiptap/extension-placeholder`)
versus a plain `<textarea>` with Markdown. TipTap buys real WYSIWYG formatting;
it also adds three dependencies to a frontend that currently has zero
component-library dependencies. Slice B must pick one deliberately — it is not
inherited by default.