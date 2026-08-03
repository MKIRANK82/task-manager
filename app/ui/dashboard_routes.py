from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config.dependencies import get_task_service
from app.models.task import (
    TaskPriority,
    TaskStatus,
    TaskType,
    TaskUpdate,
)
from app.services.task_service import TaskService


router = APIRouter(tags=["UI"])

templates = Jinja2Templates(directory="templates")


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def dashboard(
    request: Request,
    service: TaskService = Depends(get_task_service),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "dashboard": service.get_dashboard(),
            "task_tree": service.get_tree(),
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

    return templates.TemplateResponse(
        request=request,
        name="task_details.html",
        context={
            "task": task_entity,
            "parent_task": parent_task,
            "child_tasks": service.get_children(task_id),
            "updated": (
                request.query_params.get("updated")
                == "true"
            ),
        },
    )


@router.get(
    "/tasks/{task_id}/edit",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def edit_task_page(
    request: Request,
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> HTMLResponse:
    task = service.get_by_id(task_id)

    if task is None:
        return templates.TemplateResponse(
            request=request,
            name="task_not_found.html",
            context={
                "task_id": task_id,
            },
            status_code=404,
        )

    return render_edit_form(
        request=request,
        task=task,
    )


@router.post(
    "/tasks/{task_id}/edit",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def update_task_from_form(
    request: Request,
    task_id: int,
    parent_task_id: int = Form(...),
    short_description: str = Form(...),
    description: str = Form(default=""),
    task_status: str = Form(...),
    priority: str = Form(...),
    task_type: str = Form(...),
    category: str = Form(default=""),
    tags: str = Form(default=""),
    planned_start_date: str = Form(default=""),
    planned_end_date: str = Form(default=""),
    actual_start_date: str = Form(default=""),
    actual_end_date: str = Form(default=""),
    due_date: str = Form(default=""),
    estimated_effort_hours: str = Form(default=""),
    actual_effort_hours: str = Form(default=""),
    remaining_effort_hours: str = Form(default=""),
    progress_percentage: int = Form(default=0),
    assigned_to: str = Form(default=""),
    team: str = Form(default=""),
    blocked_reason: str = Form(default=""),
    external_reference: str = Form(default=""),
    service: TaskService = Depends(get_task_service),
) -> HTMLResponse:
    existing_task = service.get_by_id(task_id)

    if existing_task is None:
        return templates.TemplateResponse(
            request=request,
            name="task_not_found.html",
            context={
                "task_id": task_id,
            },
            status_code=404,
        )

    try:
        task_update = TaskUpdate(
            parent_task_id=parent_task_id,
            short_description=short_description.strip(),
            description=empty_to_none(description),
            status=TaskStatus(task_status),
            priority=TaskPriority(priority),
            task_type=TaskType(task_type),
            category=empty_to_none(category),
            tags=parse_tags(tags),
            planned_start_date=parse_datetime(
                planned_start_date
            ),
            planned_end_date=parse_datetime(
                planned_end_date
            ),
            actual_start_date=parse_datetime(
                actual_start_date
            ),
            actual_end_date=parse_datetime(
                actual_end_date
            ),
            due_date=parse_datetime(due_date),
            estimated_effort_hours=parse_float(
                estimated_effort_hours
            ),
            actual_effort_hours=parse_float(
                actual_effort_hours
            ),
            remaining_effort_hours=parse_float(
                remaining_effort_hours
            ),
            progress_percentage=progress_percentage,
            assigned_to=empty_to_none(assigned_to),
            team=empty_to_none(team),
            blocked_reason=empty_to_none(
                blocked_reason
            ),
            external_reference=empty_to_none(
                external_reference
            ),
        )

        updated_task = service.update(
            task_id,
            task_update,
        )

        if updated_task is None:
            return templates.TemplateResponse(
                request=request,
                name="task_not_found.html",
                context={
                    "task_id": task_id,
                },
                status_code=404,
            )

    except (ValueError, TypeError) as error:
        form_task = build_form_task(
            existing_task=existing_task,
            parent_task_id=parent_task_id,
            short_description=short_description,
            description=description,
            task_status=task_status,
            priority=priority,
            task_type=task_type,
            category=category,
            tags=tags,
            planned_start_date=planned_start_date,
            planned_end_date=planned_end_date,
            actual_start_date=actual_start_date,
            actual_end_date=actual_end_date,
            due_date=due_date,
            estimated_effort_hours=(
                estimated_effort_hours
            ),
            actual_effort_hours=(
                actual_effort_hours
            ),
            remaining_effort_hours=(
                remaining_effort_hours
            ),
            progress_percentage=(
                progress_percentage
            ),
            assigned_to=assigned_to,
            team=team,
            blocked_reason=blocked_reason,
            external_reference=external_reference,
        )

        return render_edit_form(
            request=request,
            task=form_task,
            error_message=str(error),
            status_code=400,
        )

    return RedirectResponse(
        url=f"/tasks/{task_id}?updated=true",
        status_code=303,
    )


def render_edit_form(
    *,
    request: Request,
    task: object,
    error_message: str | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="task_edit.html",
        context={
            "task": task,
            "statuses": list(TaskStatus),
            "priorities": list(TaskPriority),
            "task_types": list(TaskType),
            "error_message": error_message,
        },
        status_code=status_code,
    )


def parse_datetime(
    value: str,
) -> datetime | None:
    cleaned_value = value.strip()

    if not cleaned_value:
        return None

    return datetime.fromisoformat(cleaned_value)


def parse_float(
    value: str,
) -> float | None:
    cleaned_value = value.strip()

    if not cleaned_value:
        return None

    return float(cleaned_value)


def parse_tags(
    value: str,
) -> list[str]:
    return [
        tag.strip()
        for tag in value.split(",")
        if tag.strip()
    ]


def empty_to_none(
    value: str,
) -> str | None:
    cleaned_value = value.strip()

    return cleaned_value or None


def build_form_task(
    *,
    existing_task: object,
    **form_values: object,
) -> object:
    class FormTask:
        pass

    task = FormTask()

    for attribute_name, attribute_value in vars(
        existing_task
    ).items():
        setattr(
            task,
            attribute_name,
            attribute_value,
        )

    for field_name, field_value in form_values.items():
        setattr(
            task,
            field_name,
            field_value,
        )

    task.status = form_values["task_status"]

    return task