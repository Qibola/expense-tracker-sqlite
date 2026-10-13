import io
import os
import tempfile
import unittest

from expense_tracker import chart, cli, db, store

try:
    import plotly  # noqa: F401
    HAVE_PLOTLY = True
except ImportError:
    HAVE_PLOTLY = False


class ChartTests(unittest.TestCase):
    def setUp(self):
        self.conn = db.init_db(":memory:")
        store.add_expense(self.conn, 10, "Food", "", "2026-09-05")
        store.add_expense(self.conn, 5, "food", "", "2026-09-20")
        store.add_expense(self.conn, 40, "Transport", "", "2026-10-03")

    def test_spending_by_month_category(self):
        self.assertEqual(store.spending_by_month_category(self.conn),
                         [("2026-09", "Food", 15), ("2026-10", "Transport", 40)])

    def test_chart_data_shape(self):
        series, months = chart.chart_data(self.conn)
        self.assertEqual(months, ["2026-09", "2026-10"])
        self.assertEqual(series["Food"], {"2026-09": 15})
        self.assertEqual(series["Transport"], {"2026-10": 40})

    def test_empty_db_raises(self):
        empty = db.init_db(":memory:")
        if HAVE_PLOTLY:
            with self.assertRaises(ValueError):
                chart.build_figure(empty)

    @unittest.skipUnless(HAVE_PLOTLY, "plotly not installed")
    def test_write_chart_creates_html(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "sub", "spending.html")
            with tempfile.NamedTemporaryFile(suffix=".db", dir=d, delete=False) as f:
                dbpath = f.name
            conn = db.init_db(dbpath)
            store.add_expense(conn, 10, "Food", "", "2026-09-05")
            conn.close()
            self.assertEqual(cli.main(["--db", dbpath, "chart", path], out=io.StringIO()), 0)
            html = open(path, encoding="utf-8").read()
            self.assertIn("Monthly spending by category", html)
            self.assertIn("Food", html)


if __name__ == "__main__":
    unittest.main()
