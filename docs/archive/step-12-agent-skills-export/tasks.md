# Step 12: Agent Skills export — tasks

- [ ] 12.1 Write `tests/test_skill_export.py` first: valid skill directory
  from fixture tables; refusal on unvalidated book; re-export overwrites;
  frontmatter carries commit + timestamp
- [ ] 12.2 Implement `../../../lifekit/export/skill.py`: SKILL.md, exercises.md,
  key-ideas.md, routines/ generation from extraction/validation tables
- [ ] 12.3 CLI: `lifekit export skill --book <id> --out <dir>`
- [ ] 12.4 Manual acceptance: independent agent session coaches one DYL
  exercise from the exported skill alone (record result in tasks.md)
- [ ] 12.5 Update ../../../docs/product/ROADMAP.md, ../../../docs/product/STATUS.md, ../../../docs/product/ASSUMPTIONS.md in the same commit;
  archive this change on completion
