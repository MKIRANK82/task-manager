from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.task_activity import TaskActivityCreate
from app.models.task_activity_entity import TaskActivityEntity


class TaskActivityRepository:
    def __init__(self, database: Session) -> None:
        self.database = database

    def create(
        self,
        activity: TaskActivityCreate,
    ) -> TaskActivityEntity:
        activity_entity = TaskActivityEntity(
            **activity.model_dump()
        )

        try:
            self.database.add(activity_entity)
            self.database.commit()
            self.database.refresh(activity_entity)
        except Exception:
            self.database.rollback()
            raise

        return activity_entity

    def create_without_commit(
        self,
        activity: TaskActivityCreate,
    ) -> TaskActivityEntity:
        activity_entity = TaskActivityEntity(
            **activity.model_dump()
        )

        self.database.add(activity_entity)
        self.database.flush()

        return activity_entity

    def get_by_task_id(
        self,
        task_id: int,
    ) -> list[TaskActivityEntity]:
        statement = (
            select(TaskActivityEntity)
            .where(
                TaskActivityEntity.task_id == task_id
            )
            .order_by(
                TaskActivityEntity.created_at.desc(),
                TaskActivityEntity.activity_id.desc(),
            )
        )

        return list(
            self.database.scalars(statement).all()
        )

    def get_by_task_ids(
        self,
        task_ids: list[int],
    ) -> list[TaskActivityEntity]:
        if not task_ids:
            return []

        statement = (
            select(TaskActivityEntity)
            .where(
                TaskActivityEntity.task_id.in_(task_ids)
            )
            .order_by(
                TaskActivityEntity.task_id,
                TaskActivityEntity.created_at,
                TaskActivityEntity.activity_id,
            )
        )

        return list(
            self.database.scalars(statement).all()
        )

    def delete_by_task_ids(
        self,
        task_ids: list[int],
        *,
        commit: bool = True,
    ) -> int:
        if not task_ids:
            return 0

        statement = (
            delete(TaskActivityEntity)
            .where(
                TaskActivityEntity.task_id.in_(task_ids)
            )
        )

        result = self.database.execute(statement)

        if commit:
            self.database.commit()

        return result.rowcount or 0