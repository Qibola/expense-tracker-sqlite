-- Categories are stored once and referenced by expenses.
CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS expenses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT NOT NULL,                      -- ISO format: YYYY-MM-DD
    amount      REAL NOT NULL CHECK (amount > 0),
    description TEXT NOT NULL DEFAULT '',
    category_id INTEGER NOT NULL REFERENCES categories(id)
);

CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
