from datetime import datetime, timedelta

from app.config.database import SessionLocal
from app.models.task import (
    TaskCreate,
    TaskPriority,
    TaskStatus,
    TaskType,
)
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService


def create_task(
    service: TaskService,
    *,
    short_description: str,
    parent_task_id: int = 0,
    description: str | None = None,
    status: TaskStatus = TaskStatus.NOT_STARTED,
    priority: TaskPriority = TaskPriority.MEDIUM,
    category: str | None = None,
    tags: list[str] | None = None,
    planned_start_date: datetime | None = None,
    planned_end_date: datetime | None = None,
    estimated_effort_hours: float | None = None,
    progress_percentage: int = 0,
) -> int:
    task = TaskCreate(
        parent_task_id=parent_task_id,
        short_description=short_description,
        description=description,
        status=status,
        priority=priority,
        task_type=TaskType.TASK,
        category=category,
        tags=tags or [],
        planned_start_date=planned_start_date,
        planned_end_date=planned_end_date,
        estimated_effort_hours=estimated_effort_hours,
        remaining_effort_hours=estimated_effort_hours,
        progress_percentage=progress_percentage,
        assigned_to="Kiran",
        created_by="Kiran",
    )

    created_task = service.create(task)

    print(
        f"Created: task_id={created_task.task_id}, "
        f"task_number={created_task.task_number}, "
        f"description={created_task.short_description}"
    )

    return created_task.task_id


def seed_aws_training(
    service: TaskService,
    start_date: datetime,
) -> None:
    root_id = create_task(
        service,
        short_description="Complete AWS training",
        description=(
            "Complete AWS learning plan covering core services, "
            "deployment, databases, security, and monitoring."
        ),
        priority=TaskPriority.HIGH,
        category="Learning",
        tags=["aws", "cloud", "training"],
        planned_start_date=start_date,
        planned_end_date=start_date + timedelta(days=6),
        estimated_effort_hours=10,
    )

    lesson_1_id = create_task(
        service,
        parent_task_id=root_id,
        short_description="Lesson 1 - AWS fundamentals",
        description="Learn AWS regions, availability zones, IAM, and billing.",
        priority=TaskPriority.HIGH,
        category="Learning",
        tags=["aws", "fundamentals"],
        planned_start_date=start_date,
        planned_end_date=start_date,
        estimated_effort_hours=2,
    )

    create_task(
        service,
        parent_task_id=lesson_1_id,
        short_description="Day 1 - Regions, AZs and IAM",
        description=(
            "Study AWS global infrastructure and create IAM users, "
            "groups, roles, and policies."
        ),
        priority=TaskPriority.HIGH,
        category="Learning",
        tags=["aws", "iam"],
        planned_start_date=start_date,
        planned_end_date=start_date,
        estimated_effort_hours=2,
    )

    lesson_2_id = create_task(
        service,
        parent_task_id=root_id,
        short_description="Lesson 2 - Compute services",
        description="Learn EC2, Lambda, ECS, and Fargate.",
        priority=TaskPriority.HIGH,
        category="Learning",
        tags=["aws", "ec2", "ecs", "lambda"],
        planned_start_date=start_date + timedelta(days=1),
        planned_end_date=start_date + timedelta(days=1),
        estimated_effort_hours=2,
    )

    create_task(
        service,
        parent_task_id=lesson_2_id,
        short_description="Day 2 - EC2 and ECS practice",
        description="Launch an EC2 instance and review ECS Fargate deployment.",
        priority=TaskPriority.HIGH,
        category="Learning",
        tags=["aws", "ec2", "ecs"],
        planned_start_date=start_date + timedelta(days=1),
        planned_end_date=start_date + timedelta(days=1),
        estimated_effort_hours=2,
    )


def seed_fastapi_project(
    service: TaskService,
    start_date: datetime,
) -> None:
    root_id = create_task(
        service,
        short_description="Build personal FastAPI project",
        description="Complete the local task-management application.",
        priority=TaskPriority.HIGH,
        category="Development",
        tags=["python", "fastapi"],
        planned_start_date=start_date,
        planned_end_date=start_date + timedelta(days=5),
        estimated_effort_hours=8,
    )

    api_id = create_task(
        service,
        parent_task_id=root_id,
        short_description="Build task-management API",
        description="Complete task CRUD, filtering, tree, and dashboard APIs.",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH,
        category="Development",
        tags=["fastapi", "api"],
        planned_start_date=start_date,
        planned_end_date=start_date + timedelta(days=2),
        estimated_effort_hours=4,
        progress_percentage=70,
    )

    create_task(
        service,
        parent_task_id=api_id,
        short_description="Add automated API tests",
        description="Test create, update, delete, filters, tree, and dashboard.",
        priority=TaskPriority.MEDIUM,
        category="Testing",
        tags=["pytest", "testing"],
        planned_start_date=start_date,
        planned_end_date=start_date,
        estimated_effort_hours=2,
    )


