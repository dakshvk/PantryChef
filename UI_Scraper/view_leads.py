import argparse
import sqlite3
from pathlib import Path


DB_PATH = Path("leads.db")


def parse_args():
    parser = argparse.ArgumentParser(description="View leads.db stats and recent rows.")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of recent rows to display (default: 10).",
    )
    parser.add_argument(
        "--pending-only",
        action="store_true",
        help="Show only rows where ai_processed = 0.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not DB_PATH.exists():
        print("leads.db not found. Run Landscape.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    total = cursor.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    pending = cursor.execute(
        "SELECT COUNT(*) FROM leads WHERE ai_processed = 0"
    ).fetchone()[0]
    processed = cursor.execute(
        "SELECT COUNT(*) FROM leads WHERE ai_processed = 1"
    ).fetchone()[0]

    print(f"Total leads: {total}")
    print(f"Pending AI audit: {pending}")
    print(f"Processed: {processed}")

    if args.pending_only:
        rows = cursor.execute(
            """
            SELECT id, name, website, ai_processed
            FROM leads
            WHERE ai_processed = 0
            ORDER BY id DESC
            LIMIT ?
            """,
            (args.limit,),
        ).fetchall()
    else:
        rows = cursor.execute(
            """
            SELECT id, name, website, ai_processed
            FROM leads
            ORDER BY id DESC
            LIMIT ?
            """,
            (args.limit,),
        ).fetchall()

    if rows:
        if args.pending_only:
            print(f"\nRecent pending leads (latest {args.limit}):")
        else:
            print(f"\nRecent leads (latest {args.limit}):")
        for lead_id, name, website, ai_processed in rows:
            status = "processed" if ai_processed == 1 else "pending"
            print(f"- #{lead_id} | {name} | {website} | {status}")
    else:
        print("\nNo leads found in database yet.")

    conn.close()


if __name__ == "__main__":
    main()
