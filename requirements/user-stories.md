# LifeKit: User Stories

This document captures detailed user stories for LifeKit, written in the classic "As a [persona], I want <action> so that <benefit>" format. Each story includes acceptance criteria to define exactly when it is complete. These are organized by epic (major feature area).

---

## Epic 1: Onboarding and Context Setup

### US-01: New User Interview
**As a** new LifeKit user,  
**I want** **to go through an interactive interview about my goals, daily habits, time availability, and preferred learning style,  
so that ** LifeKit knows enough to generate personalized plans and invitations tailored to my life.

**Acceptance Criteria:**
- [x] User is greeted with a friendly welcome message on first session launch via OpenWebUI pipe or later the React frontend.
- [ ] The interviewer asks up to 8 questions in sequence (not all at once) covering: primary goal(s), secondary goals, time available per day/week, learning style preference (text/audio/video), and what motivates them.  
- [ ] Questions adapt based on previous answers (e.g., if the user says "I want to build a personal brand", follow-up asks about platform, timeline, current skills).
- [ ] At any point the user can type `skip` and move past non-critical questions.
- [x] Once complete, the interviewer summarizes a one-paragraph bio and asks for confirmation ("Does this sound right? Yes / No").
- [x] Bio is saved to SQLite (`user_bios` table) with unique ID, timestamp, and structured JSON fields.
- [x] Upon confirmed bio, OpenWebUI displays: "Great! I've got your context down. What would you like to start with today?" alongside the first set of **invitation bubbles** (not a full plan).

### US-02: Advanced User Direct Knowledge Upload
**As an** advanced user who already knows what they're working on,  
**I want** **to skip the interview and directly upload books, PDFs, audiobooks, or video links into my knowledge store, so that LifeKit can immediately start from there.

**Acceptance Criteria:**
- [x] A file-upload endpoint accepts .epub, .pdf, YouTube URLs, and local audiobook paths.
- [ ] On upload, the system parses the content (EPUB highlights, PDF text via Ollama summarization, YouTube transcripts).
- [x] Extracted chunks structured with metadata: source title, chapter/section reference, timestamp/audio segment ID, and relevance keywords for later retrieval.
- [ ] The system presents a brief confirmation ("3 chapters extracted from Atomic Habits. Your knowledge store now has 47 searchable segments.").
- [ ] No interview is forced; the system instead generates **invitation bubbles** based on the uploaded content (e.g., "Want to start with a concept check on Chapter 1?").

---

## Epic 2: Session Start Invitation and Context Injection

### US-03: Opening Context and Invitations Display
**As a** returning LifeKit user,  
**I want ** that every time I open the chat interface (OpenWebUI or later React UI), I see an opening context summary of my recent goals/library alongside clickable invitation suggestions, so that I don't have to remember what I was working on — the system surfaces it for me and lets me choose a starting point.

**Acceptance Criteria:**
- [x] At session start (pipe intercept or API endpoint `/generate_invitations`), the system **layers whatever data is available -- no forced baseline**:
  - **Fresh user (no interview, no habits):** Invitations derived **purely from knowledge store docs**. Example: *"Atomic Habits Chapter 3 introduces a principle about small wins. Want to try a Feynman check on it?"*
  - **Interviewed user (bio exists + docs in store):** Invitations combine interview responses with stored documents. Example: *"You said you want to build a personal brand AND 'Deep Work' is flagged for review. Shall we start there?"*
  - **Returning user (history + bio + docs):** Invitations cross-reference exercise history, knowledge store relevance, and behavioral patterns. Example *"Last session you completed a Feynman exercise on Chapter 3 — the concept needs reinforcement within 3 days to stick."*
- [x] A brief context summary is rendered, e.g., "Based on Atomic Habits Chapter 3 and your goal to build a habit tracker..."
- [x] 3-4 **invitation bubbles** are generated, one per exercise type relevant to that goal. Examples:  
  - `[Concept Check] Explain the 'Habit Loop' in your own words`  
  - `[Log Habit] I worked on my goal today...`  
  - `[Journal] Reflect on this week's progress...`
- [x] Clicking any bubble triggers a pipe call that logs intent and initiates the corresponding exercise session.

### US-04: Invitations Are Never Assumptive Decisions
**As a** user who wants guidance without feeling micromanaged,  
**I want ** LifeKit to **never** generate a plan or make decisions for me without an explicit invitation that I choose from, so that I stay in control of my learning journey and only take actions I'm ready for.

**Acceptance Criteria:**
- [x] The system's first interaction in any session is *always* context injection + invitation suggestions, never a direct plan or advice dump.
- [x] Invitations are derived from **tiered data layers based on user state**:
  - If no bio exists → **(a) knowledge store docs only**
  - If bio exists → **(b) interview responses (c) knowledge store docs**
  - If history exists → **(c) previous exercise logs + (d) momentum score data + (e) knowledge store relevance**
