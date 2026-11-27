from pathlib import Path

import psycopg
from pgvector.psycopg import register_vector

from .config import DATABASE_URL


def init_db() -> None:
    """Create extension, tables and indexes (safe to run every startup)."""
    sql = (Path(__file__).parent / "schema.sql").read_text()
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute(sql)


def get_conn() -> psycopg.Connection:
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    register_vector(conn)
    return conn
