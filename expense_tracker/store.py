"""Data-access functions: add, list and delete expenses."""
from datetime import date as _date


def _validate_date(value):
    """Return value if it's a real YYYY-MM-DD date, else raise ValueError."""
    try:
        _date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"invalid date {value!r}; use YYYY-MM-DD") from None
    return value


def get_or_create_category(conn, name):
    """Return the id of the category, creating it if needed."""
    name = name.strip()
    if not name:
        raise ValueError("category name cannot be empty")
    with conn:
        conn.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name,))
    return conn.execute(
        "SELECT id FROM categories WHERE name = ?", (name,)).fetchone()["id"]


def add_expense(conn, amount, category, description="", date=None):
    """Insert an expense and return its new id."""
    if amount <= 0:
        raise ValueError("amount must be greater than 0")
    date = _validate_date(date or _date.today().isoformat())
    category_id = get_or_create_category(conn, category)
    with conn:
        cur = conn.execute(
            "INSERT INTO expenses(date, amount, description, category_id) "
            "VALUES (?, ?, ?, ?)",
            (date, amount, description, category_id))
    return cur.lastrowid


def list_expenses(conn):
    """Return all expenses (newest first) joined with their category name."""
    return conn.execute(
        "SELECT e.id, e.date, e.amount, e.description, c.name AS category "
        "FROM expenses e JOIN categories c ON c.id = e.category_id "
        "ORDER BY e.date DESC, e.id DESC").fetchall()


def delete_expense(conn, expense_id):
    """Delete an expense by id. Returns True if a row was removed."""
    with conn:
        cur = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    return cur.rowcount > 0
