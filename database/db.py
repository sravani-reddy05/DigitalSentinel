import sqlite3
from pathlib import Path

from config import Config


def get_connection():
    """Create and return a database connection."""

    db_path = Path(Config.DATABASE_PATH)

    db_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        str(db_path),
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create database tables using schema.sql."""

    schema_path = (
        Path(__file__).resolve().parent
        / "schema.sql"
    )

    with open(schema_path, "r", encoding="utf-8") as file:
        schema = file.read()

    connection = get_connection()

    try:
        connection.executescript(schema)
        connection.commit()
    finally:
        connection.close()


def fetch_all(query, parameters=()):
    """Retrieve multiple database records."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            query,
            parameters
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    finally:
        connection.close()


def fetch_one(query, parameters=()):
    """Retrieve a single database record."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            query,
            parameters
        )

        row = cursor.fetchone()

        return dict(row) if row else None

    finally:
        connection.close()


def execute_query(query, parameters=()):
    """Execute an INSERT, UPDATE, or DELETE query."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            query,
            parameters
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()