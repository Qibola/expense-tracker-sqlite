"""Command-line interface: python -m expense_tracker.cli <command>."""
import argparse
import sys

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

    sub.add_parser("list", help="list all expenses")

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


def main(argv=None, out=sys.stdout):
    args = build_parser().parse_args(argv)
    conn = db.init_db(args.db)
    try:
        if args.command == "add":
            new_id = store.add_expense(conn, args.amount, args.category,
                                       args.description, args.date)
            print(f"Added expense #{new_id}", file=out)
        elif args.command == "list":
            print(format_table(store.list_expenses(conn)), file=out)
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
