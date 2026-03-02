# app/models/attachment.py

from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.task import Task

class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)  # UUID filename
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)  # original file name
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship to Task
    task: Mapped[Task] = relationship("Task", back_populates="attachments")