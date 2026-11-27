# LifeKit — User Stories

What the user does with LifeKit, in "As a / I want / so that" form with
acceptance criteria. Aligned with `.agents/intent.md` (accountability
partner, not learning platform — no quizzes, grades, or profiling).
Supersedes the OpenWebUI-era stories archived at
`docs/archive/user-stories-2026-09.md`.

---

## Epic 1: The daily briefing

### US-01: See today at a glance
**As a** user starting my day,
**I want** to open LifeKit and see one exercise to do and one idea to remember,
**so that** I know exactly what today's practice is without deciding.

**Acceptance criteria:**
- [ ] The feed shows a "Today" header (book + day), today's-exercise card, and resurfaced-idea card.
- [ ] Each card shows where it comes from (book, chapter).
- [ ] The whole briefing is generated deterministically from completion history — the LLM only phrases it.

### US-02: Mark an exercise done
**As a** user who did today's exercise,
**I want** to mark it done with one tap,
**so that** LifeKit records what I did and reschedules accordingly.

**Acceptance criteria:**
- [ ] "Mark done" on the exercise card records a completion with timestamp.
- [ ] Completion is self-declared — no test, no grade, no follow-up quiz.
- [ ] Completion provenance is stored (self-declared vs. assessed).

### US-03: Confirm an idea is still with me
**As a** user shown a resurfaced idea,
**I want** to say "still with me" (or not),
**so that** LifeKit learns what stuck without testing me.

**Acceptance criteria:**
- [ ] The resurfaced-idea card offers a "Still with me" signal.
- [ ] The signal feeds the resurfacing schedule; the user never sees a score or percentage.
- [ ] A short note explains *why* the idea resurfaced, in plain language.

### US-04: Notice what's fading
**As a** user,
**I want** to see which ideas are fading from practice,
**so that** I can revisit them before they're gone.

**Acceptance criteria:**
- [ ] The feed includes a fading-ideas card listing ideas due for a touch.
- [ ] No counts-as-gamification: plain list, no streaks, no guilt language.

---

## Epic 2: Conversations

### US-05: Talk about a card
**As a** user looking at a feed card,
**I want** to tap "Talk about this" and discuss it with the coach,
**so that** I can think through the exercise or idea in conversation.

**Acceptance criteria:**
- [ ] Every card carries a "Talk about this" action.
- [ ] Tapping it opens a conversation seeded with that card's context.
- [ ] Replies are grounded in the book (citations), conversational in tone.

### US-06: Start a conversation anytime
**As a** user with something on my mind,
**I want** a composer at the bottom of the feed that starts a new conversation,
**so that** I don't need a card to talk to the coach.

**Acceptance criteria:**
- [ ] A master text box at the bottom of the feed opens a new conversation on submit.
- [ ] The conversation is stored; it appears in the feed's conversations list.

### US-07: Leave and return
**As a** user in a conversation,
**I want** to go back to the feed and return to the conversation later,
**so that** chats don't trap me.

**Acceptance criteria:**
- [ ] The conversation view has a back-to-feed action.
- [ ] Past conversations are listed on the feed and reopen where they left off.

---

## Epic 3: Library (multi-book)

### US-08: Practice across books
**As a** user with more than one book in the library,
**I want** the feed to draw exercises and ideas across my books,
**so that** LifeKit coaches the whole shelf, not one book at a time.

**Acceptance criteria:**
- [ ] Exercises and ideas are registered per book; the briefing can surface any of them.
- [ ] Each surfaced item names its book.
