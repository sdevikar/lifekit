## ADDED Requirements

### Requirement: SQLite database is initialized idempotently
The system SHALL create the database file and apply all schema migrations when `init_db()` is called. Running `init_db()` multiple times on an existing database SHALL be safe (idempotent).

#### Scenario: First-time initialization
- **WHEN** `init_db()` is called and no database file exists
- **THEN** the database file is created and all four tables exist: `books`, `book_chunks`, `plans`, `tasks`, `sessions`

#### Scenario: Re-initialization on existing database
- **WHEN** `init_db()` is called and tables already exist
- **THEN** no error is raised and no data is lost

### Requirement: books table stores book metadata
The system SHALL maintain a `books` table with columns: `id` (TEXT PRIMARY KEY, UUID), `title` TEXT NOT NULL, `author` TEXT, `file_path` TEXT NOT NULL, `ingested_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, `chunk_count` INTEGER DEFAULT 0.

#### Scenario: Book record is created on ingest
- **WHEN** a PDF is ingested successfully
- **THEN** a row is inserted into `books` with a generated UUID and the correct file path

### Requirement: book_chunks table enables full-text search
The system SHALL maintain a `book_chunks` table with columns: `id` INTEGER PRIMARY KEY, `book_id` TEXT REFERENCES books(id), `chunk_index` INTEGER, `content` TEXT NOT NULL, `page_number` INTEGER. A FTS5 virtual table `book_chunks_fts` SHALL index the `content` column.

**Implementation Note:** FTS5 virtual tables require explicit trigger population. Use:
```sql
CREATE TRIGGER book_chunks_ai AFTER INSERT ON book_chunks BEGIN
  INSERT INTO book_chunks_fts(rowid, content) VALUES (new.rowid, new.content);
END;
CREATE TRIGGER book_chunks_au AFTER UPDATE ON book_chunks BEGIN
  INSERT INTO book_chunks_fts(book_chunks_fts, rowid, content) VALUES('delete', old.rowid);
  INSERT INTO book_chunks_fts(rowid, content) VALUES (new.rowid, new.content);
END;
CREATE TRIGGER book_chunks_ad AFTER DELETE ON book_chunks BEGIN
  INSERT INTO book_chunks_fts(book_chunks_fts, rowid, content) VALUES('delete', old.rowid);
END;
```
Without these triggers the FTS5 index will be stale after inserts/updates/deletes.

#### Scenario: FTS search returns relevant chunks
- **WHEN** a keyword search is performed via `SELECT * FROM book_chunks_fts WHERE content MATCH ?`
- **THEN** chunks containing the keyword are returned ranked by relevance

### Requirement: plans table stores generated learning plans
The system SHALL maintain a `plans` table with columns: `id` TEXT PRIMARY KEY (UUID), `book_id` TEXT REFERENCES books(id), `user_intent` TEXT NOT NULL, `duration_weeks` INTEGER NOT NULL, `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP.

#### Scenario: Plan record is created after forge
- **WHEN** `forge_plan()` completes successfully
- **THEN** a row is inserted into `plans` linking to the book and containing the user intent string

### Requirement: tasks table stores individual plan tasks
The system SHALL maintain a `tasks` table with columns: `id` INTEGER PRIMARY KEY, `plan_id` TEXT REFERENCES plans(id), `day_number` INTEGER NOT NULL, `title` TEXT NOT NULL, `description` TEXT, `estimated_minutes` INTEGER, `exercise_type` TEXT, `context_source` TEXT, `status` TEXT CHECK(status IN ('pending', 'complete', 'skipped')) DEFAULT 'pending', `completed_at` TIMESTAMP.

#### Scenario: Tasks are ordered by day
- **WHEN** `get_next_task()` is called
- **THEN** the lowest day_number pending task is returned first

#### Scenario: Task completion updates status
- **WHEN** `complete_task(task_id)` is called
- **THEN** the task's `status` is set to 'complete' and `completed_at` is set to current timestamp

### Requirement: sessions table logs MCP interactions
The system SHALL maintain a `sessions` table with columns: `id` INTEGER PRIMARY KEY, `task_id` INTEGER REFERENCES tasks(id), `notes` TEXT, `started_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP.

#### Scenario: Session is logged on task completion
- **WHEN** `complete_task(task_id, notes)` is called
- **THEN** a row is inserted into `sessions` with the task_id and any notes provided
