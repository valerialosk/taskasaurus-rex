from fastapi.testclient import TestClient
from app.main import app


def test_get_tasks():
    with TestClient(app) as client:
        response = client.get("/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert data["total"] == 0
        assert data["tasks"] == []


def test_get_task():
    with TestClient(app) as client:
        response = client.get("/tasks/1")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["id"] == 1


def test_create_task():
    with TestClient(app) as client:
        response = client.post("/tasks?title=Test Task&status=pending")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Task"
        assert data["status"] == "pending"


def test_delete_task():
    with TestClient(app) as client:
        response = client.delete("/tasks/1")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] == True
