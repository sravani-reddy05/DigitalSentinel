import uuid
from urllib.parse import urlsplit

import app as application
from app import app
from database.db import get_connection
from database.models.user_model import create_user


def test_password_reset_link_changes_password_and_cannot_be_reused(monkeypatch):
    email = f"reset-{uuid.uuid4().hex}@example.test"
    user_id = create_user("Password Reset Test", email, "old-password-123")
    sent_messages = []
    monkeypatch.setattr(
        application,
        "_send_password_reset_email",
        lambda recipient, reset_url: sent_messages.append((recipient, reset_url)),
    )

    try:
        with app.test_client() as client:
            response = client.post("/forgot-password", data={"email": email})
            assert response.status_code == 200
            assert len(sent_messages) == 1
            assert sent_messages[0][0] == email

            reset_path = urlsplit(sent_messages[0][1]).path
            response = client.post(
                reset_path,
                data={
                    "password": "new-password-456",
                    "confirm_password": "new-password-456",
                },
            )
            assert response.status_code == 200
            assert b"Password updated" in response.data

            response = client.post("/login", data={
                "email": email,
                "password": "old-password-123",
            })
            assert b"Invalid email or password" in response.data

            response = client.post("/login", data={
                "email": email,
                "password": "new-password-456",
            })
            assert response.status_code == 302

            response = client.get(reset_path)
            assert response.status_code == 400
            assert b"already been used" in response.data
    finally:
        connection = get_connection()
        try:
            connection.execute("DELETE FROM detections WHERE user_id = ?", (user_id,))
            connection.execute("DELETE FROM scan_history WHERE user_id = ?", (user_id,))
            connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
            connection.commit()
        finally:
            connection.close()
