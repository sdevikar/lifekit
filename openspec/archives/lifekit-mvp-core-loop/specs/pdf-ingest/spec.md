## ADDED Requirements

### Requirement: PDF is parsed and stored in chunks
The system SHALL parse a PDF file from a local path using PyPDF2. The text SHALL be split into chunks of approximately 500 tokens (≈ 2000 characters). Each chunk SHALL be stored as a row in `book_chunks` with its `page_number` and `chunk_index`.

#### Scenario: Successful PDF ingestion
- **WHEN** `ingest_pdf(file_path, title, author)` is called with a valid PDF path
- **THEN** a `books` row is created and all extracted text chunks are stored in `book_chunks`

#### Scenario: Chunk count is accurate
- **WHEN** ingestion completes
- **THEN** `books.chunk_count` equals the number of rows inserted into `book_chunks` for that book_id

### Requirement: Empty or malformed PDFs are handled gracefully
The system SHALL catch `PyPDF2` parse errors and log a warning. If zero text is extracted, the function SHALL raise a `ValueError` with a message indicating the PDF could not be read.

#### Scenario: Unreadable PDF
- **WHEN** `ingest_pdf()` is called with a password-protected or corrupt PDF
- **THEN** a `ValueError` is raised with a human-readable message and no partial data is written to the database

### Requirement: Re-ingesting the same file path is rejected
**Implementation Note:** Use `BEGIN IMMEDIATE` (not default `BEGIN TRANSACTION`/deferred) to lock the table before the EXISTS query. This prevents TOCTOU races between check and insert.

The system SHALL check if a book with the same `file_path` already exists in the `books` table. If it does, ingestion SHALL raise a `FileExistsError` with a hint to delete the existing record first.

#### Scenario: Duplicate ingest attempt
- **WHEN** `ingest_pdf()` is called with a `file_path` that already exists in `books`
- **THEN** a `FileExistsError` is raised and no duplicate records are created

### Requirement: FTS5 index is updated after ingestion
The system SHALL ensure the FTS5 virtual table `book_chunks_fts` reflects all newly inserted chunks immediately after ingestion completes.

#### Scenario: FTS search works immediately after ingest
- **WHEN** `ingest_pdf()` completes and a keyword search is run
- **THEN** chunks containing the keyword are returned without requiring a manual FTS rebuild
