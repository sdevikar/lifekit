# DeepTutor Docs Review — for the LifeKit borrow assessment

Date: 2026-09-21. Reviewer: subagent (docs-level, not code-level).
Commit surveyed at code level (separately, by another pass): `17b3aaf60c1a7c2fcddbe9936c4c9ec7900650f0` of `HKUDS/DeepTutor`.

## Important caveat on coverage

Only three docs pages were successfully read before the browser-fetch tool failed for the session:

1. `https://docs.deeptutor.info/` (docs index)
2. `https://docs.deeptutor.info/explore/chat-workspace/` (Home)
3. `https://docs.deeptutor.info/explore/mastery-path/` (Mastery Path)

The following were **not** read and are flagged as gaps, not findings: the Books page itself, Immersive Reading, Partners detail, Co-Writer, Knowledge Center, Learning Space, Memory, Settings, Get Started, Ecosystem, Providers, CLI, pricing/FAQ/API pages. Where this report goes beyond the three pages, the source is the prior **code-level survey** of the repo, and it is explicitly labeled as such. Nothing below invents docs content that was not read.

## 1. What DeepTutor is and who it's for

From the docs index, verbatim positioning: "DeepTutor is an open-source, agent-native learning companion. A shared runtime powers Chat, deeper capabilities, Partners, Book generation, Co-Writer editing, RAG, and three-layer Memory. Partners carry the same chat agent loop into IM channels while keeping their own soul, library, tools, and workspace."

It is built at the HKU Data Intelligence Lab and licensed Apache 2.0. The target user is a self-directed learner who wants an AI study companion across many surfaces: chat, structured study paths, reading, writing, and messaging apps. It is a *learning platform* in the broad sense — tutoring, quizzing, research, video watching, document editing — not a coach, not a habit app, not a journaling app.

## 2. The book section

The docs index lists the product journey as: Home → Partners → Mastery Path → Immersive Reading → Books → My Agents → Co-Writer → Knowledge Center → Learning Space → Memory → Settings. The Books page itself was not readable in this pass, so the following is assembled from the three pages that were read:

- Books are compiled artifacts ("a compiled book, a reading section") that can be attached as one-time context (`+` menu) in any conversation.
- In Mastery Path, a study route is grounded in **Books, Notebooks, or selected Knowledge Base files** — the book is source material the deterministic study machinery operates over, not the experience itself.
- "Book generation" is listed as a runtime capability on the index, implying books can be authored/generated in-app, not only uploaded — but the upload/import mechanics were not verified in this pass.

Day-to-day learner flow (docs-verified for Mastery Path): pick a goal → bind materials (books/notebooks/KB files) → edit the generated outline of modules and typed knowledge points → study one waypoint at a time in Outline/Study/Review modes, answering posed questions in a chat transcript → pass the assessed mastery gate (or explicitly self-declare mastery) → completed points come back later via spaced review.

## 3. Overlap with the LifeKit vision

("Every day, one exercise to do and one idea to remember" — deterministic runtime + LLM conversation, deep book model, facts-only user model, chat-first, local-first, no deep personalization, notifications deferred.)

Genuine overlaps (docs-verified):

- **Deterministic engine owns advancement; LLM owns pedagogy.** The Mastery Path docs say "the assessed mastery gate controls progression" and that "progress records assessed mastery or an explicit learner declaration, rather than time spent reading." This is the same architectural split LifeKit wants: a deterministic gate decides advancement; the LLM tutors within the bounds.
- **Typed knowledge points as the unit of book modeling.** Each knowledge point is typed as memory, procedure, concept, or design, and "that type changes what evidence counts as mastery and lets the tutor choose an appropriate learning activity." This is a deep-book-model idea LifeKit could learn from — content typed by what it demands of the learner.
- **Spaced review of completed items.** "Completed points return later through spaced review when they are due." A resurface mechanism exists, though it is point-mastery-shaped, not reflection-shaped.
- **Knowledge grounding.** A large RAG story (LlamaIndex, GraphRAG, LightRAG, PageIndex, Obsidian, MarginNote 4, Tencent IMA) for grounding answers in the learner's own library — same "RAG for reference and grounding" role LifeKit envisions.
- **Chat-first surface.** Home is "the default agent loop" and study sessions are "an ordinary DeepTutor conversation bound to a Mastery Path."

Partial / superficial overlaps:

