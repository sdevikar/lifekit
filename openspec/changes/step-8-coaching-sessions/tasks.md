# Step 8: Coaching session model — tasks

- [ ] 8.1 Write `tests/test_sessions.py` first: open → attempt → close happy
  path; attempt rejected outside `in_session`; intention lifecycle
  pending→honored/missed/cancelled; Markdown note written with YAML frontmatter
- [ ] 8.2 Implement schema migration: `sessions`, `session_events`,
  `intentions` tables
- [ ] 8.3 Implement `../../../lifekit/sessions/` — session state machine
  (planning→in_session→review→closed, server-enforced), event logging,
  intention lifecycle, Markdown memory writer
- [ ] 8.4 Wire MCP tools (`start_coaching_session`, `get_coaching_context`,
  `next_coached_exercise`, `record_attempt`, `end_coaching_session`,
  `list_intentions`, `resolve_intention`) into `../../../lifekit/mcp/server.py`
  (also resolves BACKLOG H1 for the Step 5 tools)
- [ ] 8.5 CLI: `lifekit session start/end`
- [ ] 8.6 Update ../../../docs/product/ROADMAP.md, ../../../docs/product/STATUS.md, ../../../docs/product/ASSUMPTIONS.md in the same commit;
  archive this change on completion
