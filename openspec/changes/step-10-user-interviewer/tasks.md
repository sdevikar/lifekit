# Step 10: User interviewer — tasks

- [ ] 10.1 Write `tests/test_interviewer.py` first: full protocol → complete
  validated profile; resumability (answer → crash → resume); invalid answers
  rejected; `why_matters` reaches a `value_recall` brief
- [ ] 10.2 Implement `../../../lifekit/interview/`: question protocol, Pydantic
  profile schema, answer validation, resume logic
- [ ] 10.3 Schema: `profiles`, `profile_goals` tables; `link_book_to_goal`
  with scalar relevance boost in `next_coached_exercise` ordering
- [ ] 10.4 Wire MCP tools (`interview_start`, `interview_answer`,
  `link_book_to_goal`)
- [ ] 10.5 Update ../../../docs/product/ROADMAP.md, ../../../docs/product/STATUS.md, ../../../docs/product/ASSUMPTIONS.md in the same commit;
  archive this change on completion
