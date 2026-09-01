from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class TaskDependencyEntity(Base):
    __tablename__ = "task_dependencies"

    dependency_id: Mapped[int] = mapped_column(
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

    depends_on_task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.task_id"),
        nullable=False,
        index=True,
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
    )

    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "depends_on_task_id",
            name="uq_task_dependency",
        ),
    )