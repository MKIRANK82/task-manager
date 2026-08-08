from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
    status,
)

from app.config.dependencies import get_task_service
from app.errors.api_exception import ApiException
from app.models.api_response import ApiResponse
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
from app.services.task_service import TaskService


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.post(
    "",
    response_model=ApiResponse[Task],
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    request: Request,
    task: TaskCreate,
    service: TaskService = Depends(
        get_task_service
    ),
) -> ApiResponse[Task]:
    try:
        task_entity = service.create(task)
    except ValueError as error:
        raise ApiException(
            code="INVALID_PARENT_TASK",
            message=str(error),
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from error

    return ApiResponse[Task](
        success=True,
        code="TASK_CREATED",
        message="Task created successfully.",
        data=Task.model_validate(task_entity),
        correlation_id=request.state.correlation_id,
    )


@router.get(
    "",
    response_model=ApiResponse[TaskListResult],
)
def get_tasks(
    request: Request,
    task_status: Annotated[
        TaskStatus | None,
        Query(alias="status"),
    ] = None,
    priority: TaskPriority | None = None,
    task_type: TaskType | None = None,
    parent_task_id: Annotated[
        int | None,
        Query(ge=0),
    ] = None,
    assigned_to: str | None = None,
    category: str | None = None,
    search: Annotated[
        str | None,
        Query(min_length=1, max_length=200),
    ] = None,
    planned_today: bool = False,
    due_today: bool = False,
    overdue: bool = False,
    page: Annotated[
        int,
        Query(ge=1),
    ] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=200),
    ] = 50,
    service: TaskService = Depends(
        get_task_service
    ),
) -> ApiResponse[TaskListResult]:
    result = service.get_filtered(
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

    return ApiResponse[TaskListResult](
        success=True,
        code="TASKS_RETRIEVED",
        message="Tasks retrieved successfully.",
        data=result,
        correlation_id=request.state.correlation_id,
    )


@router.get(
    "/tree",
    response_model=ApiResponse[list[TaskTreeNode]],
)
def get_task_tree(
    request: Request,
    service: TaskService = Depends(
        get_task_service
    ),
) -> ApiResponse[list[TaskTreeNode]]:
    tree = service.get_tree()

    return ApiResponse[list[TaskTreeNode]](
        success=True,
        code="TASK_TREE_RETRIEVED",
        message="Task tree retrieved successfully.",
        data=tree,
        correlation_id=request.state.correlation_id,
    )


@router.get(
    "/dashboard",
    response_model=ApiResponse[TaskDashboard],
)
def get_task_dashboard(
    request: Request,
    service: TaskService = Depends(
        get_task_service
    ),
) -> ApiResponse[TaskDashboard]:
    dashboard = service.get_dashboard()

    return ApiResponse[TaskDashboard](
        success=True,
        code="TASK_DASHBOARD_RETRIEVED",
        message="Task dashboard retrieved successfully.",
        data=dashboard,
        correlation_id=request.state.correlation_id,
    )


@router.get(
    "/{task_id}",
    response_model=ApiResponse[Task],
)
def get_task(
    request: Request,
    task_id: int,
    service: TaskService = Depends(
        get_task_service
    ),
) -> ApiResponse[Task]:
    task_entity = service.get_by_id(task_id)

    if task_entity is None:
        raise ApiException(
            code="TASK_NOT_FOUND",
            message=f"Task {task_id} was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return ApiResponse[Task](
        success=True,
        code="TASK_RETRIEVED",
        message="Task retrieved successfully.",
        data=Task.model_validate(task_entity),
        correlation_id=request.state.correlation_id,
    )


@router.put(
    "/{task_id}",
    response_model=ApiResponse[Task],
)
def update_task(
    request: Request,
    task_id: int,
    task: TaskUpdate,
    service: TaskService = Depends(
        get_task_service
    ),
) -> ApiResponse[Task]:
    try:
        task_entity = service.update(
            task_id,
            task,
        )
    except ValueError as error:
        raise ApiException(
            code="INVALID_TASK_UPDATE",
            message=str(error),
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from error

    if task_entity is None:
        raise ApiException(
            code="TASK_NOT_FOUND",
            message=f"Task {task_id} was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return ApiResponse[Task](
        success=True,
        code="TASK_UPDATED",
        message="Task updated successfully.",
        data=Task.model_validate(task_entity),
        correlation_id=request.state.correlation_id,
    )


@router.delete(
    "/{task_id}",
    response_model=ApiResponse[None],
)
def delete_task(
    request: Request,
    task_id: int,
    service: TaskService = Depends(
        get_task_service
    ),
) -> ApiResponse[None]:
    try:
        deleted = service.delete(task_id)
    except ValueError as error:
        raise ApiException(
            code="TASK_HAS_ACTIVE_CHILDREN",
            message=str(error),
            status_code=status.HTTP_409_CONFLICT,
        ) from error

    if not deleted:
        raise ApiException(
            code="TASK_NOT_FOUND",
            message=f"Task {task_id} was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return ApiResponse[None](
        success=True,
        code="TASK_DELETED",
        message="Task deleted successfully.",
        data=None,
        correlation_id=request.state.correlation_id,
    )