from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class TaskEntity(Base):
    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    task_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    parent_task_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        index=True,
    )

    short_description: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="not_started",
        index=True,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
        index=True,
    )

    task_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="task",
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    tags: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    planned_start_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    planned_end_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    actual_start_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    actual_end_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    estimated_effort_hours: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    actual_effort_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    remaining_effort_hours: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    progress_percentage: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    assigned_to: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    team: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    blocked_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    external_reference: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    created_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    __table_args__ = (
        Index(
            "ix_tasks_parent_active",
            "parent_task_id",
            "is_active",
        ),
    )