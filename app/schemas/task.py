from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Import the Enums we already created in our database models!
from app.models.task import TaskStatus, TaskPriority

# 1. Base Schema (Shared attributes)
class TaskBase(BaseModel):
    title: str = Field(..., max_length=200, description="The title of the task")
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None

# 2. Schema for Creating a Task
class TaskCreate(TaskBase):
    pass # Inherits exactly what's in TaskBase

# 3. Schema for Updating a Task (All fields are optional)
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None

# 4. Schema for Returning a Task Response
class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    # Pydantic V2 config to tell it to read data from a SQLAlchemy ORM model
    model_config = ConfigDict(from_attributes=True)