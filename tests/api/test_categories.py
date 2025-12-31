from fastapi.testclient import TestClient
from app.main import app


def test_get_categories():
    with TestClient(app) as client:
        response = client.get("/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "total" in data


def test_get_category():
    with TestClient(app) as client:
        response = client.get("/categories/1")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["id"] == 1


def test_create_category():
    with TestClient(app) as client:
        response = client.post("/categories?name=Work&color=%23FF0000")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "Work"
