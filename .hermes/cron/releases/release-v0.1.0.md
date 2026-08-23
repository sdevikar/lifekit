# Release: v0.1.0 — 2026-07-08 (Phase 0 Complete)

## What Ships
- **Project scaffold:** pyproject.toml, Makefile, .env.example, package layout (lifekit/ sub-packages)
- **Database schema:** SQLite 5 tables + FTS5 virtual table with ai/au/ad triggers via init_db() and get_connection()
- **PDF ingestion:** Sentence-boundary chunking (~2000 chars), duplicate ingest guard, empty-PDF error, TOCTOU safety (pypdf.PdfReader)
- **Plan forge:** Ollama integration + Pydantic PlanResponse validation; configurable teaching methods (socratic, feynman, analogical, spaced_recall); fallback plan generation on invalid LLM responses
- **MCP server:** JSON-RPC over stdio with 3 tools — get_next_task, complete_task, get_plan_status (includes teaching_method in status output)
- **Documentation:** README.md with release log + architecture table + error handling reference; USER_MANUAL.md with step-by-step walkthrough

**Stats:** 11 Python files, ~1,059 lines. All compile cleanly via py_compile. OpenSpec proposal "lifekit-mvp-core-loop" archived to openspec/archives/.

## Caveats / Known Issues
- Zero test coverage yet (pytest tests deferred in tasks.md)
- DB exists at ~/.lifekit/lifekit.db but has no data rows — end-to-end integration not yet tested with live PDF content
- pyproject.toml still uses setuptools (no pypdf2/PyPDF2 pin yet; user must install separately: pip install pypdf ollama pydantic)

## Next Up
- Phase 1: Plan manager / external library connectors  
- Or run integration smoke tests with live PDF data first (verify the full pipeline ingest → forge → MCP works end-to-end)