def seed_mainframe_learning(
    service: TaskService,
    start_date: datetime,
) -> None:
    root_id = create_task(
        service,
        short_description="Modernize mainframe skills",
        description="Learn off-host integration and modern engineering tools.",
        priority=TaskPriority.HIGH,
        category="Career",
        tags=["mainframe", "modernization"],
        planned_start_date=start_date,
        planned_end_date=start_date + timedelta(days=14),
        estimated_effort_hours=12,
    )

    integration_id = create_task(
        service,
        parent_task_id=root_id,
        short_description="Learn mainframe API integration",
        description="Study REST APIs, CICS integration, and event-driven patterns.",
        priority=TaskPriority.HIGH,
        category="Career",
        tags=["mainframe", "rest-api", "cics"],
        planned_start_date=start_date + timedelta(days=2),
        planned_end_date=start_date + timedelta(days=5),
        estimated_effort_hours=4,
    )

    create_task(
        service,
        parent_task_id=integration_id,
        short_description="Create sample CICS REST design",
        description="Document a sample request, response, routing, and error flow.",
        priority=TaskPriority.MEDIUM,
        category="Career",
        tags=["cics", "architecture"],
        planned_start_date=start_date + timedelta(days=3),
        planned_end_date=start_date + timedelta(days=3),
        estimated_effort_hours=2,
    )


def seed_health_routine(
    service: TaskService,
    start_date: datetime,
) -> None:
    root_id = create_task(
        service,
        short_description="Follow daily health routine",
        description="Maintain breathing, walking, meditation, and healthy meals.",
        priority=TaskPriority.HIGH,
        category="Health",
        tags=["health", "routine"],
        planned_start_date=start_date,
        planned_end_date=start_date + timedelta(days=30),
        estimated_effort_hours=15,
    )

    morning_id = create_task(
        service,
        parent_task_id=root_id,
        short_description="Complete morning routine",
        description="Breathing, light exercise, and daily planning.",
        priority=TaskPriority.HIGH,
        category="Health",
        tags=["morning", "wellness"],
        planned_start_date=start_date,
        planned_end_date=start_date,
        estimated_effort_hours=0.5,
    )

    create_task(
        service,
        parent_task_id=morning_id,
        short_description="Do five minutes of breathing",
        description="Complete slow breathing before starting office work.",
        priority=TaskPriority.MEDIUM,
        category="Health",
        tags=["breathing", "mindfulness"],
        planned_start_date=start_date,
        planned_end_date=start_date,
        estimated_effort_hours=0.1,
    )


def seed_weekly_planning(
    service: TaskService,
    start_date: datetime,
) -> None:
    root_id = create_task(
        service,
        short_description="Complete weekly planning",
        description="Review achievements, pending work, and next-week priorities.",
        priority=TaskPriority.MEDIUM,
        category="Planning",
        tags=["weekly-review", "planning"],
        planned_start_date=start_date + timedelta(days=5),
        planned_end_date=start_date + timedelta(days=6),
        estimated_effort_hours=1,
    )

    review_id = create_task(
        service,
        parent_task_id=root_id,
        short_description="Review completed and pending tasks",
        description="Check completed, overdue, blocked, and deferred work.",
        priority=TaskPriority.MEDIUM,
        category="Planning",
        tags=["review"],
        planned_start_date=start_date + timedelta(days=5),
        planned_end_date=start_date + timedelta(days=5),
        estimated_effort_hours=0.5,
    )

    create_task(
        service,
        parent_task_id=review_id,
        short_description="Prepare next week's top five priorities",
        description="Select the five most important tasks for the coming week.",
        priority=TaskPriority.MEDIUM,
        category="Planning",
        tags=["priorities"],
        planned_start_date=start_date + timedelta(days=6),
        planned_end_date=start_date + timedelta(days=6),
        estimated_effort_hours=0.5,
    )


def main() -> None:
    database = SessionLocal()

    try:
        repository = TaskRepository(database)
        service = TaskService(repository)

        today = datetime.now().replace(
            hour=9,
            minute=0,
            second=0,
            microsecond=0,
        )

        seed_aws_training(service, today)
        seed_fastapi_project(service, today)
        seed_mainframe_learning(service, today)
        seed_health_routine(service, today)
        seed_weekly_planning(service, today)

        print("\nSample tasks created successfully.")

    except Exception:
        database.rollback()
        raise

    finally:
        database.close()


if __name__ == "__main__":
    main()