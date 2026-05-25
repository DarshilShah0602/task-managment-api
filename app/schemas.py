from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """Base schema for task fields"""

    title: str = Field(..., max_length=200, min_length=1)
    description: Optional[str] = None
    status: str = Field(default="pending")


class TaskCreate(TaskBase):
    """Schema for creating a new task"""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task"""

    title: Optional[str] = Field(None, max_length=200, min_length=1)
    description: Optional[str] = None
    status: Optional[str] = None


class TaskStatusUpdate(BaseModel):
    """Schema for updating task status"""

    status: str = Field(..., min_length=1)


class TaskResponse(TaskBase):
    """Schema for task response"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
