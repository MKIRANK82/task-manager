from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ActivityType(StrEnum):
    COMMENT = "comment"
    SYSTEM = "system"
    STATUS = "status"
    DATE = "date"
    PRIORITY = "priority"
    COMPLETION = "completion"
    AI = "ai"


class TaskActivityCreate(BaseModel):
    task_id: int = Field(gt=0)
    activity_type: ActivityType = ActivityType.COMMENT

    title: str | None = Field(
        default=None,
        max_length=200,
    )

    message: str = Field(
        min_length=1,
        max_length=5000,
    )

    created_by: str = Field(
        default="Kiran",
        min_length=1,
        max_length=100,
    )


class TaskActivity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    activity_id: int
    task_id: int

    activity_type: ActivityType
    title: str | None
    message: str

    created_by: str
    created_at: datetime