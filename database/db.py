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
    connection.execute("PRAGMA foreign_keys = ON")

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
        detection_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(detections)")
        }
        if "user_id" not in detection_columns:
            connection.execute("ALTER TABLE detections ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")

        scan_history_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(scan_history)")
        }
        if "user_id" not in scan_history_columns:
            connection.execute("ALTER TABLE scan_history ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")

        user_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(users)")
        }
        if "password_reset_nonce" not in user_columns:
            connection.execute("ALTER TABLE users ADD COLUMN password_reset_nonce TEXT")

        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_detections_user ON detections(user_id)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_scan_history_user ON scan_history(user_id)"
        )
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