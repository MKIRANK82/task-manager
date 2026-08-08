from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.database import get_database_session
from app.repositories.task_activity_repository import (
    TaskActivityRepository,
)
from app.repositories.task_repository import (
    TaskRepository,
)
from app.services.task_activity_service import (
    TaskActivityService,
)
from app.services.task_service import (
    TaskService,
)

from app.services.task_delete_archive_service import (
    TaskDeleteArchiveService,
)


def get_task_activity_service(
    database: Session = Depends(
        get_database_session
    ),
) -> TaskActivityService:
    repository = TaskActivityRepository(
        database
    )

    return TaskActivityService(
        repository
    )


def get_task_service(
    database: Session = Depends(
        get_database_session
    ),
) -> TaskService:
    task_repository = TaskRepository(database)

    activity_repository = (
        TaskActivityRepository(database)
    )

    activity_service = TaskActivityService(
        activity_repository
    )

    delete_archive_service = (
        TaskDeleteArchiveService()
    )

    return TaskService(
        repository=task_repository,
        activity_service=activity_service,
        delete_archive_service=(
            delete_archive_service
        ),
    )