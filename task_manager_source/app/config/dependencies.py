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
from app.repositories.task_dependency_repository import (
    TaskDependencyRepository,
)

from app.services.task_dependency_service import (
    TaskDependencyService,
)

from app.repositories.work_from_office_repository import (
    WorkFromOfficeRepository,
)
from app.services.work_from_office_service import (
    WorkFromOfficeService,
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

    task_repository = TaskRepository(
        database
    )

    activity_repository = (
        TaskActivityRepository(database)
    )

    activity_service = TaskActivityService(
        activity_repository
    )

    dependency_repository = (
        TaskDependencyRepository(database)
    )

    dependency_service = TaskDependencyService(
        dependency_repository=(
            dependency_repository
        ),
        task_repository=task_repository,
        activity_service=activity_service,
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
        dependency_service=(
            dependency_service
        ),
    )

def get_task_dependency_service(
    database: Session = Depends(
        get_database_session
    ),
) -> TaskDependencyService:

    dependency_repository = (
        TaskDependencyRepository(database)
    )

    task_repository = TaskRepository(
        database
    )

    activity_repository = (
        TaskActivityRepository(database)
    )

    activity_service = TaskActivityService(
        activity_repository
    )

    return TaskDependencyService(
        dependency_repository=(
            dependency_repository
        ),
        task_repository=task_repository,
        activity_service=activity_service,
    )

def get_work_from_office_service(
    db: Session = Depends(get_database_session),
) -> WorkFromOfficeService:

    repository = WorkFromOfficeRepository(
        db
    )

    return WorkFromOfficeService(
        repository
    )