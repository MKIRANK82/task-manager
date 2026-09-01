from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.models.task_dependency import (
    TaskDependencyCreate,
)
from app.models.task_dependency_entity import (
    TaskDependencyEntity,
)


class TaskDependencyRepository:

    def __init__(
        self,
        database: Session,
    ) -> None:
        self.database = database

    def create(
        self,
        dependency: TaskDependencyCreate,
    ) -> TaskDependencyEntity:

        entity = TaskDependencyEntity(
            **dependency.model_dump()
        )

        try:
            self.database.add(entity)
            self.database.commit()
            self.database.refresh(entity)
        except Exception:
            self.database.rollback()
            raise

        return entity

    def get_by_task_id(
        self,
        task_id: int,
    ) -> list[TaskDependencyEntity]:

        statement = (
            select(TaskDependencyEntity)
            .where(
                TaskDependencyEntity.task_id
                == task_id
            )
            .order_by(
                TaskDependencyEntity.dependency_id
            )
        )

        return list(
            self.database.scalars(
                statement
            ).all()
        )

    def get_required_by_task_id(
        self,
        task_id: int,
    ) -> list[TaskDependencyEntity]:

        statement = (
            select(TaskDependencyEntity)
            .where(
                TaskDependencyEntity.depends_on_task_id
                == task_id
            )
            .order_by(
                TaskDependencyEntity.dependency_id
            )
        )

        return list(
            self.database.scalars(
                statement
            ).all()
        )

    def exists(
        self,
        task_id: int,
        depends_on_task_id: int,
    ) -> bool:

        statement = (
            select(TaskDependencyEntity)
            .where(
                TaskDependencyEntity.task_id
                == task_id,
                TaskDependencyEntity.depends_on_task_id
                == depends_on_task_id,
            )
        )

        return (
            self.database.scalar(statement)
            is not None
        )

    def delete(
        self,
        dependency_id: int,
    ) -> bool:

        entity = self.database.get(
            TaskDependencyEntity,
            dependency_id,
        )

        if entity is None:
            return False

        try:
            self.database.delete(entity)
            self.database.commit()
        except Exception:
            self.database.rollback()
            raise

        return True

    def delete_for_task_ids(
        self,
        task_ids: list[int],
        *,
        commit: bool = True,
    ) -> int:

        if not task_ids:
            return 0

        statement = (
            delete(TaskDependencyEntity)
            .where(
                or_(
                    TaskDependencyEntity.task_id.in_(
                        task_ids
                    ),
                    TaskDependencyEntity
                    .depends_on_task_id
                    .in_(task_ids),
                )
            )
        )

        result = self.database.execute(
            statement
        )

        if commit:
            self.database.commit()

        return result.rowcount or 0