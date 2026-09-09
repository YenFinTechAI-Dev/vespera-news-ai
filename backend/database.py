"""Neon/PostgreSQL connection. Never log connection strings or driver errors."""
import os
from pathlib import Path
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env", override=False)


class DatabaseUnavailable(RuntimeError):
    pass


@contextmanager
def connection():
    url = os.getenv("DATABASE_URL", "").strip()
    if not url or "REPLACE_ME" in url:
        raise DatabaseUnavailable("Database is not configured")
    try:
        with psycopg.connect(
            url, connect_timeout=10, row_factory=dict_row,

        ) as conn:
            conn.execute("SET statement_timeout = '10s'")
            conn.commit()
            yield conn
    except psycopg.Error:
        raise DatabaseUnavailable("Database is unavailable") from None


def initialize_database():
    migrations_dir = BACKEND_DIR / "src" / "db" / "migrations"
    files = sorted(migrations_dir.glob("*.sql"))
    with connection() as conn:
        # Serialize migration attempts, making concurrent startup safe.
        conn.execute("SELECT pg_advisory_xact_lock(736521904)")
        conn.execute(
            """CREATE TABLE IF NOT EXISTS schema_migrations (
                filename TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        applied = {row["filename"] for row in conn.execute("SELECT filename FROM schema_migrations").fetchall()}
        for path in files:
            if path.name in applied:
                continue
            conn.execute(path.read_text(encoding="utf-8"), prepare=False)
            conn.execute("INSERT INTO schema_migrations (filename) VALUES (%s)", [path.name])
