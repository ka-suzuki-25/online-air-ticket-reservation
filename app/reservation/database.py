import os

import pymysql
from flask import g


def get_db():
    """Return the MySQL connection for the current request."""
    if "db" not in g:
        g.db = pymysql.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            user=os.environ["MYSQL_USER"],
            password=os.environ["MYSQL_PASSWORD"],
            database=os.environ["MYSQL_DATABASE"],
            cursorclass=pymysql.cursors.DictCursor,
        )
    return g.db


def close_db(e=None):
    """Close the connection when the request ends."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    """Register close_db so it runs after every request."""
    app.teardown_appcontext(close_db)
