"""lifekit.db — SQLite database initialization and schema management."""

from lifekit.db.schema import init_db, get_connection

__all__ = ["init_db", "get_connection"]
