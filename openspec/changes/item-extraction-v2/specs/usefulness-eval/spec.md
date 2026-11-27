# Spec — usefulness-eval

## Purpose

Measure how often the items that reach the feed are actually useful, using a
golden set of the user's own yes/no labels, so that "not random crap" is a
number instead of a feeling.

## ADDED Requirements

### Requirement: Labelling command

`lifekit eval usefulness label <book_id>` SHALL show items one at a time with
their card type, title, content summary, quote, and section title, and accept
`y` (useful), `n` (not useful), `s` (skip), or `q` (quit). It MUST sample from
items with status `kept` or `rejected_not_useful`, spread across card types,
with a fixed seed, up to `--n` items (default 60).

#### Scenario: Label and quit
- **WHEN** the user labels 10 items and presses `q`
- **THEN** 10 labels are saved and the command exits 0

#### Scenario: The label screen hides the judge verdict
- **WHEN** an item is shown for labelling
- **THEN** its status, rating, and judge reason are not shown, so the label is not biased

### Requirement: Labels are durable

Labels SHALL be appended to `evals/usefulness/<book_id>/labels.jsonl`, one JSON
line per label with the item key, card type, title, label, and time. Labelling
again MUST skip items whose key already has a label. Labels MUST match items
by key, so they survive re-runs of the items stage.

#### Scenario: Resume labelling
- **WHEN** the user runs the labelling command a second time
- **THEN** no item labelled in the first session is shown again

#### Scenario: Labels after re-extraction
- **WHEN** the items stage re-runs and produces the same quote as the same card type
- **THEN** the old label applies to the new item

### Requirement: Report

`lifekit eval usefulness report <book_id>` SHALL write
`evals/usefulness/<book_id>/report.md` with: the items run id, model, and prompt
hash; precision (share of judge-kept labelled items the user marked useful);
recall (share of user-useful labelled items the judge kept); both per card type;
the number of labels used; and item counts per status and per section.

#### Scenario: Precision computed
- **WHEN** 40 labelled items are judge-kept and the user marked 34 of them useful
- **THEN** the report shows precision 0.85 for 40 items

#### Scenario: Too few labels
- **WHEN** fewer than 30 labels match current items
- **THEN** the report shows the numbers and the warning "fewer than 30 labels — not a reliable gate"

### Requirement: Usefulness gate

The report SHALL state PASS when precision is at least the configured target
(default 0.8) with at least 30 matching labels, and FAIL otherwise. The command
MUST exit 0 on PASS and 1 on FAIL.

#### Scenario: Gate fails
- **WHEN** precision is 0.7 with 45 labels
- **THEN** the report says FAIL and the command exits 1
