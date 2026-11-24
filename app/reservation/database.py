
import os
import sqlite3

from flask import current_app, g


def get_db():
    """Get the SQLite database connection for the current request."""

    if "db" not in g:
        database_path = os.path.join(
            current_app.instance_path,
            "users.sqlite3"
        )

        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(error=None):
    """Close the database connection after the request."""

    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db(app):
    """Create database tables and apply safe database migrations."""

    database_path = os.path.join(
        app.instance_path,
        "users.sqlite3"
    )

    os.makedirs(app.instance_path, exist_ok=True)

    connection = sqlite3.connect(database_path)
    # IMPORTANT: Allows database rows to be accessed by column name.
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:

        # ==============================================
        # USERS TABLE
        # ==============================================

        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'customer',
                airline TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Add missing columns to existing users tables.
        user_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(users)"
            ).fetchall()
        }

        if "username" not in user_columns:
            connection.execute(
                "ALTER TABLE users ADD COLUMN username TEXT"
            )

        if "airline" not in user_columns:
            connection.execute(
                "ALTER TABLE users ADD COLUMN airline TEXT"
            )

        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username
            ON users(username)
        """)

        # ==============================================
        # FLIGHTS TABLE
        # ==============================================

        connection.execute("""
            CREATE TABLE IF NOT EXISTS flights (
                airline_name TEXT NOT NULL,
                flight_number TEXT NOT NULL,
                dep_datetime TEXT NOT NULL,
                dep_airport TEXT NOT NULL,
                arr_airport TEXT NOT NULL,
                arr_datetime TEXT NOT NULL,
                airplane_id TEXT,
                status TEXT NOT NULL,
                base_price REAL NOT NULL DEFAULT 0,

                PRIMARY KEY (
                    airline_name,
                    flight_number,
                    dep_datetime
                ),

                CHECK (
                    status IN (
                        'upcoming',
                        'in-progress',
                        'completed',
                        'cancelled'
                    )
                )
            )
        """)

        # ==============================================
        # TICKETS TABLE
        # ==============================================

        connection.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                airline_name TEXT NOT NULL,
                flight_number TEXT NOT NULL,
                dep_datetime TEXT NOT NULL,
                customer_email TEXT,
                sold_price REAL NOT NULL DEFAULT 0,
                purchased_at TEXT,

                FOREIGN KEY (customer_email)
                    REFERENCES users(email),

                FOREIGN KEY (
                    airline_name,
                    flight_number,
                    dep_datetime
                )
                    REFERENCES flights (
                        airline_name,
                        flight_number,
                        dep_datetime
                    )
            )
        """)

        # Add purchased_at to an existing tickets table.
        ticket_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(tickets)"
            ).fetchall()
        }

        if "purchased_at" not in ticket_columns:
            connection.execute(
                "ALTER TABLE tickets ADD COLUMN purchased_at TEXT"
            )

        # Automatically timestamp newly inserted tickets.
        connection.execute("""
            CREATE TRIGGER IF NOT EXISTS set_ticket_purchase_time
            AFTER INSERT ON tickets
            FOR EACH ROW
            WHEN NEW.purchased_at IS NULL
            BEGIN
                UPDATE tickets
                SET purchased_at = CURRENT_TIMESTAMP
                WHERE ticket_id = NEW.ticket_id;
            END
        """)

        # ==============================================
        # REVIEWS TABLE
        # ==============================================

        connection.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                customer_email TEXT NOT NULL,
                airline_name TEXT NOT NULL,
                flight_number TEXT NOT NULL,
                dep_datetime TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                PRIMARY KEY (
                    customer_email,
                    airline_name,
                    flight_number,
                    dep_datetime
                ),

                FOREIGN KEY (customer_email)
                    REFERENCES users(email),

                FOREIGN KEY (
                    airline_name,
                    flight_number,
                    dep_datetime
                )
                    REFERENCES flights (
                        airline_name,
                        flight_number,
                        dep_datetime
                    ),

                CHECK (rating BETWEEN 1 AND 5)
            )
        """)

        # ==============================================
        # DATABASE INDEXES
        # ==============================================

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_customer
            ON tickets(customer_email)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_purchase_date
            ON tickets(purchased_at)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_reviews_flight
            ON reviews(
                airline_name,
                flight_number,
                dep_datetime
            )
        """)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    # Close the request database connection automatically.
    app.teardown_appcontext(close_db)
