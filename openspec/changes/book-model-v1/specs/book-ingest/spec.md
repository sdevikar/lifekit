# Spec — book-ingest

## Purpose

Give the user one command that turns a book file into everything the feed
needs, and small commands to inspect and correct the book structure.

## ADDED Requirements

### Requirement: One ingest command

`lifekit ingest <file>` SHALL run every registered pipeline stage in a fixed
order for that file and print one summary line per stage. It MUST accept
`--book-id`, `--title`, and `--author`. Without `--title`, the title comes from
the file metadata, else from the file name.

#### Scenario: Ingest a new book
- **WHEN** the user runs `lifekit ingest ~/books/dyl.pdf --book-id dyl`
- **THEN** each stage prints its name, its status, and its counts, and the command exits 0

#### Scenario: Title from metadata
- **WHEN** the file metadata holds the title "Designing Your Life" and no `--title` is given
- **THEN** the book row has the title "Designing Your Life"

### Requirement: Stage order and re-runs

Stages SHALL run in the order `structure`, `items`, `cards`; a stage that is
not yet built is skipped with a note. `lifekit ingest --book <id> --from
<stage>` MUST re-run that stage and every later stage for a book that is
already ingested, reading the file path from the book row.

#### Scenario: Re-run from a stage
- **WHEN** the user runs `lifekit ingest --book dyl --from cards`
- **THEN** only the `cards` stage runs

#### Scenario: Unknown stage
- **WHEN** the user runs `lifekit ingest --book dyl --from summary`
- **THEN** the command exits non-zero and lists the valid stage names

### Requirement: Stop on first failure

If a stage fails, the ingest command SHALL stop, print the stage name and the
error, and exit non-zero. Stages that already finished MUST keep their results.

#### Scenario: Model unreachable during items
- **WHEN** the `items` stage cannot reach the model server
- **THEN** the command prints "items: failed — <error>", exits 1, and the structure rows stay stored

### Requirement: Inspect sections

`lifekit book sections <book_id>` SHALL print every section in reading order
with its index, an indent for its depth, its kind, its title, its passage count,
and its character count.

#### Scenario: Print the tree
- **WHEN** the user runs `lifekit book sections dyl`
- **THEN** each section prints on one line, for example `  3  body  Chapter 1: Start Where You Are  42 passages  31200 chars`

### Requirement: Correct a section kind

`lifekit book set-kind <book_id> <section_idx> <front|body|back>` SHALL set the
kind of that section and of its children, and store the correction so that
re-ingest keeps it. An unknown book, index, or kind MUST give an error and
change nothing.

#### Scenario: Mark a preface as front matter
- **WHEN** the user runs `lifekit book set-kind dyl 2 front`
- **THEN** section 2 and its children have kind front

#### Scenario: Bad kind
- **WHEN** the user runs `lifekit book set-kind dyl 2 appendix`
- **THEN** the command exits non-zero with "kind must be front, body, or back"
