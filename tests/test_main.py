from fastapi.testclient import TestClient

from app.main import app


def test_root(test_db):
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Taskasaurus Rex API"
        assert data["version"] == "0.1.0"


def test_health_check(test_db):
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "taskasaurus-rex"
