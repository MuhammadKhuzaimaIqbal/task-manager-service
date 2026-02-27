import enum
from datetime import datetime
from sqlalchemy import String, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str | None] = mapped_column(default=None)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.todo)
    priority: Mapped[TaskPriority] = mapped_column(default=TaskPriority.medium)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    due_date: Mapped[datetime | None] = mapped_column(default=None)