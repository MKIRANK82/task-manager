from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class WorkFromOfficeEntity(Base):
    __tablename__ = "work_from_office"

    wfo_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    work_date: Mapped[date] = mapped_column(
        Date,
        unique=True,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )