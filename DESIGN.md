# LifeKit design language

This file tells any agent or person how LifeKit's UI must look and behave. It
exists so a new session does not re-derive the look from old docs or invent a
new one. Read it before any UI work, together with `frontend/AGENTS.md`.

The order of authority on a conflict:

1. `.agents/intent.md` — the vision.
2. `docs/product/ROADMAP.md` D1 (layout) and D15 (design rules) — the decisions
   and their reasons.
3. This file — how to apply D1 and D15.
4. `frontend/src/app/globals.css` — the tokens.

## Layout (ROADMAP D1)

- One screen: the feed. One centered column at every width.
- The only chrome is the feed header: the book title, the card count, and the
  theme toggle.
- No sidebar, drawer, tab bar, or modal page for a card. A card's thread opens
  in place under the card.
- The phone is a first-class target. Check every change at phone width.

## Design rules (ROADMAP D15)

LifeKit follows the design language of Meta's Astryx (`meta/astryx`, MIT,
beta). We borrow its written rules, not its component library. Each rule below
names the Astryx design record it comes from.

| Rule | Astryx source |
|------|---------------|
| Nested corners are concentric: inner radius = outer radius − gap. | `docs/design/shape-relationships.md` (DR2) |
| A surface uses a hairline border or a soft shadow, not both. Depth stays quiet. | `docs/design/elevation-hierarchy.md` (DR2) |
| No colored accent stripe on the side of a card. Show selection with a boundary that follows the corners. | `docs/design/shape-relationships.md` (examples) |
| One primary action per surface. Peer actions stay visually weaker. | `docs/design/color-emphasis.md` (primary accent, examples) |
| A status always pairs color with an icon or a label. | `docs/design/system-states.md` |
| Text and controls meet WCAG AA contrast in light and dark themes. Colors are `light-dark()` pairs. | `docs/design/color-emphasis.md` asks for legible pairs in every mode; the AA level is our choice. |
| Small changes animate in about 175 ms. Entrances and exits take about 410 ms. | `packages/cli/assets/docs/tree/tokens-duration.doc.mjs` (`--duration-fast`, `--duration-medium`) |
| Animate only `transform` and `opacity`. Respect `prefers-reduced-motion`. | `docs/design/motion.md`, `docs/design/reduced-motion.md` |
| A streaming coach reply shows that the coach is working ("Coach is writing…"), and a failure shows a Retry. | `docs/design/agentic-states.md` |

Read the records at the commit we checked, `550427c` (2026-11-27):
`https://github.com/meta/astryx/tree/550427c971754888c2ec07b08c8a1a4b62c6262f/docs/design`.
If a record changes upstream, update this table and D15 together.

## What we do not use from Astryx

- The component library and StyleX. They add a beta dependency (D15).
- The Astryx Claude plugin (`astryx@astryx`). Its one skill only tells the
  agent to use the `astryx` CLI and library, which D15 rejects.

## Tokens

- All colors, radii, shadows, and fonts are `--lk-*` and `--radius-*` custom
  properties in `frontend/src/app/globals.css`. Use the tokens. Do not write
  hex or rgb literals in components.
- The current palette and type come from a flat style based on
  platform.claude.com (commit `f271e21`). The old extraction docs are in
  `docs/archive/ux-2026-10/`. They are history, not the source.
- A new token needs a light and a dark value and an AA check in both themes.

## Before you finish a UI change

1. Run `cd frontend && npx next build` and `npx eslint src`.
2. Check the table above for each surface you changed.
3. Run `lifekit ui` and ask the human to look at it on a desktop and a phone
   (AGENTS.md, Working agreements).
