# Step 11: Invite-to-coach UI — proposal

## Why

A learner may want an external coach or accountability partner to see their
progress — what they're working on, momentum, intentions honored/missed —
*without* exposing raw reflections or the full book text. This step is last
in the build order because it's the least validated need: the coach
relationship isn't defined yet (open question in the coaching plan §6 —
human friend, professional coach, or another agent?). Build only the minimal
version until that question is answered.

## What Changes

- **Static-site export** (minimal, per the build philosophy and Step 0's
  locked "no cloud" assumption):
  `lifekit export coach-report --goal <id> --out ./coach-report/` generates a
  self-contained HTML folder with: goal summary, momentum chart (SVG
  sparkline, no JS lib), exercise history, open intentions, and a coach-notes
  section.
- **Sharing = the learner sends the folder/file.** Comments arrive
  out-of-band, or via a `coach_notes.md` the learner pastes back. **No hosted
  service, no auth, no realtime.**
- **Privacy**: reflections marked `private` are excluded; reflections are
  opt-in per session (`shareable` flag at `record_attempt`, from Step 8).
- **Revocation = delete the export.** Each export is timestamped; stale
  exports are visibly labeled ("generated 2026-09-15").
- **Reuse:** Python stdlib + Jinja2 (single dependency if not already
  present); SVG sparklines hand-rolled (~20 lines).

## Capabilities

### New Capabilities

- `coach-report-export`: static HTML progress report for an external coach.

## Impact

- New `../../../lifekit/export/coach_report.py` + CLI. Reads sessions (Step 8),
  momentum (Step 9), goals (Step 10). No schema changes.

## Done criterion

1. Export renders correct data for a fixture learner; opens offline in a
   browser.
2. Private reflections never appear in output — tested with adversarial
   fixtures (reflections marked private + attempted injection via
   `coach_notes.md`).
3. Stale exports are visibly labeled with their generation timestamp.

## Non-goals

- Any hosted service, auth, realtime comments, or push delivery.
- Defining who the coach is — that decision gates whether this step grows
  beyond the static export.
