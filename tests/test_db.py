import sqlite3
import unittest

from expense_tracker import db


class InitDbTests(unittest.TestCase):
    def test_creates_tables_and_is_idempotent(self):
        conn = db.init_db(":memory:")
        names = {r["name"] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertIn("expenses", names)
        self.assertIn("categories", names)
        conn.executescript(db.SCHEMA_PATH.read_text())  # second run: no error

    def test_rejects_non_positive_amount(self):
        conn = db.init_db(":memory:")
        conn.execute("INSERT INTO categories(name) VALUES ('Food')")
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO expenses(date, amount, category_id) "
                "VALUES ('2026-10-01', -5, 1)")

    def test_foreign_key_enforced(self):
        conn = db.init_db(":memory:")
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO expenses(date, amount, category_id) "
                "VALUES ('2026-10-01', 5, 99)")


if __name__ == "__main__":
    unittest.main()
