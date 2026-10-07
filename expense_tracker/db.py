"""Database connection and schema initialisation."""
import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
DEFAULT_DB = "expenses.db"


def connect(db_path=DEFAULT_DB):
    """Open a connection with foreign keys enforced and rows as dict-likes."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=DEFAULT_DB):
    """Create the tables if they don't exist yet. Safe to call repeatedly."""
    conn = connect(db_path)
    with conn:  # commits on success, rolls back on error
        conn.executescript(SCHEMA_PATH.read_text())
    return conn


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB
    init_db(path).close()
    print(f"Initialised database at {path}")
