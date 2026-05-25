from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskResponse, TaskStatusUpdate, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task.

    - **title** (required): Task title (max 200 characters)
    - **description** (optional): Detailed task description
    - **status** (optional): Task status, defaults to "pending"
    """
    db_task = Task(
        title=task.title, description=task.description, status=task.status or "pending"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    status: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    List all tasks with optional filtering.

    - **status** (optional): Filter by status (pending, completed)
    - **skip** (optional): Number of items to skip (default: 0)
    - **limit** (optional): Maximum number of items to return (default: 100)
    """
    query = db.query(Task)

    if status:
        query = query.filter(Task.status == status)

    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Get a specific task by ID.

    - **task_id** (required): The ID of the task to retrieve
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    return task


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int, status_update: TaskStatusUpdate, db: Session = Depends(get_db)
):
    """
    Update task status.

    - **task_id** (required): The ID of the task to update
    - **status** (required): New status value (e.g., "pending", "completed")
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    task.status = status_update.status
    db.commit()
    db.refresh(task)

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """
    Update task details (title, description, status).

    - **task_id** (required): The ID of the task to update
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task by ID.

    - **task_id** (required): The ID of the task to delete
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    db.delete(task)
    db.commit()

    return None
