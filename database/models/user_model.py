import sqlite3

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database.db import get_connection


def create_user(
    username,
    email,
    password,
    role="analyst"
):
    """Create a user account with a hashed password."""

    username = (username or "").strip()
    email = (email or "").strip().lower()

    if not username or not email or not password:
        raise ValueError(
            "Username, email, and password are required."
        )

    if len(password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    if role not in {"analyst", "admin"}:
        raise ValueError("Invalid user role.")

    password_hash = generate_password_hash(password)

    connection = get_connection()

    try:
        cursor = connection.execute("""
            INSERT INTO users (
                username,
                email,
                password_hash,
                role
            )
            VALUES (?, ?, ?, ?)
        """, (
            username,
            email,
            password_hash,
            role
        ))

        connection.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError as error:

        raise ValueError(
            "Username or email already exists."
        ) from error

    finally:
        connection.close()


def get_user_by_email(email):
    """Retrieve a user by email."""

    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (
            (email or "").strip().lower(),
        ))

        row = cursor.fetchone()

        return dict(row) if row else None

    finally:
        connection.close()


def verify_user_password(email, password):
    """Verify credentials without returning the password hash."""

    user = get_user_by_email(email)

    if not user:
        return None

    if not check_password_hash(
        user["password_hash"],
        password or ""
    ):
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"]
    }


def set_password_reset_nonce(user_id, nonce):
    connection = get_connection()
    try:
        connection.execute(
            "UPDATE users SET password_reset_nonce = ? WHERE id = ?",
            (nonce, user_id),
        )
        connection.commit()
    finally:
        connection.close()


def get_user_for_password_reset(user_id, nonce):
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT id FROM users WHERE id = ? AND password_reset_nonce = ?",
            (user_id, nonce),
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def update_user_password(user_id, password):
    if len(password or "") < 8:
        raise ValueError("Password must contain at least 8 characters.")

    password_hash = generate_password_hash(password)
    connection = get_connection()
    try:
        cursor = connection.execute(
            "UPDATE users SET password_hash = ?, password_reset_nonce = NULL WHERE id = ?",
            (password_hash, user_id),
        )
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()