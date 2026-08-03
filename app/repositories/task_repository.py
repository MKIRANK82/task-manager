from datetime import datetime, time, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.task import (
    TaskCreate,
    TaskPriority,
    TaskStatus,
    TaskType,
    TaskUpdate,
)
from app.models.task_entity import TaskEntity


class TaskRepository:
    def __init__(self, database: Session) -> None:
        self.database = database

    def create(self, task: TaskCreate) -> TaskEntity:
        parent = self._get_parent(task.parent_task_id)
        task_number = self._generate_task_number(parent)

        task_entity = TaskEntity(
            **task.model_dump(),
            task_number=task_number,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        try:
            self.database.add(task_entity)
            self.database.commit()
            self.database.refresh(task_entity)
        except Exception:
            self.database.rollback()
            raise

        return task_entity

    def get_by_id(
        self,
        task_id: int,
    ) -> TaskEntity | None:
        statement = select(TaskEntity).where(
            TaskEntity.task_id == task_id,
            TaskEntity.is_active.is_(True),
        )

        return self.database.scalar(statement)

    def get_children(
                self,
                parent_task_id: int,
            ) -> list[TaskEntity]:
            statement = (
                select(TaskEntity)
                .where(
                    TaskEntity.parent_task_id == parent_task_id,
                    TaskEntity.is_active.is_(True),
                )
                .order_by(TaskEntity.task_id)
            )
    
            return list(
                self.database.scalars(statement).all()
            )

    def get_filtered(
        self,
        *,
        task_status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        task_type: TaskType | None = None,
        parent_task_id: int | None = None,
        assigned_to: str | None = None,
        category: str | None = None,
        search: str | None = None,
        planned_today: bool = False,
        due_today: bool = False,
        overdue: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[TaskEntity], int]:
        filters = self._build_filters(
            task_status=task_status,
            priority=priority,
            task_type=task_type,
            parent_task_id=parent_task_id,
            assigned_to=assigned_to,
            category=category,
            search=search,
            planned_today=planned_today,
            due_today=due_today,
            overdue=overdue,
        )

        count_statement = (
            select(func.count(TaskEntity.task_id))
            .where(*filters)
        )

        total = self.database.scalar(count_statement) or 0

        offset = (page - 1) * page_size

        statement = (
            select(TaskEntity)
            .where(*filters)
            .order_by(
                TaskEntity.parent_task_id,
                TaskEntity.task_id,
            )
            .offset(offset)
            .limit(page_size)
        )

        tasks = list(
            self.database.scalars(statement).all()
        )

        return tasks, total

    def get_all_for_tree(
    self,
    view: str = "all",
) -> list[TaskEntity]:
        statement = select(TaskEntity).where(
            TaskEntity.is_active.is_(True)
        )

        if view == "today":
            now = datetime.now()

            today_start = datetime.combine(
                now.date(),
                time.min,
            )

            tomorrow_start = today_start + timedelta(days=1)

            statement = statement.where(
                TaskEntity.status.notin_(
                    [
                        TaskStatus.COMPLETED.value,
                        TaskStatus.CANCELLED.value,
                    ]
                ),
                or_(
                    (
                        TaskEntity.planned_start_date
                        >= today_start
                    )
                    & (
                        TaskEntity.planned_start_date
                        < tomorrow_start
                    ),
                    (
                        TaskEntity.due_date
                        >= today_start
                    )
                    & (
                        TaskEntity.due_date
                        < tomorrow_start
                    ),
                ),
            )

        statement = statement.order_by(
            TaskEntity.task_id
        )

        return list(
            self.database.scalars(statement).all()
        )

    def update(
        self,
        task_id: int,
        task: TaskUpdate,
    ) -> TaskEntity | None:
        task_entity = self.get_by_id(task_id)

        if task_entity is None:
            return None

        update_data = task.model_dump(exclude_unset=True)

        new_parent_task_id = update_data.pop(
            "parent_task_id",
            task_entity.parent_task_id,
        )

        if new_parent_task_id != task_entity.parent_task_id:
            self._validate_new_parent(
                task_entity=task_entity,
                new_parent_task_id=new_parent_task_id,
            )

            parent = self._get_parent(new_parent_task_id)

            task_entity.parent_task_id = new_parent_task_id
            task_entity.task_number = (
                self._generate_task_number(parent)
            )

        for field_name, value in update_data.items():
            setattr(task_entity, field_name, value)

        self._apply_status_rules(task_entity)
        task_entity.updated_at = datetime.now()

        try:
            self.database.commit()
            self.database.refresh(task_entity)
        except Exception:
            self.database.rollback()
            raise

        return task_entity

    def delete(
        self,
        task_id: int,
    ) -> bool:
        task_entity = self.get_by_id(task_id)

        if task_entity is None:
            return False

        active_children_statement = select(
            func.count(TaskEntity.task_id)
        ).where(
            TaskEntity.parent_task_id == task_id,
            TaskEntity.is_active.is_(True),
        )

        active_children = (
            self.database.scalar(active_children_statement)
            or 0
        )

        if active_children > 0:
            raise ValueError(
                "A task with active child tasks cannot be deleted"
            )

        task_entity.is_active = False
        task_entity.updated_at = datetime.now()

        try:
            self.database.commit()
        except Exception:
            self.database.rollback()
            raise

        return True

    def get_dashboard_counts(self) -> dict[str, int]:
        now = datetime.now()

        today_start = datetime.combine(
            now.date(),
            time.min,
        )

        tomorrow_start = today_start + timedelta(days=1)

        active_filter = TaskEntity.is_active.is_(True)

        return {
            "total_active": self._count(
                active_filter,
            ),
            "planned_today": self._count(
                active_filter,
                TaskEntity.planned_start_date >= today_start,
                TaskEntity.planned_start_date < tomorrow_start,
            ),
            "due_today": self._count(
                active_filter,
                TaskEntity.due_date >= today_start,
                TaskEntity.due_date < tomorrow_start,
            ),
            "overdue": self._count(
                active_filter,
                TaskEntity.due_date < now,
                TaskEntity.status.notin_(
                    [
                        TaskStatus.COMPLETED.value,
                        TaskStatus.CANCELLED.value,
                    ]
                ),
            ),
            "completed_today": self._count(
                active_filter,
                TaskEntity.status
                == TaskStatus.COMPLETED.value,
                TaskEntity.actual_end_date >= today_start,
                TaskEntity.actual_end_date < tomorrow_start,
            ),
            "in_progress": self._count(
                active_filter,
                TaskEntity.status
                == TaskStatus.IN_PROGRESS.value,
            ),
            "blocked": self._count(
                active_filter,
                TaskEntity.status
                == TaskStatus.BLOCKED.value,
            ),
            "high_priority": self._count(
                active_filter,
                TaskEntity.priority
                == TaskPriority.HIGH.value,
            ),
            "critical_priority": self._count(
                active_filter,
                TaskEntity.priority
                == TaskPriority.CRITICAL.value,
            ),
        }

    def _build_filters(
        self,
        *,
        task_status: TaskStatus | None,
        priority: TaskPriority | None,
        task_type: TaskType | None,
        parent_task_id: int | None,
        assigned_to: str | None,
        category: str | None,
        search: str | None,
        planned_today: bool,
        due_today: bool,
        overdue: bool,
    ) -> list:
        filters = [
            TaskEntity.is_active.is_(True),
        ]

        if task_status is not None:
            filters.append(
                TaskEntity.status == task_status.value
            )

        if priority is not None:
            filters.append(
                TaskEntity.priority == priority.value
            )

        if task_type is not None:
            filters.append(
                TaskEntity.task_type == task_type.value
            )

        if parent_task_id is not None:
            filters.append(
                TaskEntity.parent_task_id
                == parent_task_id
            )

        if assigned_to is not None:
            filters.append(
                func.lower(TaskEntity.assigned_to)
                == assigned_to.lower()
            )

        if category is not None:
            filters.append(
                func.lower(TaskEntity.category)
                == category.lower()
            )

        if search:
            search_value = f"%{search.strip()}%"

            filters.append(
                or_(
                    TaskEntity.short_description.ilike(
                        search_value
                    ),
                    TaskEntity.description.ilike(
                        search_value
                    ),
                    TaskEntity.external_reference.ilike(
                        search_value
                    ),
                    TaskEntity.task_number.ilike(
                        search_value
                    ),
                )
            )

        now = datetime.now()

        today_start = datetime.combine(
            now.date(),
            time.min,
        )

        tomorrow_start = today_start + timedelta(days=1)

        if planned_today:
            filters.extend(
                [
                    TaskEntity.planned_start_date
                    >= today_start,
                    TaskEntity.planned_start_date
                    < tomorrow_start,
                ]
            )

        if due_today:
            filters.extend(
                [
                    TaskEntity.due_date >= today_start,
                    TaskEntity.due_date < tomorrow_start,
                ]
            )

        if overdue:
            filters.extend(
                [
                    TaskEntity.due_date < now,
                    TaskEntity.status.notin_(
                        [
                            TaskStatus.COMPLETED.value,
                            TaskStatus.CANCELLED.value,
                        ]
                    ),
                ]
            )

        return filters

    def _count(self, *filters) -> int:
        statement = select(
            func.count(TaskEntity.task_id)
        ).where(*filters)

        return self.database.scalar(statement) or 0

    def _get_parent(
        self,
        parent_task_id: int,
    ) -> TaskEntity | None:
        if parent_task_id == 0:
            return None

        parent = self.get_by_id(parent_task_id)

        if parent is None:
            raise ValueError(
                f"Parent task {parent_task_id} does not exist"
            )

        return parent

    def _generate_task_number(
        self,
        parent: TaskEntity | None,
    ) -> str:
        parent_task_id = (
            0 if parent is None else parent.task_id
        )

        statement = select(
            TaskEntity.task_number
        ).where(
            TaskEntity.parent_task_id == parent_task_id
        )

        sibling_numbers = list(
            self.database.scalars(statement).all()
        )

        next_position = self._next_sibling_position(
            sibling_numbers=sibling_numbers,
            parent_number=(
                None
                if parent is None
                else parent.task_number
            ),
        )

        if parent is None:
            return str(next_position)

        return f"{parent.task_number}.{next_position}"

    @staticmethod
    def _next_sibling_position(
        *,
        sibling_numbers: list[str],
        parent_number: str | None,
    ) -> int:
        positions: list[int] = []

        for task_number in sibling_numbers:
            try:
                if parent_number is None:
                    if "." not in task_number:
                        positions.append(int(task_number))
                else:
                    prefix = f"{parent_number}."

                    if not task_number.startswith(prefix):
                        continue

                    remainder = task_number[len(prefix):]

                    if "." not in remainder:
                        positions.append(int(remainder))
            except ValueError:
                continue

        return max(positions, default=0) + 1

    def _validate_new_parent(
        self,
        *,
        task_entity: TaskEntity,
        new_parent_task_id: int,
    ) -> None:
        if new_parent_task_id == task_entity.task_id:
            raise ValueError(
                "A task cannot be its own parent"
            )

        current_parent_id = new_parent_task_id

        while current_parent_id != 0:
            parent = self.get_by_id(current_parent_id)

            if parent is None:
                raise ValueError(
                    f"Parent task {current_parent_id} "
                    "does not exist"
                )

            if parent.task_id == task_entity.task_id:
                raise ValueError(
                    "A task cannot be moved under "
                    "one of its descendants"
                )

            current_parent_id = parent.parent_task_id

    @staticmethod
    def _apply_status_rules(
        task_entity: TaskEntity,
    ) -> None:
        now = datetime.now()

        if (
            task_entity.status
            == TaskStatus.IN_PROGRESS.value
            and task_entity.actual_start_date is None
        ):
            task_entity.actual_start_date = now

        if (
            task_entity.status
            == TaskStatus.COMPLETED.value
        ):
            if task_entity.actual_start_date is None:
                task_entity.actual_start_date = now

            if task_entity.actual_end_date is None:
                task_entity.actual_end_date = now

            task_entity.progress_percentage = 100
            task_entity.remaining_effort_hours = 0

    