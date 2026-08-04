from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class TaskActivityEntity(Base):
    __tablename__ = "task_activity"

    activity_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.task_id"),
        nullable=False,
        index=True,
    )

    activity_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="comment",
        index=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Kiran",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        index=True,
    )

    __table_args__ = (
        Index(
            "ix_task_activity_task_created",
            "task_id",
            "created_at",
        ),
    )