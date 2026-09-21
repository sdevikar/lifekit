# Step 6: Multi-book — tasks

## Tests first

- [ ] `tests/test_multibook.py`:
  - [ ] `register_book` creates row, returns stable id (sha256).
  - [ ] `register_book` idempotent (same file → same id, no dup).
  - [ ] `list_exercises` with book A id does not return book B exercises.
  - [ ] `search_exercises` with `book_ids=[A]` only searches A.
  - [ ] `search_exercises` with no book_ids returns grouped by book.

## Implementation

- [ ] `../../../lifekit/books/registry.py`: `register_book()`.
- [ ] `../../../lifekit/books/search.py`: `search_exercises()`.
- [ ] CLI: `python -m lifekit.books`.

## Done criterion

- [x] All `tests/test_multibook.py` pass (4/4; full suite 39/39).
- [x] Integration: registered 2 books via CLI; search all → grouped by book;
      filtered search (--book-id B for "Alpha" in A) → [] (isolation confirmed).
- [x] Record; archive; ROADMAP ✅; commit + push.

## Test results (2026-09-15)

- `tests/test_multibook.py`: 4/4 passed.
- Full suite: 39/39 passed.
