import psycopg2
import pandas as pd
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[1] / "data" / "raw"

conn = psycopg2.connect(
    dbname="smart_access",
    user="postgres",
    password="",  # or your password
    host="localhost",
    port=5432,
)
conn.autocommit = True

def load_table(csv_path, table_name, columns_sql):
    cur = conn.cursor()
    # Create table once if it doesn't exist
    cur.execute(f"create table if not exists {table_name} ({columns_sql});")
    # Empty it for fresh load
    cur.execute(f"truncate table {table_name};")

    df = pd.read_csv(csv_path)
    cols = ",".join(df.columns)
    placeholders = ",".join(["%s"] * len(df.columns))

    for _, row in df.iterrows():
        cur.execute(
            f"insert into {table_name} ({cols}) values ({placeholders})",
            tuple(row.values),
        )
    cur.close()

def main():
    load_table(
        BASE_PATH / "households" / "households.csv",
        "raw_households",
        "household_id int, region text, timezone text",
    )
    load_table(
        BASE_PATH / "devices" / "devices.csv",
        "raw_devices",
        """device_id int,
           household_id int,
           device_type text,
           model text,
           firmware_version text,
           installed_at timestamp""",
    )
    load_table(
        BASE_PATH / "access_events" / "access_events.csv",
        "raw_access_events",
        """event_id text,
           device_id int,
           user_id int,
           event_type text,
           trigger_source text,
           created_at timestamp,
           lat double precision,
           lon double precision""",
    )
    load_table(
        BASE_PATH / "device_health" / "device_health.csv",
        "raw_device_health",
        """device_id int,
           reported_at timestamp,
           battery_pct double precision,
           signal_strength_dbm double precision,
           is_online boolean""",
    )

if __name__ == "__main__":
    main()