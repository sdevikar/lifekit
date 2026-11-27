# OpenSpec archives

Finished or retired proposals, kept for history. Nothing here is binding. The
pending proposals are in `../changes/`, and the current plan is
`docs/product/ROADMAP.md`.

Most folders here shipped; `docs/product/KANBAN.md` → Done lists them. The
folders below never shipped in full. The v1 slices replaced them on
2026-11-27. Do not apply them.

| Proposal | Replaced by | Reason |
|----------|-------------|--------|
| `exercise-type-system/` | `card-types-v1` | Typed cards cover exercises and ideas together. OpenUI replaces A2UI. |
| `exercise-surface-routing/` | `feed-v1` | One screen, the feed (ROADMAP D1). |
| `exercise-surface-journal/`, `exercise-surface-tracking/`, `exercise-surface-questionnaire/`, `exercise-surface-concept-check/`, `exercise-surface-worksheet/` | `card-comments` | A comment is the only way to act on a card (D2). Worksheet waits for v2 (D7). |
| `openui-exercise-surfaces/` | `card-generation` | No per-type surfaces. Code builds card programs offline (D6). |
| `openui-hybrid-chat/` (with its `scratch/` notes), `openui-system-prompt/` | `card-comments`, `feed-only-ui` | Shipped in part (commit `6c61732`). Coach replies keep the OpenUI renderer; the free chat goes away (D10). |
| `chat-surface/`, `chat-surface-b-composer-open/`, `chat-surface-c-entry-points/` | `feed-only-ui` | Free chat is retired (D10). |
| `journal-tab/`, `journal-tab-a-storage-api/`, `journal-tab-b-editor/`, `journal-tab-c-toc-navigation/`, `journal-tile-layout/` | `card-comments` | A journal entry is a comment on a reflect card (D2). Posts without a card are v2 (D13). |
| `combine-product-tracking-docs/` | — | Done by hand: KANBAN is the one tracker, and `ROADMAP.md` holds the stages and decision reasons. |

Two more drafts never reached `main`. They live only on the abandoned branch
`feat/card-first-feed`: `card-associated-activity/` and `card-discovery/`
(replaced by `feed-v1` and `card-comments`). `card-activity-drawer/` became
`card-comments` (the drawer is dropped, D1).

The 2026-10-07 chat design (chat as a destination page, a "Recent" list in the
sidebar, no "+" button) shipped. D10 and `feed-only-ui` retire it. It used to sit under KANBAN → Done.