- **Daily rhythm.** There is no "one exercise + one idea per day" product in what was read. There is a `cron` tool ("quiz me on this chapter every weekday at 9 is a sentence, not a setup screen"), but scheduling is learner-initiated, not a coach that shows up with today's exercise and idea.
- **Reflection-shaped content.** Knowledge points are ability-building units (memorize a fact, learn a procedure, grasp a concept). Nothing in the pages read treats book content as reflective exercises, prompts, or practices to *do in your life*.
- **Local-first.** Docs lead with PyPI / From Source / Docker install paths, so self-hosting is real, but the docs also describe server/Docker deployments and a hosted PageIndex Cloud option — "local-first" as a product principle is not claimed in what was read.

## 4. Integrations

Docs-index-verified:

- **IM channels (Partners & Channels):** WeChat, WeCom, QQ/NapCat, "and other IM channels." Partners are "persistent learning companions" that "carry the same chat agent loop into IM channels while keeping their own soul, library, tools, and workspace." Load-bearing for a "companion that reaches you where you are" story; nice-to-have for LifeKit while notifications are deferred.
- **Ecosystem:** Skills, MCP Services, CLI Apps, RAG integrations, and EduHub. MCP services are listed but not detailed on the pages read.
- **Knowledge/RAG integrations:** LlamaIndex, GraphRAG, LightRAG (local, server, remote), PageIndex OSS/Cloud, Obsidian vaults, MarginNote 4, Tencent IMA. These are the load-bearing ones for the "deep book model" story — the system meets the learner's existing library.
- **Media:** YouTube (Immersive Watching with transcript-grounded tutoring), image/video generation tools (once a generation model is configured), GeoGebra, Manim/visualizers.
- **Providers:** pluggable LLM, embedding, and search providers, plus per-turn model switching in chat.
- **CLI:** a full terminal interface (capabilities, KBs, sessions, notebooks, memory, books, partners).

(Code-survey note, not docs-verified in this pass: the repo also wires these into a large tool/MCP fleet. Treat integration-count claims as code-derived.)

## 5. Pricing, availability, open-source posture

No pricing page, plans page, or hosted-SaaS offer was found in the pages read. What the docs do say:

- Apache 2.0, open source, GitHub repo public, Discord + GitHub Discussions + issue tracker as support channels.
- Get Started offers **PyPI, From Source, Docker, and CLI-Only** install paths — i.e., you run it yourself.
- Mentions of "server deployments," a "self-hosted Invidious origin," and "PageIndex Cloud" imply hosted components exist around the edges, but no hosted DeepTutor product with pricing was documented on the pages read.

Net: the docs story is self-hosted open source, not SaaS. (Unverified: whether any hosted offering or pricing exists elsewhere on the site.)

## 6. Differentiation opportunities — where DeepTutor does not go

Based strictly on the three pages read:

- **No accountability.** Partners are "persistent learning companions" — tutors that live in your IM app — not accountability partners. Nothing in the docs talks about commitments, follow-through, streaks, or holding the learner to their intentions.
- **No reflection or journaling.** The entire practice vocabulary is quiz/exam/mastery/review. Knowledge points are things to *master* (memory, procedure, concept, design), not prompts to *reflect on* or practices to *do*. LifeKit's core unit — the exercise extracted from a self-help book — has no counterpart in what was read.
- **No reading-life integration.** Books are study material to be mastered; there is no concept of carrying an idea into your day, noticing it in your life, or reporting back on lived practice.
- **Deep user modeling, not facts-only.** The docs describe "three-layer Memory," "personalization" managed in Learning Space, personas (peer, research-assistant, teacher), and starting-point suggestions "drawn from your own history — the L3 memory synthesis plus your last several activities across surfaces." That is the opposite of LifeKit's facts-only, no-deep-personalization line — and a clean differentiator.
- **Breadth over depth of ritual.** DeepTutor is a wide workbench (research, video watching, document co-writing, quizzes, coding via `exec`, image generation). LifeKit's "venue, not menu" — one exercise, one idea, daily — is a deliberate rejection of exactly this breadth.
- **No notification/deferral posture stated.** The `cron` tool can push scheduled quizzes, and Partner jobs "ride back out through the IM channel" — proactive nudging exists as a mechanism, but it is generic scheduling, not a coaching relationship.

## 7. What the docs confirm, qualify, or leave open vs. the code survey

