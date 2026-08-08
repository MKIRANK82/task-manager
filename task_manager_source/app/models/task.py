from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TaskStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CLOSED = "closed"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(StrEnum):
    TASK = "task"
    BUG = "bug"
    FEATURE = "feature"
    RESEARCH = "research"
    SUPPORT = "support"


class TaskBase(BaseModel):
    parent_task_id: int = Field(default=0, ge=0)

    short_description: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    status: TaskStatus = TaskStatus.NOT_STARTED
    priority: TaskPriority = TaskPriority.MEDIUM
    task_type: TaskType = TaskType.TASK

    category: str | None = Field(
        default=None,
        max_length=100,
    )

    tags: list[str] = Field(default_factory=list)

    planned_start_date: datetime | None = None
    planned_end_date: datetime | None = None

    actual_start_date: datetime | None = None
    actual_end_date: datetime | None = None

    due_date: datetime | None = None

    estimated_effort_hours: float | None = Field(
        default=None,
        ge=0,
    )

    actual_effort_hours: float = Field(
        default=0,
        ge=0,
    )

    remaining_effort_hours: float | None = Field(
        default=None,
        ge=0,
    )

    progress_percentage: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    assigned_to: str | None = Field(
        default=None,
        max_length=100,
    )

    team: str | None = Field(
        default=None,
        max_length=100,
    )

    blocked_reason: str | None = Field(
        default=None,
        max_length=1000,
    )

    external_reference: str | None = Field(
        default=None,
        max_length=200,
    )

    @model_validator(mode="after")
    def validate_dates(self) -> "TaskBase":
        if (
            self.planned_start_date is not None
            and self.planned_end_date is not None
            and self.planned_end_date < self.planned_start_date
        ):
            raise ValueError(
                "planned_end_date cannot be before planned_start_date"
            )

        if (
            self.actual_start_date is not None
            and self.actual_end_date is not None
            and self.actual_end_date < self.actual_start_date
        ):
            raise ValueError(
                "actual_end_date cannot be before actual_start_date"
            )

        return self


class TaskCreate(TaskBase):
    created_by: str = Field(
        default="Kiran",
        min_length=1,
        max_length=100,
    )


class TaskUpdate(BaseModel):
    parent_task_id: int | None = Field(
        default=None,
        ge=0,
    )

    short_description: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    task_type: TaskType | None = None

    category: str | None = Field(
        default=None,
        max_length=100,
    )

    tags: list[str] | None = None

    planned_start_date: datetime | None = None
    planned_end_date: datetime | None = None

    actual_start_date: datetime | None = None
    actual_end_date: datetime | None = None

    due_date: datetime | None = None

    estimated_effort_hours: float | None = Field(
        default=None,
        ge=0,
    )

    actual_effort_hours: float | None = Field(
        default=None,
        ge=0,
    )

    remaining_effort_hours: float | None = Field(
        default=None,
        ge=0,
    )

    progress_percentage: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    assigned_to: str | None = Field(
        default=None,
        max_length=100,
    )

    team: str | None = Field(
        default=None,
        max_length=100,
    )

    blocked_reason: str | None = Field(
        default=None,
        max_length=1000,
    )

    external_reference: str | None = Field(
        default=None,
        max_length=200,
    )


class Task(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    task_number: str

    created_by: str
    created_at: datetime
    updated_at: datetime

    is_active: bool


class TaskTreeNode(Task):
    children: list["TaskTreeNode"] = Field(
        default_factory=list,
    )


class TaskListResult(BaseModel):
    items: list[Task]
    total: int
    page: int
    page_size: int
    total_pages: int


class TaskDashboard(BaseModel):
    total_active: int
    planned_today: int
    due_today: int
    overdue: int
    completed_today: int
    in_progress: int
    blocked: int
    high_priority: int
    critical_priority: int