from app.models.task_activity import (
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