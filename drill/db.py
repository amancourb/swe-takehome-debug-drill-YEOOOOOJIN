from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import psycopg

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://drill:drill@localhost:5433/drill"
)

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


@contextmanager
def connect() -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()


def reset_schema() -> None:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(SCHEMA_PATH.read_text())
        conn.commit()
