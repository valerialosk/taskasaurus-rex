from fastapi.testclient import TestClient

from app.main import app


def test_get_tasks(test_db):
    with TestClient(app) as client:
        response = client.get("/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert isinstance(data["tasks"], list)


def test_get_task(test_db):
    with TestClient(app) as client:
        create_response = client.post(
            "/tasks",
            json={
                "title": "Test Task",
                "description": "Test",
                "status": "pending",
                "priority": "medium",
            },
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"


def test_create_task(test_db):
    with TestClient(app) as client:
        response = client.post(
            "/tasks",
            json={
                "title": "New Task",
                "description": "Task description",
                "status": "pending",
                "priority": "high",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == "New Task"
        assert data["status"] == "pending"
        assert data["priority"] == "high"


def test_update_task(test_db):
    with TestClient(app) as client:
        create_response = client.post(
            "/tasks",
            json={"title": "Original", "status": "pending", "priority": "low"},
        )
        task_id = create_response.json()["id"]

        response = client.put(
            f"/tasks/{task_id}", json={"title": "Updated", "status": "completed"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"
        assert data["status"] == "completed"


def test_delete_task(test_db):
    with TestClient(app) as client:
        create_response = client.post(
            "/tasks", json={"title": "To Delete", "status": "pending"}
        )
        task_id = create_response.json()["id"]

        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True

        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404