- [x] Each invitation includes a clear description of what it will entail (e.g., "[Concept Check] Explain the 'Habit Loop' in your own words" vs vague "Continue working!").
- [ ] User can dismiss all invitations and instead type a free-form prompt like "Just give me a summary of this week."

---

## Epic 3: Exercise Execution and Logging -- Concept Check (Feynman)

### US-05: Feynman Technique Concept Check
**As a** user learning from a book,  
**I want ** to be prompted with a specific concept from my library and asked to explain it back in your own words, so that I can actively test my understanding rather than passively rereading.

**Acceptance Criteria:**
- [ ] User clicks `[Concept Check]` invitation -> `exercise_instances` record created with `type='feynman'`, relevant excerpt from the knowledge store.
- [x] System presents: "Let's do a quick concept check. From Atomic Habits Chapter 3: '[excerpt text]' -- Can you explain this principle in your own words?"
- [ ] User types explanation (no time limit, free form).
- [x] On submission, system evaluates the explanation using Ollama (`qwen3.6:latest`) against a rubric: accuracy, completeness, and clarity.
- [x] Feedback is given in 2-3 sentences, not graded with a score: highlight strengths and gently correct any misconceptions.
- [ ] Log entry stored in `exercise_logs` with user's response, AI feedback summary, and metadata fields (`has_misconception: bool`, `confidence_hint`).

---

## Epic 4: Exercise Execution and Logging -- Habit Log

### US-06: Simple Habit Log Check-in
**As a** user building consistent habits,  
**I want ** to quickly log whether I completed my daily habit without long prompts or friction, **so that momentum decay can be calculated accurately and I maintain streaks.

**Acceptance Criteria:**
- [x] User clicks `[Log Habit]` invitation.
- [ ] System presents the specific habit/task with a simple prompt: "Did you complete today's habit? 'Review Atomic Habits Chapter 4' -- [Yes / Partially / No]" plus an optional text box for notes.
- [x] On submission, `exercise_logs` entry is created with type `'action_log'`, boolean completion value, and any notes as JSON in the metadata field.
- [x] `momentum_tracker.py` receives the completion log and updates that goal's urgency score accordingly:
  - If Yes -> normal decay interval continues
  - If Partially -> shortens the next review deadline (+24h)
  - If No -> triggers a "Revival" flag; next session generates a lower-friction invitation ("Want to do just a 2-minute version today?")
- [x] Streak counter increments/decrement is displayed in OpenWebUI or later dashboard.

---

## Epic 5: Journaling Exercises -- Daily and Guided Reflections

### US-07: Semi-Prompts for Journal Reflection
**As a** user who benefits from guided reflection,  
**I want ** journal exercises that provide me with a focused prompt rather than a blank page, so the reflection is more productive.

**Acceptance Criteria:**
- [x] User clicks `[Journal]` invitation.
- [ ] System pulls from `knowledge_store` and previous logs to generate 2-3 **semi-prompts**. Examples:
  - "Did you complete your reading today?"
  - "What blocked progress this week, and what's one thing you could adjust?" 
  - "What did you learn that surprised you from the content you consumed?"
- [x] User chooses one prompt (or ignores all and writes freely).
- [x] On submission: Ollama performs a lightweight `tone_analysis` of the entry -- returns 1-3 descriptors (e.g., "Stressed", "Frustrated but Motivated", "Productive") stored in the `tone_analysis` column.
- [x] Log is saved in `exercise_logs` with type `'journal'`, full text, tone metadata.

### US-08: Unprompted Journal Entry Anytime
**As a** user who may have an insight at any moment,  
**I want ** to be able to type "Journal:" or just free-text at any point in the chat, so that I can capture thoughts immediately without waiting for an invitation prompt.

**Acceptance Criteria:**
- [x] Any message starting with `journal:` or typed freely (after initial confirmation) is routed to a journal exercise instance rather than treated as a concept check or habit log.
- [ ] System logs it in `exercise_logs` regardless of whether an invitation was clicked first.
- [x] Tone analysis runs automatically and returns briefly: **"Your entry reflects 'Frustration'. Want me to suggest a small action?"**

---

## Epic 6: Passive Content Consumption

### US-09: Passive Learning with Deferred Engagement
**As someone consuming knowledge when time allows,  
**I want ** to receive bite-sized content chunks from my library (summaries or key quotes) and mark when I've read them so that the system knows I consumed it and can quiz me on it later.

**Acceptance Criteria:**
- [ ] User clicks `[Content Digest]` invitation (or system suggests passive consumption during revival).
- [x] System extracts a 150-200 word relevant excerpt from `knowledge_store`, formatted as:  
```"...From Atomic Habits, Chapter 3:"```
"[ excerpts text]"
- [x] User reads and clicks `[Marked as Read]`.
- [ ] `exercise_logs` records consumption with a timestamp.
- [x] System schedules a quiz or reflection exercise for that content within 3-7 days based on the spaced repetition algorithm (`momentum_tracker`).

