# Card Discovery — Hashtags & Semantic Search — Proposal

## Why

With the feed as the single surface, users need a way to find a card they
remember later. Today there is no search. Two candidate mechanisms: hashtags
(tagged at extraction time) and semantic search over card text.

## Open questions (need human decision)

1. Hashtags vs. semantic search vs. both?
2. Where does the search box live if there is no sidebar? (Top of feed? Drawer?)
3. Tagging: LLM-assigned at extraction, or user-assigned?

## Proposed first pass (deferred)

- Add a search input at the top of the feed.
- Backend: extend `search_exercises` (fix empty-list bug D5 first) to also
  match idea text; return card-shaped results.
- Hashtags: reuse F14 (auto-tag by theme) when it ships; until then, keyword
  search only.

## Not In Scope (this change)

- Implementing F14 tagging now.
- Voice/semantic embeddings (F9 hybrid search).

## Done Criterion

1. Search box on feed filters cards by text.
2. Empty results state.