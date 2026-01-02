from fastapi.testclient import TestClient

from app.main import app


def test_get_categories(test_db):
    with TestClient(app) as client:
        response = client.get("/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "total" in data
        assert isinstance(data["categories"], list)


def test_get_category(test_db):
    with TestClient(app) as client:
        create_response = client.post(
            "/categories",
            json={"name": "Work", "color": "#FF0000", "description": "Work tasks"},
        )
        assert create_response.status_code == 201
        category_id = create_response.json()["id"]

        response = client.get(f"/categories/{category_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == "Work"


def test_create_category(test_db):
    with TestClient(app) as client:
        response = client.post(
            "/categories",
            json={
                "name": "Personal",
                "color": "#00FF00",
                "description": "Personal tasks",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "Personal"
        assert data["color"] == "#00FF00"


def test_update_category(test_db):
    with TestClient(app) as client:
        create_response = client.post(
            "/categories", json={"name": "Original", "color": "#111111"}
        )
        category_id = create_response.json()["id"]

        response = client.put(
            f"/categories/{category_id}",
            json={"name": "Updated", "color": "#222222"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["color"] == "#222222"


def test_delete_category(test_db):
    with TestClient(app) as client:
        create_response = client.post(
            "/categories", json={"name": "To Delete", "color": "#333333"}
        )
        category_id = create_response.json()["id"]

        response = client.delete(f"/categories/{category_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True
