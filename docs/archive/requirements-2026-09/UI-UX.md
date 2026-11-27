# LifeKit — UI/UX Design

## Design System

**Source:** platform.claude.com flat design (extracted via `designlang` 2026-09-26)

| Token | Value |
|-------|-------|
| Primary | `#cf222e` |
| Secondary | `#0550ae` |
| Accent | `#6da7ec` |
| Background | `#fcfcfb` |
| Foreground | `#0b0b0b` |
| Neutral | `#898781` |
| Font | system-ui stack |
| Body | 14px / 21px line-height |
| Container | 785px |
| Radii | sm: 4px, md: 10px, lg: 14px |
| Elevation | Flat; xs shadow only |

## Feed Screen

```
+-----------------------------------------+
|  Today - Designing Your Life - Day 12  |  TodayHeader
+-----------------------------------------+
|  ideas seen -> retained -> lived        |  Stage strip
+-----------------------------------------+
|  +-----------------------------------+  |
|  |  Exercise: Mind Mapping           |  |  ExerciseCard
|  |  Chapter 3 - Prototyping          |  |
|  |  "Map your problem..."            |  |
|  |  [Mark done]  [Talk about this]  |  |
|  +-----------------------------------+  |
+-----------------------------------------+
|  +-----------------------------------+  |
|  |  Idea: Failure is data            |  |  ResurfacedIdeaCard
|  |  Because you haven't revisited    |  |
|  |  this since Sep 15...             |  |
|  |  [Still with me]  [Talk about]   |  |
|  +-----------------------------------+  |
+-----------------------------------------+
|  Fading ideas:                          |  FadingIdeasCard
|  - Talk to people (Oct 2)               |
|  - Grok (Sep 28)                        |
+-----------------------------------------+
|  Conversations:                         |  ConversationsList
|  - Mind Mapping (Sep 20)                |
|  - Prototyping (Sep 18)                 |
+-----------------------------------------+
|  +-----------------------------------+  |
|  |  Ask anything...                  |  |  MasterComposer
|  +-----------------------------------+  |
+-----------------------------------------+
```

## Conversation Screen

```
+-----------------------------------------+
|  < Feed                                  |  Back button
|  Mind Mapping - seeded from exercise    |  Title + seed badge
+-----------------------------------------+
|                                         |
|  Coach: Let's talk through mind         |
|  mapping. What problem are you           |
|  working on?                             |
|                                         |
|  You: I'm stuck on my career            |
|  direction...                            |
|                                         |
|  Coach: The book says "failure is       |
|  data" - what would you try if you      |
|  knew you couldn't fail?                 |
|                                         |
+-----------------------------------------+
|  +-----------------------------------+  |
|  |  Type a message...            |  |  ChatInput (pinned bottom)
|  +-----------------------------------+  |
+-----------------------------------------+
```

## UI Constraints

- **No quiz framing.** No grades, no percentages, no mastery gates.
- **No dashboards.** No browsing surfaces that turn doing back into browsing.
- **No streaks as gamification.** Plain count only, no guilt language.
- **Venue, not menu.** The feed is where you do the work.

## Component Inventory

| Component | File | Purpose |
|-----------|------|---------|
| TodayHeader | `frontend/src/components/feed/TodayHeader.tsx` | Book + day |
| ExerciseCard | `frontend/src/components/feed/ExerciseCard.tsx` | Today's exercise |
| ResurfacedIdeaCard | `frontend/src/components/feed/ResurfacedIdeaCard.tsx` | Idea to remember |
| FadingIdeasCard | `frontend/src/components/feed/FadingIdeasCard.tsx` | Ideas due for a touch |
| ConversationsList | `frontend/src/components/feed/ConversationsList.tsx` | Past conversations |
| MasterComposer | `frontend/src/components/feed/MasterComposer.tsx` | New conversation |
| MessageList | `frontend/src/components/conversation/MessageList.tsx` | Chat messages |
| ChatInput | `frontend/src/components/conversation/ChatInput.tsx` | Message input |
| useBriefing | `frontend/src/hooks/useBriefing.ts` | Feed data hook |
| useConversation | `frontend/src/hooks/useConversation.ts` | Conversation hook |
