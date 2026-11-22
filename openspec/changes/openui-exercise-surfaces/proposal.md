# OpenUI Exercise Surfaces — Proposal

**Status: proposal only — do not implement yet.**

## Why

The upcoming exercise surfaces (`exercise-surface-routing`, `exercise-type-system`,
`exercise-surface-journal/tracking/questionnaire/concept-check/worksheet`) planned
a separate A2UI component registry. With OpenUI adopted for chat, the exercise
components should become the same OpenUI library — one library, one spec, one
prompt. This proposal absorbs the A2UI plan into OpenUI: the component registry
keyed by exercise type becomes OpenUI components, and the A2UI message format
is replaced by OpenUI Lang.

## What Changes

Frontend (primary). Depends on `openui-hybrid-chat` (shared library + styles).

## Decisions (locked)

- **Absorb, don't parallel.** A2UI is replaced by OpenUI. One component library
  serves both chat and exercises. No second component system.
- **Minimal component set.** Only components the exercise surfaces actually need
  (form fields, inputs, tracking logs, journal editors, concept-check inputs,
  worksheets). Reuse built-in OpenUI components where possible.
- **OpenUI owns the visual.** Exercise surfaces render via `<Renderer>`; no
  custom wrappers around generated UI (same principle as chat).

## Relationship to existing proposals

- `exercise-type-system`: its "component registry keyed by exercise type" becomes
  OpenUI components defined via `defineComponent`. The schema (exercise_type →
  component) stays; the rendering mechanism changes from A2UI to OpenUI Lang.
- `exercise-surface-*`: each surface's component is an OpenUI component in the
  shared library, composed by the model/backend as needed.
- `exercise-surface-routing`: unchanged — routing/transition logic is independent
  of the rendering format.

## Not In Scope

- The routing/transition/animation (unchanged, separate proposal).
- Design-token mapping (follow-up, shared with chat).
- Backend generation of exercise UI (deferred; surfaces render static OpenUI
  components for now).

## Open Questions (to settle during grilling of ticket 02)

- Exact component list per exercise type.
- Whether the backend generates exercise UI as OpenUI Lang or the frontend
  maps exercise_type → component directly.

## Done Criterion

1. A single OpenUI library contains both chat and exercise components.
2. At least one exercise surface renders via `<Renderer>`.
3. `npm run build` and `npm run lint` pass.