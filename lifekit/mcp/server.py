"""Lifekit MCP server — JSON-RPC over stdio transport.

Usage as a service (MCP client integration):
    python -m lifekit.mcp.server   # blocks, waiting for MCP client input on stdin/stdout
"""
import json
import sys
import sqlite3
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # Add project root to path
from lifekit.db.schema import get_connection


def _send_result(id: int | None, result: dict[str, Any]) -> None:
    """Send JSON-RPC success response back to client via stdout."""
    resp = {
        "jsonrpc": "2.0",
        "id": id,
        "result": result,
    }
    sys.stdout.write(json.dumps(resp) + chr(10))   # newline separator
    sys.stdout.flush()


def _send_error(id: int | None, code: int, message: str) -> None:
    """Send JSON-RPC error response back to client."""
    resp = {
        "jsonrpc": "2.0",
        "id": id,
        "error": {"code": code, "message": message},
    }
    sys.stdout.write(json.dumps(resp) + chr(10))
    sys.stdout.flush()


def handle_get_next_task(params: dict[str, Any] | None = None, id: int | None = None) -> None:
    """Get the next pending task across all plans (or specified plan)."""
    db_path = Path.home() / ".lifekit" / "lifekit.db"
    if not db_path.exists():
        _send_error(id, -32000, "Database not found. Run 'make bootstrap' first.")
        return
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.execute(
            """SELECT t.id, t.day_number, t.title, t.description, 
                      t.estimated_minutes, t.exercise_type, t.context_source
              FROM tasks t
              JOIN plans p ON p.id = t.plan_id
              WHERE t.status = 'pending'
                AND (p.duration_weeks * 7) >= t.day_number
              ORDER BY t.day_number ASC, t.id ASC
              LIMIT 1"""
        )
        row = cur.fetchone()
        if row is None:
            _send_result(id, {"ok": False, "error": "No pending tasks found."})
            return
        result = {
            "task_id": row[0],
            "day_number": row[1],
            "title": row[2],
            "description": row[3],
            "estimated_minutes": row[4],
            "exercise_type": row[5],
            "context_source": row[6],
        }
        _send_result(id, result)
    except sqlite3.Error as e:
        _send_error(id, -32001, f"Database error: {e!s}")


def handle_complete_task(params: dict[str, Any] | None = None, id: int | None = None) -> None:
    """Mark task as complete and log session."""
    if not params or "task_id" not in params:
        _send_error(id, -32602, "Missing 'task_id' parameter")
        return
    task_id = params["task_id"]
    notes = params.get("notes", "")
    db_path = Path.home() / ".lifekit" / "lifekit.db"
    conn = sqlite3.connect(str(db_path))
    try:
        task_row = conn.execute(
            "SELECT id, status FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if task_row is None:
            _send_result(id, {"ok": False, "error": "task_not_found"})
            return
        if task_row[1] == "complete":
            _send_result(id, {"ok": False, "error": "task_already_completed"})
            return
        conn.execute(
            "UPDATE tasks SET status = 'complete', completed_at = datetime('now') WHERE id = ?",
            (task_id,),
        )
        conn.execute(
            "INSERT INTO sessions (task_id, notes) VALUES (?, ?)",
            (task_id, notes),
        )
        conn.commit()
        _send_result(id, {"ok": True, "message": f"Task {task_id} marked as complete."})
    except sqlite3.Error as e:
        _send_error(id, -32001, f"Database error: {e!s}")


def handle_get_plan_status(params: dict[str, Any] | None = None, id: int | None = None) -> None:
    """Get aggregated plan status."""
    db_path = Path.home() / ".lifekit" / "lifekit.db"
    conn = sqlite3.connect(str(db_path))
    try:
        if not params or "plan_id" not in params:
            # Use most recent plan
            row = conn.execute(
                """SELECT p.id, b.title, p.user_intent, p.teaching_method,
                          COUNT(t2.id) as total_tasks,
                          SUM(CASE WHEN t2.status='complete' THEN 1 ELSE 0 END) as complete_count
                   FROM plans p
                   JOIN books b ON p.book_id = b.id
                   LEFT JOIN tasks t2 ON t2.plan_id = p.id
                   GROUP BY p.id
                   ORDER BY p.created_at DESC
                   LIMIT 1"""
            ).fetchone()
            if row is None:
                _send_result(id, {"ok": False, "error": "no_plan_found"})
                return
        else:
            plan_id = params["plan_id"]
            row = conn.execute(
                """SELECT p.id, b.title, p.user_intent, p.teaching_method,
                          COUNT(t2.id) as total_tasks,
                          SUM(CASE WHEN t2.status='complete' THEN 1 ELSE 0 END) as complete_count
                   FROM plans p
                   JOIN books b ON p.book_id = b.id
                   LEFT JOIN tasks t2 ON t2.plan_id = p.id
                   WHERE p.id = ?
                   GROUP BY p.id""",
                (plan_id,),
            ).fetchone()
            if row is None:
                _send_result(id, {"ok": False, "error": "no_plan_found"})
                return

        plan_id, book_title, user_intent, teaching_method, total_tasks, complete_count = row
        pending = max(0, total_tasks - complete_count)
        pct = round((complete_count / total_tasks * 100), 1) if total_tasks > 0 else 0
        _send_result(id, {
            "plan_id": plan_id,
            "book_title": book_title,
            "user_intent": user_intent,
            "teaching_method": teaching_method,
            "total_tasks": total_tasks,
            "complete_count": complete_count or 0,
            "pending_tasks": pending,
            "completion_percentage": pct,
        })
    except sqlite3.Error as e:
        _send_error(id, -32001, f"Database error: {e!s}")


def handle_message(msg: dict[str, Any]) -> None:
    """Route an incoming MCP request to the appropriate handler."""
    method = msg.get("method")
    params = msg.get("params")
    req_id = msg.get("id", 1)
    
    handlers = {
        "get_next_task": handle_get_next_task,
        "complete_task": handle_complete_task, 
        "get_plan_status": handle_get_plan_status,
    }
    handler = handlers.get(method, lambda **kw: _send_error(req_id, -32601, f"Unknown method: {method}"))
    handler(params=params, id=req_id)


if __name__ == "__main__":
    """Main loop — read JSON-RPC messages from stdin until EOF."""
    sys.stderr.write("[LifeKit MCP server ready.\n")  # startup message to stderr
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            handle_message(msg)
        except json.JSONDecodeError:
            _send_error(None, -32700, "Invalid JSON")

