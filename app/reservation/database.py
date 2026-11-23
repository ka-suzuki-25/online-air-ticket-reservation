
import os
import sqlite3
from flask import current_app, g


def get_db():
    """Return a database connection for the current request."""

    if "db" not in g:
        database_path = os.path.join(
            current_app.instance_path,
            "users.sqlite3"
        )

        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(error=None):
    """Close the current request's database connection."""

    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db(app):
    """Create the user table if it does not already exist."""

    database_path = os.path.join(
        app.instance_path,
        "users.sqlite3"
    )

    os.makedirs(app.instance_path, exist_ok=True)

    connection = sqlite3.connect(database_path)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

    app.teardown_appcontext(close_db)
