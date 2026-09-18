# Step 11: Invite-to-coach UI — tasks

- [ ] 11.1 Write `tests/test_coach_report.py` first: fixture learner renders
  correct data; private reflections excluded (adversarial fixtures);
  timestamp label present; opens offline (no external asset references)
- [ ] 11.2 Implement `lifekit/export/coach_report.py`: HTML generation,
  SVG momentum sparkline, goal summary, intentions, exercise history
- [ ] 11.3 CLI: `lifekit export coach-report --goal <id> --out <dir>`
- [ ] 11.4 Add `shareable` flag to `record_attempt` (Step 8) if not already
  present — reflections opt-in per session
- [ ] 11.5 Update ROADMAP.md, STATUS.md, ASSUMPTIONS.md in the same commit;
  archive this change on completion
