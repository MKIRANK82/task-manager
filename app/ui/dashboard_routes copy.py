from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config.dependencies import get_task_service
from app.services.task_service import TaskService


router = APIRouter(
    tags=["UI"],
)

templates = Jinja2Templates(
    directory="templates",
)


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def dashboard(
    request: Request,
    service: TaskService = Depends(get_task_service),
) -> HTMLResponse:
    dashboard_data = service.get_dashboard()
    task_tree = service.get_tree()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "dashboard": dashboard_data,
            "task_tree": task_tree,
        },
    )


@router.get(
    "/ui/tasks/tree",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def task_tree(
    request: Request,
    service: TaskService = Depends(get_task_service),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="task_tree.html",
        context={
            "task_tree": service.get_tree(),
        },
    )


@router.get(
    "/tasks/{task_id}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def task_details(
    request: Request,
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> HTMLResponse:
    task_entity = service.get_by_id(task_id)

    if task_entity is None:
        return templates.TemplateResponse(
            request=request,
            name="task_not_found.html",
            context={
                "task_id": task_id,
            },
            status_code=404,
        )

    parent_task = None

    if task_entity.parent_task_id != 0:
        parent_task = service.get_by_id(
            task_entity.parent_task_id
        )

    child_tasks = service.get_children(task_id)

    return templates.TemplateResponse(
        request=request,
        name="task_details.html",
        context={
            "task": task_entity,
            "parent_task": parent_task,
            "child_tasks": child_tasks,
        },
    )