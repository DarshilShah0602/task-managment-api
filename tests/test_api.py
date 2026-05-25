import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_task():
    response = client.post(
        "/tasks", json={"title": "Test Task", "description": "Test Description"}
    )
    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_list_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_task():
    # Create task first
    create_response = client.post("/tasks", json={"title": "Test"})
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_update_task_status():
    create_response = client.post("/tasks", json={"title": "Test"})
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}/status", json={"status": "completed"})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_delete_task():
    create_response = client.post("/tasks", json={"title": "Test"})
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
