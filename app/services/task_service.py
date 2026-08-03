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


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
    ) -> None:
        self.repository = repository

    def create(
        self,
        task: TaskCreate,
    ) -> TaskEntity:
        return self.repository.create(task)

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

    def get_tree(self) -> list[TaskTreeNode]:
        task_entities = (
            self.repository.get_all_for_tree()
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
        return self.repository.update(
            task_id,
            task,
        )

    def delete(
        self,
        task_id: int,
    ) -> bool:
        return self.repository.delete(task_id)

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

    @staticmethod
    def _task_number_key(
        task_number: str,
    ) -> tuple[int, ...]:
        return tuple(
            int(part)
            for part in task_number.split(".")
        )

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