# LifeKit — User Stories

What the user does with LifeKit v1, in "As a / I want / so that" form with
acceptance criteria. The vision is `.agents/intent.md`; the reason for each
choice is in `docs/product/ROADMAP.md`. The briefing-era stories are archived
at `docs/archive/user-stories-2026-10.md`.

---

## Epic 1: Read the book as cards

### US-01: Open the feed where I left off
**As a** user coming back to LifeKit,
**I want** the feed to open at the furthest card I responded to,
**so that** I do not scroll past cards I already handled.

**Acceptance criteria:**
- [ ] With no responses yet, the feed opens at the first card of the book.
- [ ] Otherwise, it opens at the card with the highest position that I liked, disliked, or commented on.
- [ ] "Show earlier cards" loads the cards above, without moving what I see.

### US-02: See where a card comes from
**As a** user reading a card,
**I want** to see whether the book says it or LifeKit made it, and the exact quote,
**so that** I can trust the card and find it in the book.

**Acceptance criteria:**
- [ ] Every card shows "From the book" or "LifeKit question".
- [ ] Every card shows a verbatim quote and its chapter or page.

### US-03: Get rid of a card that is not useful
**As a** user who finds a card useless,
**I want** to dislike it,
**so that** it leaves my feed and LifeKit learns which cards miss.

**Acceptance criteria:**
- [ ] Dislike folds the card into "Marked not useful · Undo".
- [ ] Undo brings the card back.
- [ ] A disliked card does not appear on the next load.
- [ ] Like marks a card as worth keeping. No counts are shown.

## Epic 2: Respond with comments

### US-04: Write a journal entry on a prompt
**As a** user on a reflect card,
**I want** to write my entry as a comment, with markdown if I like,
**so that** my journal lives next to the prompt that started it.

**Acceptance criteria:**
- [ ] The comment box shows the hint "Write your entry…".
- [ ] Bold, lists, and links render after I post.
- [ ] Ctrl/Cmd+Enter posts.

### US-05: Check in on a habit or an exercise
**As a** user who did a habit or an exercise,
**I want** to post a short note under its card,
**so that** I have a record of what I did.

**Acceptance criteria:**
- [ ] The note is saved before the coach replies.
- [ ] The card shows the last 2 messages and "View all N comments".

### US-06: Answer a question, then see the author's answer
**As a** user on a question card,
**I want** to write my answer first and then see what the author says,
**so that** I check my own understanding without a grade.

**Acceptance criteria:**
- [ ] The author's answer is hidden until I post a comment.
- [ ] After I post, the card shows the author's answer and the quote, with no score or mark.

## Epic 3: The coach replies

### US-07: Get a reply that fits what I wrote
**As a** user who posted a comment,
**I want** the coach to reply, briefly for an entry and fully for a question,
**so that** my effort feels seen and my questions get answers.

**Acceptance criteria:**
- [ ] Every comment gets one coach reply, which streams in.
- [ ] The reply uses only the card, its passage, my thread, and passages from the same book.
- [ ] The reply never grades me.

### US-08: Never lose what I wrote
**As a** user whose coach reply failed,
**I want** my comment to stay and a way to try again,
**so that** a dead GPU never costs me a journal entry.

**Acceptance criteria:**
- [ ] On failure, my comment stays and the reply slot shows "The coach could not reply." and Retry.
- [ ] Retry adds one reply and does not post my comment twice.

### US-09: Tell LifeKit when a reply misses
**As a** user reading a coach reply,
**I want** to like or dislike it,
**so that** the dogfood review can tell if replies help.

**Acceptance criteria:**
- [ ] Like and dislike on each coach reply, not on my own comments.
- [ ] A pressed button pairs color with a filled icon.