- **Confirmed:** deterministic gating of advancement (mastery gate), spaced review, LLM-as-tutor within a bounded study loop, typed knowledge points, book-as-source-material. The docs are consistent with the code survey's "deterministic engine + LLM pedagogy" characterization.
- **Qualified / new nuance:** progression is not purely assessed — "a learner may explicitly mark a point mastered, with that source distinguished from assessment." The system tracks *provenance* of mastery (assessed vs. self-declared). That is a design detail LifeKit should note: completion provenance matters, and DeepTutor already distinguishes "the test said so" from "the learner said so."
- **Qualified:** the code survey said learner identity is effectively tied to `path_id` with "no deep learner profile." The docs describe three-layer Memory, L3 memory synthesis, and personalization in Learning Space — at the product level, DeepTutor *does* present a persistent, cross-surface learner memory. The code-level claim may describe the study subsystem specifically; the product story is broader. Do not cite "no learner profile" as a DeepTutor fact without reconciling this.
- **Not contradicted:** nothing in the pages read claims real FSRS/BKT/IRT fitting; the scheduling is described behaviorally (spaced review "when they are due"), which is consistent with the code survey's custom-ladder finding. But the algorithm question was not addressed on these pages at all — the docs simply don't discuss scheduling math.
- **Open (unread):** Books page mechanics, Partners setup depth, Memory architecture, Co-Writer, pricing/FAQ/API, self-hosting vs. hosted details, MCP services catalog.

## Bottom line for the LifeKit borrow decision

Borrow-worthy ideas (docs-evidenced): the deterministic-gate + LLM-tutor split; typed knowledge points (type changes what counts as mastery); completion provenance (assessed vs. declared); the `+`-menu pattern for attaching book material as one-time context; the RAG-meets-your-library posture.

Not borrow-worthy: the breadth (research/video/coding/image-gen workbench); the deep learner memory and personalization; the quiz/exam framing; the IM-companion-as-tutor model.

The single biggest differentiation: DeepTutor helps you *master material*; LifeKit would help you *practice a book in your life*. Nothing in the docs read suggests DeepTutor touches reflection, lived practice, or accountability — that space is empty in their product story as documented.

---

# Part 2 (continued)

# DeepTutor docs review — Part 2 (partial: tool blocked mid-pass)

**Status:** In this pass I docs-read: index, Get Started, chat-workspace (Home), Partners, Memory.
**Blocked/gap:** Books page, Co-Writer, Learning Space, Knowledge Center, Immersive Reading,
My Agents, Partners & Channels setup guides, FAQ/pricing/API/MCP catalog pages, and the /explore/
landing (redirects to chat-workspace) were NOT docs-read — the page-fetch tool failed for the
remainder of this session. Retry planned next session.
Book details below are from GitHub release notes/README (labeled as such), NOT the docs Books page.

---

## 1. Docs index (docs-read: https://docs.deeptutor.info/)

> "DeepTutor is an open-source, agent-native learning companion. A shared runtime powers Chat,
> deeper capabilities, Partners, Book generation, Co-Writer editing, RAG, and three-layer Memory.
> Partners carry the same chat agent loop into IM channels while keeping their own soul, library,
> tools, and workspace."
> "Built at HKU Data Intelligence Lab. Apache 2.0 license."

Nav: Get Started (PyPI / From Source / Docker / CLI-Only), Explore DeepTutor, DeepTutor Ecosystem
(Skills, MCP Services, CLI Apps, RAG integrations, EduHub), Partners & Channels (WeChat, WeCom,
QQ/NapCat, other IM), DeepTutor CLI, Providers (LLM, embedding, search). Support: Discord, GitHub
Discussions, issue tracker. Docs note the canonical agent-handover doc is SKILL.md on GitHub.

**Explore journey order (from index):** Home → Partners → Mastery Path → Immersive Reading →
Books → My Agents → Co-Writer → Knowledge Center → Learning Space → Memory → Settings.

## 2. Get Started (docs-read: https://docs.deeptutor.info/get-started/)

- Four install paths, all sharing one workspace layout: "settings live in `data/user/settings/`
  under the directory you launch from ... Knowledge bases, memory, Partner runtime state,
  multi-user accounts, and audit logs also live under the same `data/` tree, so deployments only
  need to persist that tree."
- "For the full app, the recommended flow is **pick a workspace directory → install →
  `deeptutor init` → `deeptutor start`**."
- After start, two local services: FastAPI backend on 8001, Next.js frontend on 3782.
- "You'll also need an **LLM provider**. Hosted services usually require an API key; local
  providers such as Ollama, LM Studio, llama.cpp, and vLLM can run without one."
