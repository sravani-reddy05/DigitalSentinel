
import pytest
import uuid

from app import app
from database.db import get_connection
from database.models.user_model import create_user


@pytest.fixture
def client():
    app.config["TESTING"] = True
    email = f"route-test-{uuid.uuid4().hex}@example.test"
    user_id = create_user("Route Test", email, "test-password-123")
    try:
        with app.test_client() as test_client:
            with test_client.session_transaction() as test_session:
                test_session["user_id"] = user_id
                test_session["user_email"] = email
                test_session["username"] = "Route Test"
                test_session["role"] = "analyst"
            yield test_client
    finally:
        connection = get_connection()
        try:
            connection.execute("DELETE FROM detections WHERE user_id = ?", (user_id,))
            connection.execute("DELETE FROM scan_history WHERE user_id = ?", (user_id,))
            connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
            connection.commit()
        finally:
            connection.close()


def test_dashboard_page(client):
    response = client.get("/dashboard")
    assert response.status_code == 200


def test_empty_dashboard_shows_guidance_instead_of_blank_charts(client):
    response = client.get("/dashboard")
    assert b"id=\"riskOverviewEmpty\"" in response.data
    assert b"id=\"trendEmpty\"" in response.data
    assert b"Run your first scan" in response.data

    stats = client.get("/api/dashboard/stats").get_json()
    assert stats["total_detections"] == 0
    assert stats["risk_counts"] == {}
    assert stats["trend"] == []


def test_social_monitor_page(client):
    response = client.get("/social-monitor")
    assert response.status_code == 200


def test_app_monitor_page(client):
    response = client.get("/app-monitor")
    assert response.status_code == 200


def test_detections_page(client):
    response = client.get("/detections")
    assert response.status_code == 200


def test_reports_page(client):
    response = client.get("/reports")
    assert response.status_code == 200


def test_assistant_page(client):
    response = client.get("/assistant")
    assert response.status_code == 200


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_private_routes_require_sign_in():
    with app.test_client() as anonymous_client:
        assert anonymous_client.get("/dashboard").status_code == 302
        assert anonymous_client.get("/api/detections").status_code == 401


def test_detection_views_only_include_signed_in_users_history(client):
    from database.models.brand_model import get_all_brands
    from database.models.detection_model import create_detection

    brand_id = get_all_brands()[0]["id"]
    with client.session_transaction() as test_session:
        user_id = test_session["user_id"]

    other_user_id = create_user(
        f"Other-{uuid.uuid4().hex[:8]}",
        f"other-{uuid.uuid4().hex}@example.test",
        "test-password-123",
    )
    try:
        own_detection = create_detection(
            brand_id, "my-test-profile", "Instagram", risk_score=30,
            user_id=user_id,
        )
        other_detection = create_detection(
            brand_id, "other-test-profile", "Instagram", risk_score=80,
            risk_level="High", user_id=other_user_id,
        )

        response = client.get("/api/detections")
        assert response.status_code == 200
        ids = {row["id"] for row in response.get_json()["detections"]}
        assert own_detection in ids
        assert other_detection not in ids

        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        assert response.get_json()["total_detections"] == 1

        response = client.get("/api/reports/summary")
        assert response.status_code == 200
        assert response.get_json()["total_detections"] == 1

        response = client.get(f"/api/detections/{other_detection}")
        assert response.status_code == 404
    finally:
        connection = get_connection()
        try:
            connection.execute(
                "DELETE FROM detections WHERE user_id = ?", (other_user_id,)
            )
            connection.execute(
                "DELETE FROM scan_history WHERE user_id = ?", (other_user_id,)
            )
            connection.execute(
                "DELETE FROM users WHERE id = ?", (other_user_id,)
            )
            connection.commit()
        finally:
            connection.close()
