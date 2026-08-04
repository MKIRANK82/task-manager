from math import ceil

from app.models.task import (
    Task,
    TaskCreate,
    TaskDashboard,
    TaskListResult,
    TaskPriority,
    TaskStatus,
    TaskTreeNode,
    TaskType,
    TaskUpdate,
)
from app.models.task_entity import TaskEntity
from app.repositories.task_repository import TaskRepository

from app.services.task_activity_service import (
    TaskActivityService,
)


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
        activity_service: TaskActivityService,
        ) -> None:

        self.repository = repository
        self.activity_service = activity_service

    def create(
        self,
        task: TaskCreate,
    ) -> TaskEntity:
        created_task = self.repository.create(task)

        self._record_child_task_created(
            created_task
        )

        self._propagate_planned_end_date(
            created_task
        )

        return created_task

    def get_by_id(
        self,
        task_id: int,
    ) -> TaskEntity | None:
        return self.repository.get_by_id(task_id)

    def get_filtered(
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
        page: int,
        page_size: int,
    ) -> TaskListResult:
        task_entities, total = (
            self.repository.get_filtered(
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
                page=page,
                page_size=page_size,
            )
        )

        items = [
            Task.model_validate(task)
            for task in task_entities
        ]

        total_pages = (
            ceil(total / page_size)
            if total > 0
            else 0
        )

        return TaskListResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_tree(
    self,
    view: str = "all",
) -> list[TaskTreeNode]:
        task_entities = (
            self.repository.get_all_for_tree(view)
        )

        if view == "today":
            task_entities = self._include_ancestor_tasks(
                task_entities
            )

        nodes: dict[int, TaskTreeNode] = {
            entity.task_id: TaskTreeNode(
                **Task.model_validate(
                    entity
                ).model_dump(),
                children=[],
            )
            for entity in task_entities
        }

        roots: list[TaskTreeNode] = []

        for entity in task_entities:
            node = nodes[entity.task_id]

            if entity.parent_task_id == 0:
                roots.append(node)
                continue

            parent_node = nodes.get(
                entity.parent_task_id
            )

            if parent_node is None:
                roots.append(node)
                continue

            parent_node.children.append(node)

        self._sort_tree(roots)

        return roots

    def get_dashboard(self) -> TaskDashboard:
        counts = (
            self.repository.get_dashboard_counts()
        )

        return TaskDashboard(**counts)

    def update(
        self,
        task_id: int,
        task: TaskUpdate,
    ) -> TaskEntity | None:
        updated_task = self.repository.update(
            task_id,
            task,
        )

        if updated_task is None:
            return None

        self._propagate_planned_end_date(
            updated_task
        )

        return updated_task

    
    def delete(
        self,
        task_id: int,
    ) -> bool:
        return self.repository.delete(task_id)

    def _include_ancestor_tasks(
    self,
    task_entities: list[TaskEntity],
    ) -> list[TaskEntity]:
        entities_by_id = {
            task.task_id: task
            for task in task_entities
        }

        tasks_to_check = list(task_entities)

        while tasks_to_check:
            current_task = tasks_to_check.pop()

            if current_task.parent_task_id == 0:
                continue

            if (
                current_task.parent_task_id
                in entities_by_id
            ):
                continue

            parent = self.repository.get_by_id(
                current_task.parent_task_id
            )

            if parent is None:
                continue

            entities_by_id[parent.task_id] = parent
            tasks_to_check.append(parent)

        return list(entities_by_id.values())

    def _record_child_task_created(
        self,
        child_task: TaskEntity,
    ) -> None:
        if child_task.parent_task_id == 0:
            return

        parent = self.repository.get_by_id(
            child_task.parent_task_id
        )

        if parent is None:
            return

        self.activity_service.create_system_activity(
            task_id=parent.task_id,
            title="Subtask Added",
            message=(
                f"Task {child_task.task_number} "
                f"(Task ID {child_task.task_id}) "
                f"was added under this task.\n\n"
                f"Description: "
                f"{child_task.short_description}"
            ),
        )


    def _propagate_planned_end_date(
        self,
        child_task: TaskEntity,
    ) -> None:
        child_end_date = (
            child_task.planned_end_date
        )

        if child_end_date is None:
            return

        parent_task_id = (
            child_task.parent_task_id
        )

        while parent_task_id != 0:
            parent = self.repository.get_by_id(
                parent_task_id
            )

            if parent is None:
                break

            next_parent_task_id = (
                parent.parent_task_id
            )

            parent_end_date = (
                parent.planned_end_date
            )

            if (
                parent_end_date is not None
                and child_end_date > parent_end_date
            ):
                old_end_date = parent_end_date

                self.repository.update_planned_end_date(
                    task_id=parent.task_id,
                    planned_end_date=child_end_date,
                )

                self.activity_service.create_date_activity(
                    task_id=parent.task_id,
                    title="Planned End Date Extended",
                    message=(
                        "Planned end date changed "
                        f"from {old_end_date:%d %b %Y %I:%M %p} "
                        f"to {child_end_date:%d %b %Y %I:%M %p}.\n\n"
                        "Reason: "
                        f"Child task {child_task.task_number} "
                        f"(Task ID {child_task.task_id}) "
                        "has a later planned end date."
                    ),
                )

            parent_task_id = (
                next_parent_task_id
            )

    def _sort_tree(
        self,
        nodes: list[TaskTreeNode],
    ) -> None:
        nodes.sort(
            key=lambda node: self._task_number_key(
                node.task_number
            )
        )

        for node in nodes:
            self._sort_tree(node.children)

    def get_children(
            self,
            parent_task_id: int,
        ) -> list[Task]:
            return [
                Task.model_validate(task)
                for task in self.repository.get_children(
                    parent_task_id
                )
            ]

    @staticmethod
    def _task_number_key(
        task_number: str,
    ) -> tuple[int, ...]:
        return tuple(
            int(part)
            for part in task_number.split(".")
        )


    