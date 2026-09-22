# Step 13c: Conversation view — tasks

- [ ] 13c.1 Build the conversation screen: "‹ Feed" header + title, message
  list, bottom input
- [ ] 13c.2 Wire load (`GET /api/conversations/:id`) and send
  (`POST /api/conversations/:id/messages`) against the real API
- [ ] 13c.3 Implement card seeding display from `seed_kind`/`seed_ref`
- [ ] 13c.4 Verify the full loop on the dogfood DB: seed → message → grounded
  reply → reload → back to feed → reopen
- [ ] 13c.5 Update `docs/product/STATUS.md`; archive this slice on completion
