# expense-tracker-sqlite

A Python CLI for tracking expenses, backed by a real SQLite database (standard library only — no server).
Planned features: add/list/delete entries, categories, monthly reports, CSV export, and a Plotly spending chart.

## Setup

```
pip install -r requirements.txt   # only needed for the chart step
python -m expense_tracker.db      # creates expenses.db with the schema
```

## Schema

- `categories(id, name UNIQUE)`
- `expenses(id, date, amount > 0, description, category_id -> categories.id)`

See `expense_tracker/schema.sql`.

## Tests

```
python -m unittest discover -s tests -v
```

## Roadmap

- [x] Scaffold: README, requirements, .gitignore, sqlite3 schema init
- [ ] Add / list / delete entry CLI commands
- [ ] Category filtering + monthly summary report
- [ ] CSV export
- [ ] Plotly chart of spending by category/month + polish
