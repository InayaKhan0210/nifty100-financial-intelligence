import sqlite3
from pathlib import Path
import pandas as pd

from src.etl.loader import load_core_datasets

DB_PATH = Path("data/database/nifty100.db")


def load_to_database():
    datasets = load_core_datasets()

    conn = sqlite3.connect(DB_PATH)

    audit = []

    for table_name, df in datasets.items():

        print(f"Loading {table_name}...")

        rows_before = len(df)

        # Replace existing table contents
        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False
        )

        rows_after = pd.read_sql(
            f"SELECT COUNT(*) AS total FROM {table_name}",
            conn
        ).iloc[0]["total"]

        audit.append({
            "table": table_name,
            "rows_loaded": rows_after
        })

        print(f"Loaded {rows_after} rows.")

    audit_df = pd.DataFrame(audit)

    audit_df.to_csv(
        "load_audit.csv",
        index=False
    )

    conn.close()

    print("\nDatabase loading completed.")
    print("load_audit.csv generated.")


if __name__ == "__main__":
    load_to_database()