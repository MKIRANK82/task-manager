from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.models.task_attachment_entity import (
    TaskAttachmentEntity,
)


class TaskAttachmentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        task_id: int,
        original_filename: str,
        stored_filename: str,
    ) -> TaskAttachmentEntity:

        entity = TaskAttachmentEntity(
            task_id=task_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
        )

        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)

        return entity

    def get_by_task_id(
        self,
        task_id: int,
    ) -> list[TaskAttachmentEntity]:

        stmt = (
            select(TaskAttachmentEntity)
            .where(
                TaskAttachmentEntity.task_id
                == task_id
            )
            .order_by(
                TaskAttachmentEntity.created_at
            )
        )

        return list(
            self.db.scalars(stmt).all()
        )

    def get_by_id(
        self,
        attachment_id: int,
    ) -> TaskAttachmentEntity | None:

        stmt = (
            select(TaskAttachmentEntity)
            .where(
                TaskAttachmentEntity.attachment_id
                == attachment_id
            )
        )

        return self.db.scalar(stmt)

    def delete_by_task_ids(
        self,
        task_ids: list[int],
        *,
        commit: bool = True,
    ) -> int:

        if not task_ids:
            return 0

        stmt = (
            delete(TaskAttachmentEntity)
            .where(
                TaskAttachmentEntity.task_id.in_(
                    task_ids
                )
            )
        )

        result = self.db.execute(stmt)

        if commit:
            self.db.commit()

        return result.rowcount or 0