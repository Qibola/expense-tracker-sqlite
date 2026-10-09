"""Command-line interface: python -m expense_tracker.cli <command>."""
import argparse
import sys
from datetime import date

from . import db, store


def build_parser():
    p = argparse.ArgumentParser(prog="expense-tracker",
                                description="Track expenses in SQLite.")
    p.add_argument("--db", default=db.DEFAULT_DB, help="database file path")
    sub = p.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add an expense")
    add.add_argument("amount", type=float)
    add.add_argument("category")
    add.add_argument("-d", "--description", default="")
    add.add_argument("--date", help="YYYY-MM-DD (default: today)")

    ls = sub.add_parser("list", help="list expenses")
    ls.add_argument("-c", "--category", help="only show this category")

    rep = sub.add_parser("report", help="monthly spending by category")
    rep.add_argument("month", nargs="?",
                     help="YYYY-MM (default: current month)")

    rm = sub.add_parser("delete", help="delete an expense by id")
    rm.add_argument("id", type=int)
    return p


def format_table(rows):
    if not rows:
        return "No expenses yet."
    lines = [f"{'ID':>4}  {'Date':<10}  {'Amount':>9}  {'Category':<12}  Description"]
    for r in rows:
        lines.append(f"{r['id']:>4}  {r['date']:<10}  {r['amount']:>9.2f}  "
                     f"{r['category']:<12}  {r['description']}")
    return "\n".join(lines)


def format_report(month, summary):
    if not summary:
        return f"No expenses in {month}."
    lines = [f"Spending for {month}", f"{'Category':<12}  {'Total':>9}"]
    for name, total in summary:
        lines.append(f"{name:<12}  {total:>9.2f}")
    lines.append(f"{'TOTAL':<12}  {sum(t for _, t in summary):>9.2f}")
    return "\n".join(lines)


def main(argv=None, out=sys.stdout):
    args = build_parser().parse_args(argv)
    conn = db.init_db(args.db)
    try:
        if args.command == "add":
            new_id = store.add_expense(conn, args.amount, args.category,
                                       args.description, args.date)
            print(f"Added expense #{new_id}", file=out)
        elif args.command == "list":
            print(format_table(store.list_expenses(conn, args.category)), file=out)
        elif args.command == "report":
            month = args.month or date.today().strftime("%Y-%m")
            print(format_report(month, store.monthly_summary(conn, month)), file=out)
        elif args.command == "delete":
            if store.delete_expense(conn, args.id):
                print(f"Deleted expense #{args.id}", file=out)
            else:
                print(f"No expense with id {args.id}", file=sys.stderr)
                return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
