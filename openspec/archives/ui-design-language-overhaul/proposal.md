# UI Design Language Overhaul — Proposal

## Why

The current frontend UI in `frontend/` is functional but uses generic, minimal Tailwind fallback styles that do not match the comprehensive design language documented in `docs/ux/ui/design_language.md` and `docs/ux/ui/variable.css`. Bringing the UI into complete alignment with the design language improves visual hierarchy, readability, consistency, and fidelity with the Claude Platform design system on which LifeKit's UX is based.

## What Changes

- **Design System Tokens & Global CSS:**
  - Update `frontend/src/app/globals.css` to import and expose full design variables from `docs/ux/ui/variable.css` (primary `#cf222e`, secondary `#0550ae`, accent `#6da7ec`, neutral palette ramps, background `#fcfcfb`, surface raised `#ffffff`, card border `#d1d1ce`, typography scales, radii `4px`/`10px`/`14px`, and inset/panel elevation shadows).
  - Configure page container wrapper to enforce centered `785px` maximum width with `24px` horizontal gutters.

- **Feed Components Alignment:**
  - `TodayHeader`: Format title, date, and stage strip ("Seen", "Retained", "Lived") with correct typography tokens and spacing.
  - `ExerciseCard`: Apply exact `.lk-card` raised surface styling, subtle borders, shadows, quote styling, and primary/secondary button variants.
  - `ResurfacedIdeaCard`: Align with card typography, why-it-resurfaced badge/label, and action button styles.
  - `FadingIdeasCard`: Align per-idea list and action buttons.
  - `ConversationsList` & `MasterComposer`: Format bottom composer input and conversation links according to design language button/input tokens.

- **Conversation Components Alignment:**
  - `ConversationPage`, `MessageList`, and `ChatInput`: Update back button, header, seed context badge, user message bubbles (`--cds-bg-user-message`), coach response styling, and input field aesthetics.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: UI overhaul aligning the feed and conversation pages with the extracted platform design language tokens and layout system.

## Done Criterion

1. `frontend` builds successfully with Next.js (`npm run build`) and passes ESLint (`npm run lint`).
2. All components in `frontend/src/components/` and pages in `frontend/src/app/` utilize design tokens from `globals.css` matching `docs/ux/ui/design_language.md`.
3. Feed and Conversation UI pages render with a centered `785px` container width, correct typography scale, OKLCH/hex colors, radii, and button states.
