# Chat Markdown Rendering — Tasks

- [x] Add the Markdown clause to the `_coach_reply` system prompt in `lifekit/serve/server.py` (bullets for steps/options, bold for the key term, short paragraphs) <!-- id: 0 -->
- [x] `npm install react-markdown remark-gfm` in `frontend/` <!-- id: 1 -->
- [x] `MessageList.tsx` — render coach messages through `react-markdown` with `remark-gfm`; user messages stay the plain `<p className="whitespace-pre-wrap">` <!-- id: 2 -->
- [x] Add `.lk-prose` rules to `frontend/src/app/globals.css` (`ul`/`ol`, `strong`, `code`, `pre`, `blockquote`, headings, links) using the existing `--lk-*` tokens only <!-- id: 3 -->
- [x] Verify: `npm run build` clean (lint's 5 problems are pre-existing — confirmed identical on a stashed tree); a bulleted reply renders as a real `<ul>`, `**bold**` as `<strong>`, and `<script>` / `<img onerror=…>` as escaped visible text — checked by rendering `react-markdown` server-side in node, not in a browser <!-- id: 4 -->
- [ ] User asks the human to eyeball list/code indentation in both light and dark themes in the running app <!-- id: 5 -->
- [x] `uv run pytest tests/ -v` — 116 passed, 1 failed: only the known `test_split_dyl_pdf` (BACKLOG P2) <!-- id: 6 -->
- [x] Update `docs/product/STATUS.md` and move this slice to **Done** in `docs/product/KANBAN.md` <!-- id: 7 -->