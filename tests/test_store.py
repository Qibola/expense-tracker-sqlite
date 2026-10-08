import io
import os
import tempfile
import unittest

from expense_tracker import cli, db, store


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.conn = db.init_db(":memory:")

    def test_add_and_list_newest_first(self):
        store.add_expense(self.conn, 12.5, "Food", "lunch", "2026-10-01")
        store.add_expense(self.conn, 40, "Transport", "", "2026-10-03")
        rows = store.list_expenses(self.conn)
        self.assertEqual([r["date"] for r in rows], ["2026-10-03", "2026-10-01"])
        self.assertEqual(rows[1]["category"], "Food")

    def test_category_reused(self):
        store.add_expense(self.conn, 1, "Food", date="2026-10-01")
        store.add_expense(self.conn, 2, "Food", date="2026-10-02")
        n = self.conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        self.assertEqual(n, 1)

    def test_validation(self):
        with self.assertRaises(ValueError):
            store.add_expense(self.conn, 0, "Food")
        with self.assertRaises(ValueError):
            store.add_expense(self.conn, 5, "Food", date="10/01/2026")
        with self.assertRaises(ValueError):
            store.add_expense(self.conn, 5, "  ")

    def test_delete(self):
        i = store.add_expense(self.conn, 5, "Food", date="2026-10-01")
        self.assertTrue(store.delete_expense(self.conn, i))
        self.assertFalse(store.delete_expense(self.conn, i))
        self.assertEqual(store.list_expenses(self.conn), [])


class CliTests(unittest.TestCase):
    def test_add_list_delete_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.db")
            out = io.StringIO()
            self.assertEqual(cli.main(["--db", path, "add", "9.99", "Food",
                                       "-d", "coffee", "--date", "2026-10-02"], out), 0)
            cli.main(["--db", path, "list"], out)
            self.assertIn("coffee", out.getvalue())
            self.assertIn("9.99", out.getvalue())
            self.assertEqual(cli.main(["--db", path, "delete", "1"], out), 0)
            self.assertEqual(cli.main(["--db", path, "delete", "1"], out), 1)


if __name__ == "__main__":
    unittest.main()
