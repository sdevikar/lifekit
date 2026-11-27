# Spec — book-model

## Purpose

Turn a book file into a deterministic, stable structure — book, sections, and
passages — that every later stage can point into, and record which pipeline run
produced each derived row.

## ADDED Requirements

### Requirement: Supported formats

The system SHALL accept `.pdf` and `.epub` files. It MUST refuse any other
extension, an encrypted or password-protected file, and a file with less than
200 characters of extractable text, each with an error message that names the
reason.

#### Scenario: EPUB accepted
- **WHEN** the user ingests a DRM-free `.epub` with a table of contents
- **THEN** the book, its sections, and its passages are stored

#### Scenario: Scanned PDF refused
- **WHEN** the user ingests a PDF whose pages are images with no text layer
- **THEN** ingest stops with "No extractable text (image-only scan?)" and stores nothing

#### Scenario: Unsupported format refused
- **WHEN** the user ingests `book.mobi`
- **THEN** ingest stops with "Supported formats: .pdf, .epub"

### Requirement: Book identity

The book id SHALL be the first 16 hex characters of the SHA-256 of the file
bytes, unless the user passes an explicit id. The same file at two different
paths MUST get the same id.

#### Scenario: Same file, different path
- **WHEN** the same PDF is ingested once as `./dyl.pdf` and once as `/home/u/books/dyl.pdf`
- **THEN** both runs use the same book id and the second run replaces the first run's structure

#### Scenario: Explicit id
- **WHEN** the user ingests a file with book id `dyl`
- **THEN** all rows use the book id `dyl`

### Requirement: Sections tree

The system SHALL build one section per table-of-contents entry at every level.
Each section MUST have a reading-order index unique within the book, the index
of its parent (none for top level), a depth, a title, a page range, and its own
text: the text from its heading to the next entry at any level.

#### Scenario: Nested TOC
- **WHEN** a book has a TOC with "Chapter 1" and child entries "1.1" and "1.2"
- **THEN** three sections are stored, "1.1" and "1.2" have parent "Chapter 1", and "Chapter 1" holds only the text before "1.1"

#### Scenario: No TOC
- **WHEN** a PDF has no TOC
- **THEN** sections come from detected headings, or from fixed 15-page ranges if no headings are found, all at depth 1

### Requirement: Section kind

Each section SHALL have kind `front`, `body`, or `back`. A top-level section
gets its kind from the configured title list; an unmatched title is `body`.
A child section MUST have the kind of its top-level parent. A user correction
MUST override the title list and MUST survive re-ingest of the same book.

#### Scenario: Front and back matter detected
- **WHEN** a book has top-level sections "Dedication", "Contents", "Introduction", "Chapter 1", "Notes", and "Acknowledgments"
- **THEN** "Dedication" and "Contents" are front, "Introduction" and "Chapter 1" are body, and "Notes" and "Acknowledgments" are back

#### Scenario: Correction survives re-ingest
- **WHEN** the user sets "Preface" to front and then re-ingests the same file
- **THEN** "Preface" is still front

### Requirement: Passages

The system SHALL split each section's text into passages of about one paragraph,
in reading order. Each passage MUST have the id `<book_id>:<section_idx>:<n>`,
its text, its start and end character offsets in the section text, and its
first page. The passage texts joined by a blank line MUST equal the section text.

#### Scenario: Offsets point into the section
- **WHEN** a passage has offsets 120 and 480
- **THEN** characters 120 to 480 of its section text equal the passage text

#### Scenario: Short heading line joins the next paragraph
- **WHEN** a 40-character line without end punctuation is followed by a paragraph
- **THEN** the line and the paragraph are one passage

### Requirement: Page furniture removed

The system SHALL remove running headers, running footers, and page numbers
from section text. A line counts as furniture when it sits in the top or
bottom 7% of the page and repeats, ignoring digits, on at least 30% of pages,
or when it holds only a page number.

#### Scenario: Running header removed
- **WHEN** every page starts with the line "DESIGNING YOUR LIFE" and a page number
- **THEN** no passage contains "DESIGNING YOUR LIFE" as a header line

### Requirement: Deterministic structure

Ingesting the same file twice with the same settings SHALL produce identical
sections and passages, including ids, offsets, and kinds.

#### Scenario: Re-ingest is stable
- **WHEN** a book is ingested twice
- **THEN** a dump of its sections and passages rows is byte-identical between the runs

### Requirement: Passage search index

The system SHALL keep a full-text index over passage text, filterable by book.
Re-ingesting a book MUST replace that book's index entries without touching
other books.

#### Scenario: Search within one book
- **WHEN** two books are ingested and the index is searched for "prototype" in book A
- **THEN** only passages of book A are returned

### Requirement: Run records

Every pipeline stage run SHALL create one run record with a unique id, the book
id, the stage name, the model name (or none), a hash of the prompt text (or
none), the parameters, a status of `running`, `ok`, or `failed`, start and end
times, and row counts. A failed stage MUST leave its run marked `failed` with the
error text.

#### Scenario: Structure run recorded
- **WHEN** the structure stage finishes for a book
- **THEN** one run with stage `structure`, status `ok`, and the section and passage counts exists

#### Scenario: Failed stage recorded
- **WHEN** a stage raises an error
- **THEN** its run has status `failed` and holds the error message
