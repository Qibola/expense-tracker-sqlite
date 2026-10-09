"""Data-access functions: add, list, delete and summarise expenses."""
from datetime import date as _date


def _validate_date(value):
    """Return value if it's a real YYYY-MM-DD date, else raise ValueError."""
    try:
        _date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"invalid date {value!r}; use YYYY-MM-DD") from None
    return value


def get_or_create_category(conn, name):
    """Return the id of the category (case-insensitive), creating it if needed."""
    name = name.strip()
    if not name:
        raise ValueError("category name cannot be empty")
    row = conn.execute(
        "SELECT id FROM categories WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
    if row:  # reuse existing category regardless of letter case
        return row["id"]
    with conn:
        cur = conn.execute("INSERT INTO categories(name) VALUES (?)", (name,))
    return cur.lastrowid


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


def list_expenses(conn, category=None):
    """Return expenses (newest first) with their category name.

    If ``category`` is given, only that category is returned (case-insensitive).
    """
    sql = ("SELECT e.id, e.date, e.amount, e.description, c.name AS category "
           "FROM expenses e JOIN categories c ON c.id = e.category_id ")
    params = ()
    if category is not None:
        sql += "WHERE c.name = ? COLLATE NOCASE "
        params = (category.strip(),)
    sql += "ORDER BY e.date DESC, e.id DESC"
    return conn.execute(sql, params).fetchall()


def monthly_summary(conn, month):
    """Total spending per category for a month ('YYYY-MM'), biggest first.

    Returns a list of (category, total) tuples.
    """
    try:
        _date.fromisoformat(month + "-01")
    except (TypeError, ValueError):
        raise ValueError(f"invalid month {month!r}; use YYYY-MM") from None
    rows = conn.execute(
        "SELECT c.name AS category, SUM(e.amount) AS total "
        "FROM expenses e JOIN categories c ON c.id = e.category_id "
        "WHERE substr(e.date, 1, 7) = ? "
        "GROUP BY c.id ORDER BY total DESC, c.name", (month,)).fetchall()
    return [(r["category"], r["total"]) for r in rows]


def delete_expense(conn, expense_id):
    """Delete an expense by id. Returns True if a row was removed."""
    with conn:
        cur = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    return cur.rowcount > 0
