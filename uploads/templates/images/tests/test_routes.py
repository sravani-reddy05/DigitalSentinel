
import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_dashboard_page(client):
    response = client.get("/dashboard")
    assert response.status_code == 200


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
