from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class TaskAttachmentEntity(Base):
    __tablename__ = "task_attachments"

    attachment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.task_id"),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )