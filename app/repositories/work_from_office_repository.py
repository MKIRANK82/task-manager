from datetime import date

from sqlalchemy import extract, select
from sqlalchemy.orm import Session

from app.models.work_from_office_entity import (
    WorkFromOfficeEntity,
)


class WorkFromOfficeRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_date(
        self,
        work_date: date,
    ) -> WorkFromOfficeEntity | None:
        stmt = (
            select(WorkFromOfficeEntity)
            .where(
                WorkFromOfficeEntity.work_date
                == work_date
            )
        )

        return self.db.scalar(stmt)

    def get_by_month(
        self,
        year: int,
        month: int,
    ) -> list[WorkFromOfficeEntity]:

        stmt = (
            select(WorkFromOfficeEntity)
            .where(
                extract(
                    "year",
                    WorkFromOfficeEntity.work_date,
                )
                == year,
                extract(
                    "month",
                    WorkFromOfficeEntity.work_date,
                )
                == month,
            )
            .order_by(
                WorkFromOfficeEntity.work_date
            )
        )

        return list(
            self.db.scalars(stmt).all()
        )

    def add(
        self,
        work_date: date,
    ) -> WorkFromOfficeEntity:

        entity = WorkFromOfficeEntity(
            work_date=work_date
        )

        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)

        return entity

    def delete(
        self,
        entity: WorkFromOfficeEntity,
    ) -> None:

        self.db.delete(entity)
        self.db.commit()

    def toggle(
        self,
        work_date: date,
    ) -> bool:

        existing = self.get_by_date(
            work_date
        )

        if existing:
            self.delete(existing)
            return False

        self.add(work_date)
        return True