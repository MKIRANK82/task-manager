from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskDependencyCreate(BaseModel):
    task_id: int = Field(gt=0)
    depends_on_task_id: int = Field(gt=0)
    created_by: str = Field(
        default="Kiran",
        min_length=1,
        max_length=100,
    )


class TaskDependency(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    dependency_id: int
    task_id: int
    depends_on_task_id: int
    created_by: str
    created_at: datetime