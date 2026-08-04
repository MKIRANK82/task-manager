# app/config/dependencies.py

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.database import get_database_session
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService
from app.repositories.task_activity_repository import (
    TaskActivityRepository,
)

from app.services.task_service import TaskService

from app.services.task_activity_service import (
    TaskActivityService,
)


def get_task_repository(
    database: Session = Depends(get_database_session),
) -> TaskRepository:
    return TaskRepository(database)


def get_task_service(
    repository: TaskRepository = Depends(get_task_repository),
) -> TaskService:
    return TaskService(repository)

def get_task_activity_service(
    database: Session = Depends(get_database_session),
) -> TaskActivityService:
    repository = TaskActivityRepository(database)

    return TaskActivityService(repository)