"""One-off script to verify the backend can reach Postgres, before wiring a DB client into the app."""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# .env lives at the repo root, not inside backend/ — be explicit about the path
# rather than relying on python-dotenv's upward search, so this works no matter
# which directory you run the script from.
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

conn_info = {
    "host": "localhost",   # the backend isn't containerized yet, so it reaches
    "port": 5432,          # Postgres via the host-mapped port, not the service name
    "dbname": os.environ["POSTGRES_DB"],
    "user": os.environ["POSTGRES_USER"],
    "password": os.environ["POSTGRES_PASSWORD"],
}

with psycopg.connect(**conn_info) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
        print("Connected. Query result:", cur.fetchone())
