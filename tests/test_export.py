import csv
import io
import os
import tempfile
import unittest

from expense_tracker import cli, db, store


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.conn = db.init_db(":memory:")
        store.add_expense(self.conn, 12.5, "Food", "lunch, with tip", "2026-10-01")
        store.add_expense(self.conn, 40, "Transport", 'say "hi"', "2026-10-03")
        store.add_expense(self.conn, 3, "food", "coffee", "2026-10-02")

    def _export(self, category=None):
        buf = io.StringIO(newline="")
        n = store.export_csv(self.conn, buf, category)
        return n, list(csv.reader(io.StringIO(buf.getvalue())))

    def test_header_and_order_oldest_first(self):
        n, rows = self._export()
        self.assertEqual(n, 3)
        self.assertEqual(rows[0], store.CSV_FIELDS)
        self.assertEqual([r[1] for r in rows[1:]],
                         ["2026-10-01", "2026-10-02", "2026-10-03"])

    def test_commas_and_quotes_round_trip(self):
        _, rows = self._export()
        self.assertEqual(rows[1][4], "lunch, with tip")
        self.assertEqual(rows[3][4], 'say "hi"')
        self.assertEqual(rows[1][2], "12.50")

    def test_category_filter_case_insensitive(self):
        n, rows = self._export("FOOD")
        self.assertEqual(n, 2)
        self.assertTrue(all(r[3].lower() == "food" for r in rows[1:]))

    def test_empty_export_has_only_header(self):
        n, rows = self._export("Nothing")
        self.assertEqual((n, rows), (0, [store.CSV_FIELDS]))

    def test_cli_export_writes_file(self):
        with tempfile.TemporaryDirectory() as d:
            dbp, out = os.path.join(d, "t.db"), os.path.join(d, "o.csv")
            cli.main(["--db", dbp, "add", "5", "Food", "--date", "2026-10-05"],
                     out=io.StringIO())
            msg = io.StringIO()
            self.assertEqual(cli.main(["--db", dbp, "export", out], out=msg), 0)
            self.assertIn("Exported 1 expense(s)", msg.getvalue())
            with open(out, newline="") as f:
                self.assertEqual(len(list(csv.reader(f))), 2)


if __name__ == "__main__":
    unittest.main()
