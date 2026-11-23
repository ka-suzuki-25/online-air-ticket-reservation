
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
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(error=None):
    """Close the current request's database connection."""

    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db(app):
    """Initialize account, flight, ticket, and review tables."""

    database_path = os.path.join(
        app.instance_path,
        "users.sqlite3"
    )

    os.makedirs(app.instance_path, exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")

    # Existing customer accounts table.
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

    # Flight information.
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

            CHECK (status IN (
                'upcoming',
                'in-progress',
                'completed',
                'cancelled'
            ))
        )
    """)

    # Tickets connect customers to purchased flights.
    connection.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            airline_name TEXT NOT NULL,
            flight_number TEXT NOT NULL,
            dep_datetime TEXT NOT NULL,
            customer_email TEXT,
            sold_price REAL NOT NULL DEFAULT 0,

            FOREIGN KEY (customer_email)
                REFERENCES users(email),

            FOREIGN KEY (
                airline_name,
                flight_number,
                dep_datetime
            )
                REFERENCES flights(
                    airline_name,
                    flight_number,
                    dep_datetime
                )
        )
    """)

    # One review per customer for each flight instance.
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
                REFERENCES flights(
                    airline_name,
                    flight_number,
                    dep_datetime
                ),

            CHECK (rating BETWEEN 1 AND 5)
        )
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_tickets_customer
        ON tickets(customer_email)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_reviews_flight
        ON reviews(airline_name, flight_number, dep_datetime)
    """)

    connection.commit()
    connection.close()

    app.teardown_appcontext(close_db)
