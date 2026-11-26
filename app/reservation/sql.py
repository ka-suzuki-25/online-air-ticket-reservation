"""Small helpers so every use case runs SQL the same safe way.

Every call passes user input as parameters (%s), never by string
formatting, so PyMySQL sends it as a prepared statement and SQL
injection is not possible.
"""
from .database import get_db


def query(sql, args=(), one=False):
    """Run a SELECT. Returns a list of rows, or a single row if one=True."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, args)
        rows = cur.fetchall()
    conn.commit()
    if one:
        return rows[0] if rows else None
    return rows


def execute(sql, args=()):
    """Run an INSERT/UPDATE/DELETE and commit. Returns rows affected."""
    conn = get_db()
    with conn.cursor() as cur:
        n = cur.execute(sql, args)
    conn.commit()
    return n
