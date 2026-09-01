import calendar
from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config.dependencies import (
    get_work_from_office_service,
)
from app.services.work_from_office_service import (
    WorkFromOfficeService,
)


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


@router.get("/work-from-office")
def work_from_office_calendar(
    request: Request,
    year: int | None = None,
    month: int | None = None,
    service: WorkFromOfficeService = Depends(
        get_work_from_office_service
    ),
):
    today = date.today()

    year = year or today.year
    month = month or today.month

    month_data = service.get_month(
        year=year,
        month=month,
    )

    cal = calendar.Calendar(
        firstweekday=calendar.MONDAY
    )

    weeks = cal.monthdatescalendar(
        year,
        month,
    )

    # Previous month
    if month == 1:
        previous_year = year - 1
        previous_month = 12
    else:
        previous_year = year
        previous_month = month - 1

    # Next month
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1

    return templates.TemplateResponse(
        request=request,
        name="work_from_office.html",
        context={
            "weeks": weeks,
            "year": year,
            "month": month,
            "month_name": calendar.month_name[
                month
            ],
            "today": today,
            "selected_dates": (
                month_data["selected_dates"]
            ),
            "selected_count": (
                month_data["selected_count"]
            ),
            "target_count": (
                month_data["target_count"]
            ),
            "previous_year": previous_year,
            "previous_month": previous_month,
            "next_year": next_year,
            "next_month": next_month,
        },
    )


@router.post("/work-from-office/toggle")
def toggle_work_from_office(
    work_date: date = Form(...),
    service: WorkFromOfficeService = Depends(
        get_work_from_office_service
    ),
):
    service.toggle_date(
        work_date
    )

    return RedirectResponse(
        url=(
            "/work-from-office"
            f"?year={work_date.year}"
            f"&month={work_date.month}"
        ),
        status_code=303,
    )