- **Multi-User Deployment** page exists ("host DeepTutor for a team") — self-hosted story,
  no hosted SaaS offer anywhere on the pages read. No pricing page found in nav.
- **Open item (a) — hosted/paid offering:** no evidence of any. All deployment docs are
  self-hosted (PyPI/source/Docker/CLI). PageIndex Cloud is mentioned only as a *retrieval*
  option for knowledge bases (see Home page), not as a DeepTutor hosting product. Status:
  docs-read confirms self-hosted-only story; pricing page: gap (not found in nav read so far).

## 3. Home / chat-workspace (docs-read: https://docs.deeptutor.info/explore/chat-workspace/)

- "Home is the heart of DeepTutor. It is not a plain message box: it is the **default agent loop**
  that can call tools, read your sources, search knowledge bases, write notes, generate images,
  consult other agents, ask you clarifying questions, and switch into deeper capabilities — all
  inside one thread."
- Starting points: "three lines drawn from your own history — the L3 memory synthesis plus your
  last several activities across surfaces — each proposing a specific thing to understand rather
  than a way to revisit what you already did."
- Capabilities: Chat, Ask Questions, Quiz, Visualize, Immersive Watching, Research, Solve;
  **Mastery Path** and **Immersive Reading** are workspaces under **Personalized Learning**,
  alongside Books and Practice.
- The `+` menu (one-time context): "A compiled book, a reading section, a saved notebook, or
  practice material from your Learning Space."
- `cron` tool (docs-read, this page): "`cron` lets a turn schedule work instead of doing it now:
  **at** a time, **every** N seconds, or on a **cron expression** with a timezone. When the job is
  due, its message runs as a new instruction **in this same conversation** and the reply lands
  here — so 'quiz me on this chapter every weekday at 9' is a sentence, not a setup screen. The
  same tool lists this conversation's jobs and cancels one. For a Partner, a due job rides back
  out through the IM channel the partner is connected to."
- **Open item (e) — cron/proactive features:** the ONLY proactive mechanism documented is this
  generic `cron` tool — learner-authored scheduled prompts, no coaching-style nudges, no
  accountability/reminder product. Confirmed docs-read on this page.
