from datetime import date, datetime, time, timedelta

from sqlalchemy import or_, select

from app.config.database import SessionLocal
from app.models.task import TaskStatus
from app.models.task_entity import TaskEntity


def get_day_range(target_date: date) -> tuple[datetime, datetime]:
    start = datetime.combine(target_date, time.min)
    end = start + timedelta(days=1)
    return start, end


def get_todays_tasks(database) -> list[TaskEntity]:
    today_start, tomorrow_start = get_day_range(date.today())

    statement = (
        select(TaskEntity)
        .where(
            TaskEntity.is_active.is_(True),
            TaskEntity.status.notin_(
                [
                    TaskStatus.COMPLETED.value,
                    TaskStatus.CANCELLED.value,
                ]
            ),
            or_(
                (
                    TaskEntity.planned_start_date >= today_start
                )
                & (
                    TaskEntity.planned_start_date < tomorrow_start
                ),
                (
                    TaskEntity.due_date >= today_start
                )
                & (
                    TaskEntity.due_date < tomorrow_start
                ),
            ),
        )
        .order_by(
            TaskEntity.priority.desc(),
            TaskEntity.planned_start_date,
            TaskEntity.task_id,
        )
    )

    return list(database.scalars(statement).all())


def get_yesterdays_status(database) -> list[TaskEntity]:
    yesterday = date.today() - timedelta(days=1)
    yesterday_start, today_start = get_day_range(yesterday)

    statement = (
        select(TaskEntity)
        .where(
            TaskEntity.is_active.is_(True),
            or_(
                (
                    TaskEntity.actual_end_date >= yesterday_start
                )
                & (
                    TaskEntity.actual_end_date < today_start
                ),
                (
                    TaskEntity.planned_end_date >= yesterday_start
                )
                & (
                    TaskEntity.planned_end_date < today_start
                ),
            ),
        )
        .order_by(TaskEntity.task_id)
    )

    return list(database.scalars(statement).all())


def build_email_body(
    todays_tasks: list[TaskEntity],
    yesterdays_tasks: list[TaskEntity],
) -> str:
    lines: list[str] = []

    lines.append("Good morning Kiran,")
    lines.append("")
    lines.append("Today's tasks")
    lines.append("-------------")

    if not todays_tasks:
        lines.append("No tasks are planned or due today.")
    else:
        for task in todays_tasks:
            lines.append(
                f"{task.task_number} - "
                f"{task.short_description} "
                f"[{task.priority}]"
            )

    lines.append("")
    lines.append("Yesterday's status")
    lines.append("------------------")

    if not yesterdays_tasks:
        lines.append("No tasks were completed or due yesterday.")
    else:
        for task in yesterdays_tasks:
            lines.append(
                f"{task.task_number} - "
                f"{task.short_description} "
                f"[{task.status}]"
            )

    lines.append("")
    lines.append("Task Manager")

    return "\n".join(lines)


def send_email(subject: str, body: str) -> None:
    # Add SMTP, Outlook, Graph API, or Gmail code here.
    print(subject)
    print()
    print(body)


def main() -> None:
    database = SessionLocal()

    try:
        todays_tasks = get_todays_tasks(database)
        yesterdays_tasks = get_yesterdays_status(database)

        body = build_email_body(
            todays_tasks=todays_tasks,
            yesterdays_tasks=yesterdays_tasks,
        )

        send_email(
            subject=f"Daily Task Summary - {date.today():%d %b %Y}",
            body=body,
        )
    finally:
        database.close()


if __name__ == "__main__":
    main()