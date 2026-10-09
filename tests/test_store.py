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


class FilterAndSummaryTests(unittest.TestCase):
    def setUp(self):
        self.conn = db.init_db(":memory:")
        store.add_expense(self.conn, 10, "Food", date="2026-10-01")
        store.add_expense(self.conn, 5.5, "food", date="2026-10-09")
        store.add_expense(self.conn, 40, "Transport", date="2026-10-03")
        store.add_expense(self.conn, 99, "Food", date="2026-09-30")

    def test_filter_by_category_case_insensitive(self):
        rows = store.list_expenses(self.conn, "FOOD")
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(r["category"].lower() == "food" for r in rows))
        self.assertEqual(store.list_expenses(self.conn, "Nope"), [])

    def test_monthly_summary(self):
        self.assertEqual(store.monthly_summary(self.conn, "2026-10"),
                         [("Transport", 40), ("Food", 15.5)])
        self.assertEqual(store.monthly_summary(self.conn, "2026-09"),
                         [("Food", 99)])
        self.assertEqual(store.monthly_summary(self.conn, "2025-01"), [])

    def test_summary_rejects_bad_month(self):
        with self.assertRaises(ValueError):
            store.monthly_summary(self.conn, "2026-13")


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

    def test_list_filter_and_report(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.db")
            sink = io.StringIO()
            cli.main(["--db", path, "add", "10", "Food", "--date", "2026-10-01"], sink)
            cli.main(["--db", path, "add", "40", "Transport", "--date", "2026-10-02"], sink)
            out = io.StringIO()
            cli.main(["--db", path, "list", "-c", "food"], out)
            self.assertIn("Food", out.getvalue())
            self.assertNotIn("Transport", out.getvalue())
            out = io.StringIO()
            self.assertEqual(cli.main(["--db", path, "report", "2026-10"], out), 0)
            self.assertIn("50.00", out.getvalue())
            self.assertEqual(cli.main(["--db", path, "report", "oct"], io.StringIO()), 1)


if __name__ == "__main__":
    unittest.main()
