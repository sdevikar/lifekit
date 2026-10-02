# Dark Theme — Proposal

## Why

The UI is light-only. Its 17 theme tokens are hardcoded light values in
`frontend/src/app/globals.css`, so a user on a dark-mode desktop gets a
glaring white page — on an app meant to be opened once a day, often at night.

The fix is cheap because the components are already fully tokenized: a grep for
hex or `rgb()` literals across `frontend/src/components/` and `frontend/src/app/`
returns nothing. Every color in the UI flows through `--lk-*` custom properties.
So this is a token swap, not a component rewrite.

## What Changes

- **`globals.css` — tokens become `light-dark()`.** Set `color-scheme: light dark`
  on `:root` and express each color token as `light-dark(<light>, <dark>)`. The
  browser follows the OS with no JavaScript. Three tokens invert rather than
  merely swap:

  | Token | Light | Dark | Why |
  |---|---|---|---|
  | `--lk-primary` | `#0b0b0b` | `#f5f4f2` | It is a button *fill*. A near-black pill on a dark page is invisible, so primary inverts to light. |
  | `--lk-card` | `#ffffff` | `#242422` | Must sit above the page, not below it. |
  | `--lk-border` | `rgba(11,11,11,.1)` | `rgba(245,244,242,.12)` | Black-alpha borders vanish on a dark surface. |

  Also: `--lk-brand-clay` → `#d97757` (lighter step; the base `#c6613f` reaches
  only 4.98:1 on a dark card), `--lk-bg` → `#1c1c1b`, `--lk-muted` → `#a5a49a`,
  `--lk-subtle` → `#c3c2b7`, `--lk-secondary` → `#a5a49a`, `--lk-user-msg` and
  `--lk-badge-bg` → white-alpha, shadow alphas → white-alpha for the inset ring.

- **Manual override via `data-theme`.** `:root[data-theme="dark"]` and
  `:root[data-theme="light"]` pin `color-scheme`, letting a user opt out of the
  OS preference per-app. This is the escape hatch for anyone who wants light on
  a dark desktop; flipping the OS globally is the alternative and it changes
  every other window.

- **Toggle button — `components/ThemeToggle.tsx` (new, `"use client"`).**
  Reads `localStorage` → falls back to `matchMedia` → falls back to OS. Sets
  `data-theme` on `<html>` and persists. Placed in the feed header
  (`TodayHeader`) and in **both** branches of the conversation header
  (`app/c/[id]/page.tsx` renders separate headers for loading and loaded states —
  the loading branch needs it too or the control disappears mid-load).

- **Anti-flash script in `layout.tsx`.** A small inline script sets `data-theme`
  before first paint, reading the same `localStorage` key. Without it, a
  dark-preference user sees a white flash on every load. This is the one real
  cost of the toggle and the reason it must live in the layout, not a component.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: theming. The feed and conversation views render in
  either color scheme, following the OS by default with a per-app manual
  override.

## Not In Scope

Deployment beyond localhost. `.agents/intent.md:61` makes "Localhost only, no
auth, no cloud, no sync" a non-negotiable, and line 84 defers everything past
Stage 5 until Stage 4 completes. This change makes no hosting assumption and
introduces no dependency on one: `localStorage` and `matchMedia` behave the
same on any host. If deployment is ever revisited, this work carries over
unchanged.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`.
2. With the OS set to dark, `/feed` and `/c/<id>` render dark; set to light,
   they render light. Verified by screenshot in both schemes, both views.
3. The toggle flips both views, survives a page reload, and overrides the OS in
   both directions (dark OS + light toggle, light OS + dark toggle).
4. No flash of the wrong theme on load: with the OS dark and no stored
   preference, the first painted frame is dark.
5. All 12 text/background token pairs meet WCAG AA — body text ≥ 4.5:1, large
   UI and non-text ≥ 3:1. Ratios are computed and recorded, not eyeballed.
6. `test_useConversation` still passes (it drives the real hook against a
   running server).
7. `uv run pytest` shows no new failures beyond the known
   `test_split_dyl_pdf` (BACKLOG P2, hardcoded VM path).
8. `docs/product/STATUS.md` updated in the same change.
