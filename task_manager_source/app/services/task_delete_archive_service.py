from __future__ import annotations

import json
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from app.models.task_activity_entity import TaskActivityEntity
from app.models.task_entity import TaskEntity


class TaskDeleteArchiveService:
    def __init__(
        self,
        archive_path: Path | None = None,
    ) -> None:
        self.archive_path = (
            archive_path
            or Path("data/archive/delete.json")
        )

    def append_deleted_hierarchy(
        self,
        *,
        root_task: TaskEntity,
        tasks: list[TaskEntity],
        activities: list[TaskActivityEntity],
        deleted_by: str,
    ) -> None:
        self.archive_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        activities_by_task_id: dict[
            int,
            list[TaskActivityEntity],
        ] = {}

        for activity in activities:
            activities_by_task_id.setdefault(
                activity.task_id,
                [],
            ).append(activity)

        record = {
            "archive_version": 1,
            "deleted_at": datetime.now(),
            "deleted_by": deleted_by,
            "root_task_id": root_task.task_id,
            "root_task_number": root_task.task_number,
            "root_task_description": (
                root_task.short_description
            ),
            "task_count": len(tasks),
            "tasks": [
                {
                    "task": self._serialize_model(task),
                    "activities": [
                        self._serialize_model(activity)
                        for activity in (
                            activities_by_task_id.get(
                                task.task_id,
                                [],
                            )
                        )
                    ],
                }
                for task in tasks
            ],
        }

        with self.archive_path.open(
            mode="a",
            encoding="utf-8",
        ) as archive_file:
            archive_file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    default=self._json_default,
                )
            )
            archive_file.write("\n")

    @staticmethod
    def _serialize_model(
        model: object,
    ) -> dict[str, Any]:
        return {
            column.name: getattr(model, column.name)
            for column in model.__table__.columns
        }

    @staticmethod
    def _json_default(
        value: object,
    ) -> object:
        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, Enum):
            return value.value

        raise TypeError(
            f"Object of type {type(value).__name__} "
            "is not JSON serializable."
        )