# Step 13a: Feed API — tasks

- [ ] 13a.1 Write `tests/test_feed_api.py` first: migration applies cleanly;
  briefing returns the umbrella's shape; completions + idea-signals persist;
  conversation round-trip (create → message → reply → reload); malformed
  input rejected; binds localhost only
- [ ] 13a.2 Implement the schema migration: `conversations`, `messages`
- [ ] 13a.3 Implement the HTTP API module reusing Step 5 coach tools + Step 7
  scheduler (no new scheduling logic)
- [ ] 13a.4 Implement the chat reply path: existing retrieval + `lifekit/llm`
  for prose; endpoint owns structure and persistence
- [ ] 13a.5 Run the suite; verify all endpoints against the dogfood DB with curl
- [ ] 13a.6 Update `docs/product/STATUS.md`; archive this slice on completion
