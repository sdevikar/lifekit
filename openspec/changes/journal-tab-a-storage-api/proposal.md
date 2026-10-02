# Journal Tab A — Storage + API — Proposal

Slice A of the deferred Journal Tab. Storage and transport only — no UI. See
[`../journal-tab/`](../journal-tab/) for the umbrella and the intent note.

## Why

The journal is a new surface with no persistence. Nothing can be built on top
until entries exist in SQLite and can be created, listed, fetched, and updated
over HTTP. Doing this slice alone yields a fully testable backend contract.

## What Changes

- **`lifekit/db/schema.py`** — add a `journal_entries` table in the same
  idempotent-create/migrate path the existing tables use:

  ```sql
  CREATE TABLE journal_entries (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
  );
  ```

  `id` is a caller-supplied string, matching the existing `conversations.id`
  convention. No index needed — entries are few and always read in full.

- **`lifekit/serve/server.py`** — four routes alongside the existing
  conversation routes, same localhost binding and per-request `_conn` pattern:

  | Route | Returns |
  |-------|---------|
  | `GET /api/journal` | recent entries as `{ id, title, updated_at }`, newest first — drives the TOC |
  | `POST /api/journal` | creates an entry from `{ title?, content? }`, returns `{ id }` |
  | `GET /api/journal/<id>` | `{ id, title, content, created_at, updated_at }` |
  | `PUT /api/journal/<id>` | updates `title` and/or `content`, bumps `updated_at`, returns the entry |

  A `PUT` to an unknown id returns 404, not a silent insert.

- **`tests/test_feed_api.py`** — cover the four routes over a temp DB: create
  then fetch round-trip; list ordering is newest-first after an update; `PUT`
  bumps `updated_at`; `PUT` to a missing id is a 404; `POST` without `id`
  generates one.

## Capabilities

### New Capabilities

- `journal-entries`: entries persist in SQLite and are reachable over the
  localhost API. Title is stored verbatim and derived by the caller in slice B.

## Not In Scope

- Any UI — editor, TOC, sidebar, routing. Slice B and C.
- Deletion, search, markdown rendering, title generation.

## Done Criterion

1. `uv run pytest tests/test_feed_api.py -v` passes with the new cases.
2. `uv run pytest tests/ -v` shows no new failures beyond the known
   `test_split_dyl_pdf` (BACKLOG P2).
3. `GET /api/journal` returns `[]` on a fresh DB and is newest-first otherwise.
4. `PUT /api/journal/<unknown>` returns 404.
5. `make lint` passes.
6. `docs/product/STATUS.md` updated in the same change — as *backend only, no
   user-visible surface yet*.