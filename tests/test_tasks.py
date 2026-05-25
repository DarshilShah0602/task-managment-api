import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["ENVIRONMENT"] = "test"

from app.main import app
from app.database import get_db
from app.models import Base

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database before each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_create_task():
    """Test creating a new task"""
    response = client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "This is a test task",
            "status": "pending",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["status"] == "pending"
    assert data["id"] is not None


def test_list_tasks():
    """Test listing all tasks"""
    # Create a few tasks
    for i in range(3):
        client.post(
            "/tasks",
            json={
                "title": f"Task {i}",
                "description": f"Description {i}",
                "status": "pending",
            },
        )

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_get_task_by_id():
    """Test getting a specific task"""
    # Create a task
    create_response = client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "pending",
        },
    )
    task_id = create_response.json()["id"]

    # Get the task
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"


def test_get_nonexistent_task():
    """Test getting a task that doesn't exist"""
    response = client.get("/tasks/999")
    assert response.status_code == 404


def test_update_task_status():
    """Test updating task status"""
    # Create a task
    create_response = client.post(
        "/tasks", json={"title": "Test Task", "status": "pending"}
    )
    task_id = create_response.json()["id"]

    # Update status
    response = client.patch(f"/tasks/{task_id}/status", json={"status": "completed"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_update_task():
    """Test updating task details"""
    # Create a task
    create_response = client.post(
        "/tasks",
        json={
            "title": "Original Title",
            "description": "Original Description",
            "status": "pending",
        },
    )
    task_id = create_response.json()["id"]

    # Update task
    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "title": "Updated Title",
            "description": "Updated Description",
            "status": "completed",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["status"] == "completed"


def test_delete_task():
    """Test deleting a task"""
    # Create a task
    create_response = client.post(
        "/tasks", json={"title": "Test Task", "status": "pending"}
    )
    task_id = create_response.json()["id"]

    # Delete the task
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify it's deleted
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404


def test_list_tasks_with_filter():
    """Test listing tasks with status filter"""
    # Create tasks with different statuses
    client.post("/tasks", json={"title": "Pending Task", "status": "pending"})
    client.post("/tasks", json={"title": "Completed Task", "status": "completed"})

    # Filter by pending
    response = client.get("/tasks?status=pending")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "pending"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
