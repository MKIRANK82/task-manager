from datetime import date

from app.models.task import TaskStatus
from app.models.task_activity import (
    ActivityType,
    TaskActivityCreate,
)
from app.models.task_dependency import (
    TaskDependency,
    TaskDependencyCreate,
)
from app.repositories.task_dependency_repository import (
    TaskDependencyRepository,
)
from app.repositories.task_repository import (
    TaskRepository,
)
from app.services.task_activity_service import (
    TaskActivityService,
)


class TaskDependencyService:

    SATISFIED_STATUSES = {
        TaskStatus.COMPLETED.value,
        TaskStatus.CLOSED.value,
    }

    def __init__(
        self,
        dependency_repository: (
            TaskDependencyRepository
        ),
        task_repository: TaskRepository,
        activity_service: TaskActivityService,
    ) -> None:

        self.dependency_repository = (
            dependency_repository
        )

        self.task_repository = task_repository

        self.activity_service = (
            activity_service
        )

    def add_dependency(
        self,
        dependency: TaskDependencyCreate,
    ) -> TaskDependency:

        if (
            dependency.task_id
            == dependency.depends_on_task_id
        ):
            raise ValueError(
                "A task cannot depend on itself."
            )

        task = self.task_repository.get_by_id(
            dependency.task_id
        )

        if task is None:
            raise ValueError(
                f"Task ID {dependency.task_id} "
                "does not exist."
            )

        depends_on_task = (
            self.task_repository.get_by_id(
                dependency.depends_on_task_id
            )
        )

        if depends_on_task is None:
            raise ValueError(
                "Dependency task "
                f"{dependency.depends_on_task_id} "
                "does not exist."
            )

        if self.dependency_repository.exists(
            dependency.task_id,
            dependency.depends_on_task_id,
        ):
            raise ValueError(
                "This dependency already exists."
            )

        if self._would_create_cycle(
            task_id=dependency.task_id,
            depends_on_task_id=(
                dependency.depends_on_task_id
            ),
        ):
            raise ValueError(
                "Dependency cannot be added because "
                "it would create a circular dependency."
            )

        entity = (
            self.dependency_repository.create(
                dependency
            )
        )

        self.activity_service.create(
            TaskActivityCreate(
                task_id=dependency.task_id,
                activity_type=(
                    ActivityType.SYSTEM
                ),
                title="Dependency Added",
                message=(
                    f"Task now depends on "
                    f"{depends_on_task.task_number} "
                    f"(Task ID "
                    f"{depends_on_task.task_id}) - "
                    f"{depends_on_task.short_description}."
                ),
                created_by=dependency.created_by,
            )
        )

        return TaskDependency.model_validate(
            entity
        )

    def remove_dependency(
        self,
        dependency_id: int,
        removed_by: str = "Kiran",
    ) -> bool:

        entity = (
            self.dependency_repository.database.get(
                __import__(
                    "app.models.task_dependency_entity",
                    fromlist=[
                        "TaskDependencyEntity"
                    ],
                ).TaskDependencyEntity,
                dependency_id,
            )
        )

        if entity is None:
            return False

        task_id = entity.task_id
        depends_on_task_id = (
            entity.depends_on_task_id
        )

        dependent_task = (
            self.task_repository.get_by_id(
                depends_on_task_id
            )
        )

        deleted = (
            self.dependency_repository.delete(
                dependency_id
            )
        )

        if deleted:
            description = ""

            if dependent_task is not None:
                description = (
                    f"{dependent_task.task_number} "
                    f"(Task ID "
                    f"{dependent_task.task_id}) - "
                    f"{dependent_task.short_description}"
                )

            self.activity_service.create(
                TaskActivityCreate(
                    task_id=task_id,
                    activity_type=(
                        ActivityType.SYSTEM
                    ),
                    title="Dependency Removed",
                    message=(
                        "Dependency removed: "
                        f"{description}"
                    ),
                    created_by=removed_by,
                )
            )

        return deleted

    def get_dependencies(
        self,
        task_id: int,
    ) -> list[dict[str, object]]:

        relationships = (
            self.dependency_repository
            .get_by_task_id(task_id)
        )

        result = []

        for relationship in relationships:

            dependency_task = (
                self.task_repository.get_by_id(
                    relationship
                    .depends_on_task_id
                )
            )

            if dependency_task is None:
                continue

            status = self._status_value(
                dependency_task.status
            )

            result.append(
                {
                    "dependency_id": (
                        relationship.dependency_id
                    ),
                    "task": dependency_task,
                    "satisfied": (
                        status
                        in self.SATISFIED_STATUSES
                    ),
                    "cancelled": (
                        status
                        == TaskStatus.CANCELLED.value
                    ),
                }
            )

        return result

    def get_required_by(
        self,
        task_id: int,
    ) -> list[dict[str, object]]:

        relationships = (
            self.dependency_repository
            .get_required_by_task_id(task_id)
        )

        result = []

        for relationship in relationships:

            task = self.task_repository.get_by_id(
                relationship.task_id
            )

            if task is None:
                continue

            result.append(
                {
                    "dependency_id": (
                        relationship.dependency_id
                    ),
                    "task": task,
                }
            )

        return result

    def get_dependency_state(
        self,
        task_id: int,
    ) -> str:

        dependencies = self.get_dependencies(
            task_id
        )

        if not dependencies:
            return "none"

        cancelled = any(
            item["cancelled"]
            for item in dependencies
        )

        if cancelled:
            return "cancelled"

        incomplete = any(
            not item["satisfied"]
            for item in dependencies
        )

        if not incomplete:
            return "ready"

        task = self.task_repository.get_by_id(
            task_id
        )

        if (
            task is not None
            and task.planned_start_date
            is not None
            and task.planned_start_date.date()
            <= date.today()
        ):
            return "delayed"

        return "waiting"

    def _would_create_cycle(
        self,
        *,
        task_id: int,
        depends_on_task_id: int,
    ) -> bool:

        visited: set[int] = set()

        pending = [
            depends_on_task_id
        ]

        while pending:

            current = pending.pop()

            if current == task_id:
                return True

            if current in visited:
                continue

            visited.add(current)

            dependencies = (
                self.dependency_repository
                .get_by_task_id(current)
            )

            pending.extend(
                dependency.depends_on_task_id
                for dependency in dependencies
            )

        return False

    @staticmethod
    def _status_value(
        status: object,
    ) -> str:

        return str(
            getattr(
                status,
                "value",
                status,
            )
        ).strip().lower()