- RAG engines named: LlamaIndex, GraphRAG, LightRAG (local/server/remote), PageIndex OSS and
  PageIndex Cloud, Obsidian vaults, MarginNote 4, Tencent IMA. ("PageIndex OSS and PageIndex
  Cloud are not [served by the rag tool]: their retrieval is agentic, so a reading loop walks
  the local or hosted document tree instead.")
- Personas: "built-ins like **peer**, **research-assistant**, and **teacher** change tone and
  pedagogy."

## 4. Partners (docs-read: https://docs.deeptutor.info/explore/partners/)

- "Partners are persistent companions with their own identity, soul, model policy, library,
  memory, and channel configuration. ... A Partner is 'a chat that has a personality and a
  phone number.'"
- "every inbound message — from the web or from an IM app — is routed through the **same**
  `ChatOrchestrator → AgenticChatPipeline` loop that powers Home."
- "Because a partner has memory, it builds up a picture of you over time. Ask it 'what do you
  know about me?' and you'll see a `Recalling memory` step — the partner reads its own memory
  layers before answering in its soul."
- Memory scoping: "the Partner reads and writes private relationship memory under
  `users/<user_id>/workspace/memory/`, and can read that interacting user's own shared memory."
- Channel setup: "Channels are delivery adapters around the same partner brain." Get Started
  lists: "connect autonomous tutors to WeChat, WeCom, QQ, Telegram, Slack, Feishu, and more";
  Partners page points to a Channel Matrix with WeChat, WeCom, QQ/NapCat guides. Per-channel
  cards (base URLs, tokens, polling), QR-backed onboarding (WeChat/WeCom/WhatsApp bridge),
  allowlists ("Allow From"), "Send Progress" narration switches.
- **Accountability check:** nothing about commitments, follow-through, streaks, habits, or
  checking whether the learner did something in real life. Partners = tutors in your IM app.
  Confirmed absent on this page (docs-read).

## 5. Memory (docs-read: https://docs.deeptutor.info/explore/memory/)

- "Memory is DeepTutor's **inspectable** personalization system. It is deliberately *not* a hidden
  vector store — it is a three-layer pipeline you can read, curate, and audit."
- Layers (docs-read table):
  - **L1 · Workspace mirror** (LIVE): "Current entities on each surface. Refresh stores
    fingerprints, labels, `last_refresh`, and append-only changes."
  - **L2 · Per-surface summaries** (CURATED): "Surface facts extracted from live L1 entities,
    citing the entities behind them."
  - **L3 · Cross-surface synthesis** (SYNTHESIS): "Update and Audit synthesize profile, recent,
    and scope from L2. Chat writes Preferences only through `write_memory`."
- Surfaces spanned: "Memory spans `chat`, `notebook`, `quiz`, `kb`, `book`, partner, and
  `cowriter`."
- Memory Graph: "places the automatically synthesized L3 slots — profile, recent, and scope —
  at the centre, L2 facts in the middle, and live L1 entities outside."
- "Keep memory on for long-running learning workflows — that's when it pays off."
- Multi-user: "each user gets scoped memory under their own workspace; a partner reads its own
  memory and its owner's, but only writes its own."
- **Open item (c) — three-layer memory vs facts-only:** CONFIRMED opposite. DeepTutor
  explicitly builds a synthesized learner profile ("L3 slots — profile, recent, and scope") from
  activity across chat, notebooks, quizzes, KBs, books, partners, and co-writer, and feeds it
  into the composer's starting points and the partner's answers. This is deep learner modeling
  as a product feature — the direct opposite of LifeKit's facts-only line. Reconciles the
  earlier tension: the code survey's "no deep learner profile" described only the study
  subsystem; at product level, persistent cross-surface memory is real and documented.
  (Granularity caveat from docs: "current L3 citations usually name an entire L2 surface" —
  soft links, not exact chains.)

## 6. Book (NOT docs-read — from GitHub release notes + README, labeled as such)

Docs Books page was not readable this session. From HKUDS/DeepTutor release notes
(ver1-2-0, ver1-5-13) and README (source: web search, not docs-read):
- "Book turns selected sources into an interactive **living book** — not a static PDF, but a
  reading environment built from typed blocks."
- "A book can start from knowledge bases, notebooks, question banks, or chat history; the
  creation flow proposes a chapter outline before content is generated, so you review the shape
  instead of accepting a blind one-shot output." → **how books get in: generated from your
  materials, not uploaded as books.** (Docs-page confirmation still needed.)
- Five-stage pipeline: Ideation → Source exploration (RAG) → Spine synthesis (Spine → Chapter →
  Page) → Page planning (typed blocks) → Block compilation.
- Block types: "text, callouts, quizzes, flash cards, timelines, code, figures, interactive
  HTML, animations, concept graphs, deep dives, and user notes — with its own Page Chat."
- "Progress, bookmarks, quiz attempts, captures, and Page Chat stay private per reader";
  "visited pages, bookmarks, and quiz attempts now roll up into a completion score and a list
  of weak chapters"; export to self-contained Markdown; `deeptutor book health` /
  `refresh-fingerprints` flag source drift.
- Books connect to Mastery Path as bound source material; the chat `+` menu attaches "a
  compiled book" as one-time context.
- **Framing check:** everything is mastery/quiz/completion vocabulary — no reflection,
  journaling, or lived-practice concepts in these materials either (pending docs-page check).

## 7. Open items status

- (a) Hosted SaaS / paid offering: **no evidence found** in docs-read pages. Self-hosted only
  (PyPI/source/Docker/CLI), multi-user = self-hosted team deployment. Pricing page: not found
  (gap — may not exist).
- (b) How books get created/imported: **partial** — generated from KBs/notebooks/question
  banks/chat history via multi-agent pipeline (release-notes-sourced); docs-page confirmation
  pending.
- (c) Three-layer memory: **confirmed docs-read**, and it IS the opposite of facts-only
  (synthesized profile/recent/scope/preferences across 7 surfaces, fed into chat + partners).
- (d) Reflection / journaling / habits / accountability / real-life practice: **confirmed
  absent** on all docs-read pages (Home, Partners, Memory, Get Started, index). Practice
  vocabulary throughout is quiz/exam/mastery/review. No commitments, streaks, or
  follow-through features documented.
- (e) cron/proactive: **confirmed docs-read** — only the generic `cron` tool
  (learner-authored scheduled prompts); no coaching nudges.

## 8. Tightened differentiation (pending final confirmation of gap pages)

**DeepTutor helps you *master material*; LifeKit helps you *practice a book in your life*.**
DeepTutor's loop is: bind sources → get tutored/quizzed → pass deterministic mastery gates →
spaced review — with deep, inspectable learner memory personalizing everything. LifeKit's loop
is: one idea to remember + one exercise to do, every day, from a book you're living through —
with a deterministic runtime deciding what surfaces, an LLM holding the conversation, a deep
model of the *book* instead of the *person*, and a facts-only user model as a matter of
principle. Overlap is real (deterministic-gate + LLM-tutor split, typed knowledge units,
spaced resurfacing, RAG grounding, chat-first) but the product jobs differ: tutor vs. coach,
mastery vs. practice, personalization vs. restraint, workbench breadth vs. daily ritual.
Nothing docs-read touches reflection, lived practice, or accountability — that space is empty
in DeepTutor's documented product story.

---

## Addendum — Atlas follow-up reads (2026-09-21, same day)

Docs pages fully read this session: **Immersive Reading** (`/explore/reading/`), **Home** (`/explore/chat-workspace/`, full 289 lines), **Partners** (`/explore/partners/`, full page). The **Books** docs page fetch failed again with a tool-level failure (not a 404); Book content below is GitHub-sourced (README + v1.5.13/v1.2.0 release notes), labeled as such.

### Immersive Reading (docs-read, verbatim quotes)
- "Immersive Reading puts the document and conversation side by side. The assistant reads the **same units you see** — a PDF page, EPUB chapter, slide, or extracted section — so an answer can carry a source locator."
- "It is a capability, not a separate app: everything Chat can do still works in a reading turn."
- Materials: PDF, EPUB, Word, spreadsheet, slide, Markdown, text, HTML, audio, video, web/YouTube/Bilibili links; 200 MB per document; scanned image-only docs rejected.
- Markup: select-to-highlight/underlne with notes (five colors, two styles); export as **Annotated PDF** (real PDF annotations) or **Markdown** of marks in locator order.
- Grounding: "before the model runs at all, DeepTutor runs your own question against the open document and hands the top hits to the turn... because it is deterministic it can be tested rather than sampled."
- "A reading material is not a knowledge base. Nothing is chunked, embedded, or indexed."
- Assessment for LifeKit: closest surface-level overlap with "one idea to remember" (reading + remembering), but the job is comprehension/Q&A over a document with citations — no reflection prompts, no lived practice, no accountability, no follow-through.

### Home page additions (docs-read)
- Capability picker: Chat, Ask Questions, Quiz, Visualize, Immersive Watching, Research, Solve behind flyout; "Mastery Path and Immersive Reading are workspaces under Personalized Learning, alongside Books and Practice."
- `cron`: "quiz me on this chapter every weekday at 9 is a sentence, not a setup screen"; due jobs run in the same conversation; "For a Partner, a due job rides back out through the IM channel."
- Personas: Default, peer, research-assistant, teacher — "change tone and pedagogy."
- Mobile: collapses to single column below tablet width.

### Partners page additions (docs-read)
- "A Partner is 'a chat that has a personality and a phone number.'" Synthetic workspace mirrors chat workspace; "Memory follows the relationship" (per-user private relationship memory).
- Channel Matrix includes WeChat, WeCom, QQ/NapCat, Telegram, Slack, Feishu, WhatsApp bridge. Partner Groups: multi-partner shared conversations.
- Still no accountability/coaching semantics: partners are tutors/companions with memory, not commitment trackers.

### Books (GitHub-sourced, not docs-read)
- README: "Book turns selected sources into an interactive **living book** — not a static PDF, but a reading environment built from typed blocks. A book can start from knowledge bases, notebooks, question banks, or chat history; the creation flow proposes a chapter outline before content is generated."
- v1.2.0: five-stage pipeline — Ideation → Source exploration → Spine synthesis → Page planning → Block compilation (`deeptutor/book/`).
- v1.5.13: "visited pages, bookmarks, and quiz attempts now roll up into a completion score and a list of weak chapters"; export to self-contained Markdown.
- Key differentiation note: DeepTutor *generates* books from your materials; LifeKit works from *published* books (Designing Your Life etc.) and extracts exercises/ideas. Opposite directions.

### Remaining genuinely unread docs pages
Books (docs page), Co-Writer, Learning Space, Knowledge Center, My Agents/Subagents detail, Channel setup guides, Settings, FAQ/pricing/API. Fallback path: docs are built from GitHub markdown under `site/src/content/docs/docs/explore/` in HKUDS/DeepTutor.