---

## Epic 7: Weekly Retrospective and Replanning

### US-10: Automatic Weekly Review Suggestions
**As an user tracking progress over time,  
**I want ** **to receive a weekly summary of what I said I'd do versus what I actually did, along with tone analysis from my journal entries, so that the system understands the gap and adjusts my load accordingly.

**Acceptance Criteria:**
- [x] Every Sunday (configurable via pipe logic or manual trigger), system queries `exercise_logs` for the past 7 days: completion counts, exercise types performed, tone analysis summaries.
- [ ] System generates a retrospective card/message:  
```"This week you aimed for 7 habits. Completed: 4. Partially: 1. Missed: 2.
Your journal tones suggest 'Frustrated' on 3 of those days. Based on this pattern, should I reduce your load next week or keep it the same?"```
- [ ] User responds with Yes/No/Maybe. If "Maybe" or no response within 48 hours, the system defaults to a slight reduction (20% less load).

---

## Epic 8: External Library Connections (Future Phase)

### US-11: Goodreads Integration
**As ** **a user who reads digitally and tracks reading goals externally,  
**I want ** LifeKit to automatically import my current books, progress, and highlights from Kindle/Goodreads so that I don't have to manually upload files and the system has automatic context.

**Acceptance Criteria:**
- [ ] User connects their Goodreads account via API key.
- [x] On sync, the top 3 currently-reading books are imported into `knowledge_store` with current page count as a progress indicator in invitations.

### US-12: Kindle Highlights Auto-Population for the Knowledge Store
**As ** **a reader who highlights extensively,  
**I want ** my Amazon highlights to flow directly into LifeKit's knowledge store as searchable content segments tied to specific goals or topics, so that I never have to manually re-enter anything.

**Acceptance Criteria:**
- [x] User uploads a `my_clippings.txt` file from any Kindle device/app.
- [ ] Testing: system extracts all highlights as individual, searchable chunks in `knowledge_store`. Highlights auto-linked to goals/topics where relevant (via keyword matching).

---

## Epic 9: Frontend Rendering (OpenWebUI MVP then React Production)

### US-14: OpenWebUI MVP Interface for Invitations
**As a** user testing LifeKit's early version through OpenWebUI,  
**I want ** the **invitation bubbles/cards to appear as distinct UI elements (not just plain text), so that I can visually scan and choose my starting activity without confusion.

**Acceptance Criteria:**
- [x] Invitations render in OpenWebUI as clearly separated cards/bubbles with icons, descriptions, exercise type labels.
- [x] Clicking any invitation triggers the MCP tool call to start that exercise session.
  The opening context paragraph is visually distinct from the invitation section.

### US-15: Production React UI -- Dashboard With Momentum Visualization
**As a** long-term LifeKit user,  
**I want ** **to see my momentum scores over time in charts and graphs, so that progress feels tangible and motivating rather than just abstract checkmarks.

**Acceptance Criteria:**
- [x] A dedicated dashboard page at `/dashboard` shows:
  - Current streak counts per habit/goal with visual bars
  - Weekly completion rate chart (aimed vs. achieved)
  - Mood/tone trend timeline from journal entries  
    - "Pulse" section showing high-momentum goals
- [x] Data is sourced directly from SQLite via the FastAPI REST backend (`/api/momentum/{goal_id}`, `/api/logs/latest`, etc.).

*Note: This visual dashboard layer is built **ABSOLUTE LAST** (Phase 3+), after the momentum algorithm, data model, and core exercise loops are all tested and proven.*

---

## Epic 10: Edge Cases and Resilience

### US-16: Handling Absent User for Extended Periods (Revival Mode)
**As someone who goes quiet for weeks,  
I want ** **the system to recognize my extended absence and the pressure by offering "warm-up" exercises instead of demanding a full review, 
so that ** **coming back doesn't feel overwhelming or guilt-inducing.

**Acceptance Criteria:**
- [x] If no `exercise_logs` entries exist for >7 days for a goal, the status transitions to Revival State in `momentum_tracker`.
- [x] On return, invitations are auto-lowered-friction: "You haven't revisited 'Atomic Habits' Ch. 3 in a while -- want to do a 2-minute version?"  
  The user does not see guilt-driven messaging ("You've fallen behind!").

### US-17: Error Handling and Graceful Fallbacks
**As a ** **user who sometimes encounters AI or data issues, I want error messages that are clear and corrective rather than technical jargon, so that I stay confident in the system even things go wrong.

**Acceptance Criteria:**
- [x] If Ollama is down during an exercise, users see: "Ollama's not responding right now -- we've saved your progress locally and'll try again in a moment."  
- [ ] If knowledge store query fails for context injection, system falls back to generic invitations without specific book references.

---