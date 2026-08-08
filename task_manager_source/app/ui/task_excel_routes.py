from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config.database import get_database_session
from app.services.task_excel_service import TaskExcelService


router = APIRouter(
    tags=["Task Excel"],
)


@router.get(
    "/tasks/export/excel",
    include_in_schema=False,
)
def export_tasks_to_excel(
    database: Session = Depends(
        get_database_session
    ),
) -> StreamingResponse:
    service = TaskExcelService(database)

    excel_file = service.export_tasks()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"task_manager_backup_{timestamp}.xlsx"
    )

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )