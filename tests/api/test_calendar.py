from fastapi.testclient import TestClient

from app.main import app


def test_get_month_calendar(test_db):
    with TestClient(app) as client:
        response = client.get("/calendar/month?year=2024&month=12")
        assert response.status_code == 200
        data = response.json()
        assert "year" in data
        assert "month" in data
        assert data["year"] == 2024
        assert data["month"] == 12


def test_get_today_tasks(test_db):
    with TestClient(app) as client:
        response = client.get("/calendar/today")
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "tasks" in data
        assert "total_tasks" in data


def test_get_overdue_tasks(test_db):
    with TestClient(app) as client:
        response = client.get("/calendar/overdue")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total_overdue" in data
