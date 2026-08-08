from app.models.task_activity import (
    ActivityType,
    TaskActivity,
    TaskActivityCreate,
)
from app.repositories.task_activity_repository import (
    TaskActivityRepository,
)


class TaskActivityService:
    def __init__(
        self,
        repository: TaskActivityRepository,
    ) -> None:
        self.repository = repository

    def create(
        self,
        activity: TaskActivityCreate,
    ) -> TaskActivity:
        activity_entity = self.repository.create(
            activity
        )

        return TaskActivity.model_validate(
            activity_entity
        )

    def get_by_task_id(
        self,
        task_id: int,
    ) -> list[TaskActivity]:
        return [
            TaskActivity.model_validate(activity)
            for activity
            in self.repository.get_by_task_id(task_id)
        ]

    def create_system_activity(
        self,
        *,
        task_id: int,
        title: str,
        message: str,
        created_by: str = "System",
    ) -> TaskActivity:
        return self.create(
            TaskActivityCreate(
                task_id=task_id,
                activity_type=ActivityType.SYSTEM,
                title=title,
                message=message,
                created_by=created_by,
            )
        )

    def create_date_activity(
        self,
        *,
        task_id: int,
        title: str,
        message: str,
        created_by: str = "System",
    ) -> TaskActivity:
        return self.create(
            TaskActivityCreate(
                task_id=task_id,
                activity_type=ActivityType.DATE,
                title=title,
                message=message,
                created_by=created_by,
            )
        )