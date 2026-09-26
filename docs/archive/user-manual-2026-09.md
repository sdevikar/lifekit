# LifeKit — User Manual

This guide walks you through every step of testing Lifekit from scratch. No assumptions about prior setup — follow along line by line.

---

## 1. Verify Ollama Is Running

```bash
ollama list
curl http://localhost:11434/api/version | head -5
```

**Expected output:** A list of downloaded models (e.g., `qwen3.6:latest`) and an API version string. If this fails, start Ollama first (`ollama serve`) and wait a few seconds before retrying.

---

## 2. Clone / Navigate to the Project

```bash
cd /home/swapnil/workspace/projects/lifekit
```

If you haven't pulled the project yet:

```bash
git clone <repo-url> ~/.lifekit/lifekit
cd ~/.lifekit/lifekit
```

---

## 3. Create and Populate the Virtual Environment (First Time Only)

```bash
uv venv .venv
source .venv/bin/activate
pip install pypdf ollama pydantic
```

> ⚠️ **Never use `sudo pip`** or global packages — Lifekit needs to stay isolated.

Verify the environment:

```bash
python -c "import pypdf, ollama, pydantic; print('All deps OK')"
```

---

## 4. Run Your First Book (End-to-End Walkthrough)

### Step A — Bootstrap the Database

```bash
python -m lifekit.db.schema
```

**Expected output:** `Database initialized. Tables: books, book_chunks, book_chunks_fts, plans, tasks, sessions`

A new SQLite file is created at `~/.lifekit/lifekit.db`. On every subsequent run (idempotent), it re-creates tables if missing and does no harm.

---

### Step B — Ingest a PDF Book

Find a PDF to test with:

```bash
# Option 1: Use your system's existing books
ls ~/Downloads/*.pdf | head -5

# Option 2: Download a sample (free public domain book)
wget https://www.gutenberg.org/files/84/84-0.txt -O /tmp/test_book.txt
# Convert to PDF with any tool or use an existing PDF
```

Ingest the PDF (replace path with your file):

```bash
python -m lifekit.store --pdf ~/Downloads/AtomicHabits.pdf
```

**Expected output:**

```
✅ Book ingested successfully!
   Title: AtomicHabits
   Pages: 12
   Chunks: 58
   File size: 431 KB
   Book ID: a1b2c3d4e5f6g7h8
   Stored in: /home/swapnil/.lifekit/lifekit.db (SQLite + FTS5)
```

**What happened under the hood:**
1. `pypdf` extracted text from every page
2. Each page was split into ~2000-character chunks with sentence-boundary detection and 200-char overlap
3. The book record (title, pages, file_path, chunk_count) was inserted into the `books` table
4. Every chunk was inserted into `book_chunks` with FTS5 indexing for keyword search

---

### Step C — Verify the Ingested Data

Check what LifeKit actually stored:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/swapnil/.lifekit/lifekit.db')
books = conn.execute('SELECT id, title, pages, chunk_count FROM books').fetchall()
print('Ingested books:')
for row in books:
    print(f'  ID: {row[0]}')
    print(f'  Title: {row[1]}')
    print(f'  Pages: {row[2]}')
    print(f'  Chunks: {row[3]}')

chunks = conn.execute('SELECT COUNT(*) FROM book_chunks').fetchone()[0]
print(f'\nTotal chunks in database: {chunks}')

fts_search = conn.execute(
    \"SELECT * FROM book_chunks_fts WHERE book_chunks_fts MATCH 'habits' LIMIT 3\"
).fetchall()
print(f'\nFTS5 search for \"habits\": {len(fts_search)} results')
"
```

**Expected output:** A table showing your book's ID, title, pages (12), chunks (58+ depending on PDF), and a few FTS5 search results proving keyword indexing works.

---

### Step D — Generate a Learning Plan

```bash
python -m lifekit.plan_forge.forge --book-id <BOOK_ID> --intent "Finish Atomic Habits in 2 weeks"
```

Replace `<BOOK_ID>` with the value from Step B (e.g., `a1b2c3d4e5f6g7h8`).

**Expected output:**

```
✅ Plan created!
   Plan ID: f9a8b7c6d5e4...
   Duration: 14 days
   Tasks generated: 14
   Saved to: /home/swapnil/.lifekit/lifekit.db (plans, tasks tables)
```

**What happened under the hood:**
1. LifeKit fetched your book's first ~2000 characters as context
2. Sent a structured prompt to Ollama (`qwen3.6:latest`) with your intent + context
3. Parsed the JSON response into `PlanResponse` (Pydantic validates every field)
4. Inserted all 14 tasks as individual rows in the `tasks` table, each linked to the plan via `plan_id`

---

### Step E — Check Your Active Tasks

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/swapnil/.lifekit/lifekit.db')
plans = conn.execute('SELECT id, duration_days, created_at FROM plans ORDER BY rowid DESC LIMIT 1').fetchone()
print(f'Latest plan:')
print(f'  ID: {plans[0]}')
print(f'  Duration: {plans[1]} days')
print(f'  Created: {plans[2]!r}')

tasks = conn.execute(
    'SELECT day_number, title, description[:50], exercise_type FROM tasks WHERE plan_id = \"?\"'.format(plans[0])
).fetchall()

# Actually just show all tasks for the newest plan
latest_plan_id = plans[0]
tasks = conn.execute(
    f'SELECT day_number, title, description[:50], exercise_type FROM tasks WHERE plan_id = \"{latest_plan_id}\" ORDER BY day_number'
).fetchall()

print(f'\nFirst 5 tasks:')
for t in tasks:
    print(f'  Day {t[0]:2d}: [{t[3]:10s}] {t[1]}')
"
```

