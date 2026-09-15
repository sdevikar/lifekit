# Step 6: Multi-book — proposal

## Why

LifeKit must support many self-help books, not just DYL. Step 6 adds a
book registry, per-book isolation (exercises don't leak across books),
and cross-book search.

## What Changes

- **Books table** already exists (`books`: id, title, author, file_path).
  Add `register_book(db_path, file_path, title, author) -> book_id` in
  `lifekit/books/registry.py`. Book ID: sha256(file_path)[:16] (matches
  Step 1 default).
- **Isolation**: All queries in Steps 3–5 already filter by `book_id`.
  Add test verifying exercises from book A don't appear in book B's list.
- **Cross-book search**: `search_exercises(db_path, query, book_ids=None)`:
  - If `book_ids` given: search only those books.
  - If None: search all books, but return results grouped by book
    (isolation: caller must opt into cross-book).
  - Implementation: SQLite LIKE on title/purpose (FTS5 is for chunks;
    keep it simple). Or use the existing `book_chunks_fts`? No —
    exercises are the unit. Simple LIKE is fine for MVP.
- **New**: CLI `python -m lifekit.books register --db-path DB --pdf PATH
  [--title T] [--author A]` and `python -m lifekit.books search --db-path DB
  --query Q [--book-id ID]`.

## Capabilities

### New Capabilities

- `multi-book`: registry + isolated per-book queries + opt-in cross-book search.

## Impact

- New package `lifekit/books/` (`registry.py`, `search.py`, `__main__.py`).
- No schema changes (books table exists).
- Uses existing `exercises` table with `book_id` filter.

## Done criterion

1. `tests/test_multibook.py` passes: register creates book; list isolates
   by book_id; search with book_ids filters; search without book_ids
   groups by book.
2. Integration: register 2 synthetic books, add exercises to each,
   verify isolation and cross-book search via CLI.
3. Record; archive; ROADMAP ✅; commit + push.
