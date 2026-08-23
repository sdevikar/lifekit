## ADDED Requirements

### Requirement: Project uses Poetry for dependency management
The system SHALL define all Python dependencies in `pyproject.toml` using Poetry. The minimum Python version SHALL be 3.11. Dependencies SHALL include: `fastmcp`, `pypdf2`, `ollama`, `pydantic`, `python-dotenv`.

#### Scenario: Fresh checkout installs cleanly
- **WHEN** a developer runs `poetry install` in the project root
- **THEN** all dependencies install without error and `python -m lifekit.mcp.server` is importable

#### Scenario: Missing dependency is explicit
- **WHEN** a required library is missing from `pyproject.toml`
- **THEN** `poetry install` fails with a clear error naming the missing package

### Requirement: Makefile provides standard dev targets
The system SHALL include a `Makefile` with targets: `bootstrap`, `ingest`, `forge`, `serve`, `test`. Each target SHALL print its purpose when invoked with no args.

#### Scenario: Developer runs make bootstrap
- **WHEN** developer runs `make bootstrap`
- **THEN** the SQLite database file is created at the path specified by `LIFEKIT_DB` env var (default `~/.lifekit/lifekit.db`) and schema migrations are applied

#### Scenario: Developer runs make ingest
- **WHEN** developer runs `make ingest PDF=path/to/book.pdf`
- **THEN** the PDF is parsed and chunks are stored in the `books` and `book_chunks` tables

### Requirement: Environment configuration via .env file
The system SHALL read configuration from a `.env` file (or environment variables) using `python-dotenv`. An `.env.example` SHALL be committed to the repo documenting all variables.

#### Scenario: .env.example documents all variables
- **WHEN** developer copies `.env.example` to `.env` without changes
- **THEN** the system starts with sensible defaults (model=qwen3.6:latest, db path=~/.lifekit/lifekit.db)

### Requirement: Package is importable as lifekit
The system SHALL be structured so `from lifekit.db.schema import init_db` and `from lifekit.mcp.server import mcp` work after `poetry install`.

#### Scenario: Package import works
- **WHEN** developer runs `python -c "import lifekit"`
- **THEN** no ImportError is raised