**Expected output:** A numbered list of your first 5 daily tasks, each showing the day number, exercise type (reading/writing/reflection), and title.

---

### Step F — Complete a Task

Mark one task as done:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/swapnil/.lifekit/lifekit.db')
# Update the first pending task (replace with actual task ID)
conn.execute(
    \"UPDATE tasks SET status='completed' WHERE day_number=1 AND plan_id IN (SELECT id FROM plans ORDER BY rowid DESC LIMIT 1)\",
)
print(f'✅ Day 1 marked complete')
"
```

---

### Step G — Verify Completion Status

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/swapnil/.lifekit/lifekit.db')
plans = conn.execute('SELECT id FROM plans ORDER BY rowid DESC LIMIT 1').fetchone()[0]
total = conn.execute("SELECT COUNT(*) FROM tasks WHERE plan_id=?", (plans,)).fetchone()[0]
completed = conn.execute(
    "SELECT COUNT(*) FROM tasks WHERE plan_id=? AND status='completed'", (plans,)
).fetchone()[0]
percentage = int(completed / total * 100) if total else 0
print(f'📊 Plan progress: {completed}/{total} ({percentage}% complete)')
"
```

**Expected output:** `📊 Plan progress: 1/14 (7% complete)` — or higher if you marked more tasks done in Step F.

---

## 2. Quick-Start Commands Reference

| What | Command |
|------|---------|
| Bootstrap DB | `python -m lifekit.db.schema` |
| Ingest a PDF | `python -m lifekit.store --pdf /path/to/book.pdf` |
| List ingested books | See Step C above (SQLite query) |
| Generate plan | `python -m lifekit.plan_forge.forge --book-id <ID> --intent "..."` |
| Query MCP tools | Start MCP server (`make serve`) and call via your LLM client |
| Complete a task | See Step F above (SQLite UPDATE) |
| Check progress | See Step G above (SQLite query) |

---

## 3. Expected File Locations After Running

```
/home/swapnil/.lifekit/lifekit.db       ← SQLite database (everything persists here)
~/workspace/projects/lifekit/.venv/     ← Virtual environment
~/workspace/projects/lifekit/lifekit/   ← Source code
~/workspace/projects/lifekit/pyproject.toml    ← Python dependencies
~/workspace/projects/lifekit/Makefile             ← Build automation
```

---

## 4. Troubleshooting

| Problem | Fix |
|---------|-----|
| `ollama: command not found` | Install Ollama from https://ollama.com and start it with `ollama serve` |
| `ConnectionRefusedError` during model calls | Ensure Ollama is running: `ollama list` (should show models) |
| "No extractable text in PDF" | The PDF has scanned images instead of embedded text. OCR required. |
| Duplicate ingest error | Run again with a different file path, or drop the existing row manually |
| Ingested book shows 0 pages/chunks | Try a different PDF — some are corrupted or password-protected |
| Plan generation returns "fallback" tasks | Ollama's response wasn't valid JSON. Check model availability and prompt compliance (`qwen3.6:latest` is sometimes looser) |

---

## 5. Data Flow Diagram

```
PDF Book (100 pages)
        │
        ▼
  ┌─────────────┐
  │ PDF Extraction│   pypdf → plain text per page
  └──────┬───────┘
         │
         ▼
  ┌─────────────┐
  │ Chunking (F) │   ~2000 chars/page, sentence-boundary detection
  └──────┬───────┘       + 200-char overlap for context continuity
         │
         ▼
  ┌─────────────┐
  │ SQLite Store │   books table + book_chunks (FTS5 indexed)
  │               │   ~/.lifekit/lifekit.db (idempotent bootstrap)
  └──────┬───────┘
         │
         ▼
     Prompt Builder
    (book title + first ~10 chunks + user intent)
         │
         ▼
  ┌─────────────┐
  │ Ollama       │   ollama.chat(model=qwen3.6:latest) → SMART plan JSON
  └──────┬───────┘
         │
         ▼
  ┌─────────────┐
  │ Pydantic     │   PlanResponse (14 days × N tasks, all fields validated)
  │ Validation   │   Every task gets: day_number, title, description, exercise_type
  └──────┬───────┘
         │
         ▼
  ┌─────────────┐
  │ Tasks &      │   plans table + tasks table (one row per day)
  │ Plan Save    │   status='pending' until you mark complete
  └─────────────┘
```

This is the end-to-end user test guide. Follow Steps 1 through Step G and you'll have verified every component of Lifekit in about 5 minutes with any PDF book on your filesystem.
