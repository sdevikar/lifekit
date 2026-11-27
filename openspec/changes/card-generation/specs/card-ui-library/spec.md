# Spec — card-ui-library

## Purpose

Define the OpenUI components and custom actions that generated feed cards and
drawer surfaces may use, what each one shows, and which state keys and events
it produces, so that code can save the user's work and react to actions.

## ADDED Requirements

### Requirement: Separate libraries

The frontend SHALL define three OpenUI libraries: the existing chat library,
a card library with root `FeedCard`, and a surface library with root `Surface`.
Each library MUST generate its own system prompt for the model.

#### Scenario: Card prompt lists only card components
- **WHEN** the card library prompt is generated
- **THEN** it lists FeedCard, TextContent, Quote, SourceLabel, and OpenButton, and no surface input components

### Requirement: Feed card components

The card library SHALL offer `FeedCard(children)`, `TextContent(text, size)`,
`Quote(text)`, `SourceLabel(label)`, and `OpenButton(label, action)`. The
custom action `@OpenActivity()` MUST send an `OpenActivity` event to the host
and do nothing else.

#### Scenario: Open button event
- **WHEN** the user taps `OpenButton("Try it", @OpenActivity())` on a card
- **THEN** the host receives one event of type `OpenActivity`

### Requirement: Surface input components

The surface library SHALL offer `Checklist(name, items)`, `TextArea(name,
label, placeholder)`, `Scale(name, label, min, max, minLabel, maxLabel)`, and
`Choice(name, label, options, multiple)`. Each MUST store its value in the
renderer state under its `name`.

#### Scenario: Checklist state
- **WHEN** the user ticks steps 1 and 3 of `Checklist("steps", [...4 steps])`
- **THEN** the state holds `steps` = `[true, false, true, false]`

#### Scenario: Restore state
- **WHEN** a surface renders with saved state `{"entry": "Draft text"}`
- **THEN** `TextArea("entry", …)` shows "Draft text"

### Requirement: Surface action components

The surface library SHALL offer `CheckIn(label)` with the custom action
`@CheckIn()`, `DoneButton(label)` with the custom action `@MarkDone()`,
`AskCoach(prompt)` which sends the prompt to the card's conversation, and
`Reveal(label, requires, children)` which hides its children until tapped and
stays disabled while the state field named by `requires` is empty. Revealing
MUST set the state key `revealed` to true.

#### Scenario: Reveal blocked until the user answers
- **WHEN** `Reveal("Show the author's answer", "answer", …)` renders and the `answer` field is empty
- **THEN** the reveal control is disabled

#### Scenario: Reveal sets state
- **WHEN** the user writes an answer and taps reveal
- **THEN** the children show and the state holds `revealed` = true

### Requirement: Required parts for simple surfaces

Every surface SHALL hold a DoneButton. An `insight` surface MUST also hold a
Quote and at least one AskCoach. A `habit` surface MUST also hold a CheckIn. A
`reflect` surface MUST also hold a TextArea named `entry`.

#### Scenario: Habit without a check-in
- **WHEN** a habit surface holds only a DoneButton
- **THEN** validation fails with "missing CheckIn"

### Requirement: Required parts for structured surfaces

A `practice` surface SHALL hold a Checklist named `steps` with one entry per
content step and a TextArea named `notes`. A `worksheet` surface SHALL hold one
input per content field, named by the field id. A `question` surface SHALL hold
a TextArea named `answer` and a Reveal that requires `answer` and holds a Quote.

#### Scenario: Worksheet missing a field
- **WHEN** a worksheet's content has fields `health`, `work`, and `play` and the surface has inputs only for `health` and `work`
- **THEN** validation fails with "missing input for field play"

### Requirement: Theme tokens only

All new components SHALL use the existing `--lk-*` design tokens and no colour
literals, and MUST work in light and dark themes.

#### Scenario: No colour literals
- **WHEN** the new library files are searched for hex colours, `rgb(`, and `hsl(`
- **THEN** no match is found
