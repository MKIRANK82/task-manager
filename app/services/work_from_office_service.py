from datetime import date

from app.config.settings import settings
from app.repositories.work_from_office_repository import (
    WorkFromOfficeRepository,
)


class WorkFromOfficeService:

    def __init__(
        self,
        repository: WorkFromOfficeRepository,
    ):
        self.repository = repository

    def get_month(
        self,
        year: int,
        month: int,
    ) -> dict:

        records = self.repository.get_by_month(
            year=year,
            month=month,
        )

        selected_dates = {
            record.work_date
            for record in records
        }

        return {
            "year": year,
            "month": month,
            "selected_dates": selected_dates,
            "selected_count": len(selected_dates),
            "target_count": settings.wfo_days_per_month,
        }

    def toggle_date(
        self,
        work_date: date,
    ) -> bool:

        return self.repository.toggle(
            work_date
        )