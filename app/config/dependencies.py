# app/config/dependencies.py

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.database import get_database_session
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService


def get_task_repository(
    database: Session = Depends(get_database_session),
) -> TaskRepository:
    return TaskRepository(database)


def get_task_service(
    repository: TaskRepository = Depends(get_task_repository),
) -> TaskService:
    return TaskService(repository)