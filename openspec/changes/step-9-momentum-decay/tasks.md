# Step 9: Momentum decay engine — tasks

- [ ] 9.1 Write `tests/test_momentum.py` first: hand-computed decay fixtures;
  brief-kind priority order (milestone > reactivation > plateau >
  consistency_reframe > value_recall > open_loop); quiet-hours + cap filtering
- [ ] 9.2 Implement `lifekit/momentum/`: decay math, brief engine, nudge
  policy filter
- [ ] 9.3 Schema: `momentum_state` table; wire completion/attempt outcomes into
  momentum updates
- [ ] 9.4 Write the FSRS-over-practices rating mapping design note
  (`concepts/fsrs-practices-rating.md`): how `completed|partial|skipped`
  (+ optional self-grade) map to FSRS ratings
- [ ] 9.5 Wire MCP tools (`get_momentum`, `get_momentum_brief`,
  `get_due_nudges`, `update_nudge_policy`)
- [ ] 9.6 Update ROADMAP.md, STATUS.md, ASSUMPTIONS.md in the same commit;
  archive this change on completion
