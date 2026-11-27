# LifeKit — Data Model & Storage

## Schema Overview

```sql
-- Core tables (shipped)
books(id, title, author, ingested_at, ...)
chapters(id, book_id, idx, title, page_start, page_end, content)
exercises(id, book_id, chapter_idx, chapter_title, title, body,
          source_quote, extra_quotes, created_from, ...)
key_ideas(id, book_id, chapter_idx, chapter_title, title, body,
          source_quote, extra_quotes, ...)
completions(id, exercise_id, completed_at, outcome, provenance, ...)
idea_signals(id, idea_id, signal_type, created_at, ...)
fsrs_cards(id, exercise_id, state_json, ...)
validation_log(id, book_id, exercise_id, check_type, passed, detail, created_at)
dedupe_log(id, kept_id, merged_id, reason, created_at)

-- Step 13a additions (shipped)
conversations(id, book_id, seed_type, seed_id, title, created_at, ...)
messages(id, conversation_id, role, content, created_at, ...)
-- idea_signals column added to completions

-- Proposed Step 5 tables (not built)
sessions(id, book_id, status, started_at, closed_at, ...)
session_events(id, session_id, kind, exercise_id, at, payload_json)
intentions(id, session_id, trigger_text, action_text, scheduled_for, status, resolved_at)
profiles(id, book_id, goal_text, timeframe, ...)
profile_goals(id, profile_id, goal_text, timeframe, obstacles_json, ...)
momentum_state(id, scope_type, scope_id, momentum, streak_days, last_completed_at, decay_rate)
```

## Storage Characteristics

| Property | Value |
|----------|-------|
| Engine | SQLite with WAL mode |
| Location | `~/.lifekit/lifekit.db` |
| Migrations | Versioned, checksum drift detection |
| Backup | File copy (SQLite WAL) |
| FTS5 | Keyword search over exercises + key_ideas |
| Max size | No hard limit; dogfood DB ~156 records |

## Data Retention

- All data is local and persists indefinitely.
- No automatic deletion.
- User can delete the DB file to reset.
- `validation_log` and `dedupe_log` are append-only logs.

## Book Model (Proposed — See docs/backend/BOOK_MODEL.md)

The book model is the proprietary layer: a code index for a book.

| Code index | Book model |
|---|---|
| Module tree | Structure tree: book -> parts -> chapters -> sections |
| Symbols | Typed actionable items: exercises, decision rules, anti-patterns, key ideas, principles |
| Call graph | Relations between items: prerequisite-of, reframes, feeds-into |

**Status:** Draft proposal. Open questions (items table vs per-type, relation set, key-idea typing) are documented in `docs/backend/BOOK_MODEL.md`.
