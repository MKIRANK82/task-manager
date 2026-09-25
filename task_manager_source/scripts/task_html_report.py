import sqlite3
import webbrowser
from datetime import datetime, date
from html import escape
from pathlib import Path


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DB_PATH = Path("task.db")

OUTPUT_FOLDER = Path("data/reports")

OUTPUT_FILE = OUTPUT_FOLDER / "task_report.html"

FINAL_STATUSES = (
    "completed",
    "cancelled",
    "closed",
)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def format_datetime(value):
    if not value:
        return ""

    try:
        dt = datetime.fromisoformat(value)

        return dt.strftime(
            "%d-%b-%Y %H:%M"
        )

    except (ValueError, TypeError):
        return str(value)


def format_status(value):
    if not value:
        return ""

    return (
        str(value)
        .replace("_", " ")
        .title()
    )


def safe(value):
    if value is None:
        return ""

    return escape(str(value))


# ---------------------------------------------------------
# Build task hierarchy lookup
# ---------------------------------------------------------

def load_task_lookup(connection):
    """
    Load all tasks once.

    This is used to build hierarchy information
    without querying the database repeatedly.
    """

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            task_id,
            task_number,
            parent_task_id,
            short_description
        FROM tasks
        """
    )

    tasks = cursor.fetchall()

    return {
        task["task_id"]: task
        for task in tasks
    }


def get_hierarchy(task, task_lookup):
    """
    Example:

    Current task:
        2.4.2  Create Document

    Hierarchy:
        2.4  API Development
        2    Main Project

    Nearest parent is shown first.
    """

    hierarchy = []

    parent_task_id = task["parent_task_id"]

    visited = set()

    while (
        parent_task_id
        and parent_task_id != 0
        and parent_task_id not in visited
    ):

        visited.add(
            parent_task_id
        )

        parent = task_lookup.get(
            parent_task_id
        )

        if parent is None:
            break

        hierarchy.append(
            {
                "task_number":
                    parent["task_number"],

                "short_description":
                    parent["short_description"],
            }
        )

        parent_task_id = (
            parent["parent_task_id"]
        )

    return hierarchy


def hierarchy_to_html(
    task,
    task_lookup,
):
    hierarchy = get_hierarchy(
        task,
        task_lookup,
    )

    if not hierarchy:
        return """
        <span class="no-hierarchy">
            —
        </span>
        """

    lines = []

    for parent in hierarchy:

        parent_number = safe(
            parent["task_number"]
        )

        parent_description = safe(
            parent["short_description"]
        )

        lines.append(
            f"""
            <div class="hierarchy-item">

                <span class="hierarchy-number">
                    {parent_number}
                </span>

                <span class="hierarchy-description">
                    {parent_description}
                </span>

            </div>
            """
        )

    return "".join(lines)


# ---------------------------------------------------------
# Read tasks
# ---------------------------------------------------------

def read_tasks():

    today = date.today()

    today_text = today.isoformat()

    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # -----------------------------------------------------
    # Load all tasks for hierarchy lookup
    # -----------------------------------------------------

    task_lookup = load_task_lookup(
        connection
    )

    # -----------------------------------------------------
    # 1. Tasks starting today
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            task_id,
            task_number,
            parent_task_id,
            short_description,
            status,
            priority,
            category,
            planned_start_date,
            planned_end_date,
            progress_percentage

        FROM tasks

        WHERE
            DATE(planned_start_date) = ?

            AND is_active = 1

            AND LOWER(status) NOT IN (
                'completed',
                'cancelled',
                'closed'
            )

        ORDER BY
            planned_start_date,
            task_number
        """,
        (today_text,),
    )

    starts_today = cursor.fetchall()

    # -----------------------------------------------------
    # 2. Blocked tasks
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            task_id,
            task_number,
            parent_task_id,
            short_description,
            status,
            priority,
            category,
            planned_start_date,
            planned_end_date,
            progress_percentage,
            blocked_reason

        FROM tasks

        WHERE
            LOWER(status) = 'blocked'

            AND is_active = 1

        ORDER BY
            planned_end_date,
            task_number
        """
    )

    blocked_tasks = cursor.fetchall()

    # -----------------------------------------------------
    # 3. Tasks already started and still open
    #
    # planned start < today
    # planned end >= today OR no end date
    # not completed/cancelled/closed
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            task_id,
            task_number,
            parent_task_id,
            short_description,
            status,
            priority,
            category,
            planned_start_date,
            planned_end_date,
            progress_percentage

        FROM tasks

        WHERE
            is_active = 1

            AND planned_start_date IS NOT NULL

            AND DATE(planned_start_date) < ?

            AND (
                planned_end_date IS NULL

                OR DATE(planned_end_date) >= ?
            )

            AND LOWER(status) NOT IN (
                'completed',
                'cancelled',
                'closed'
            )

        ORDER BY
            planned_end_date,
            priority,
            task_number
        """,
        (
            today_text,
            today_text,
        ),
    )

    open_tasks = cursor.fetchall()

    connection.close()

    return (
        starts_today,
        blocked_tasks,
        open_tasks,
        task_lookup,
    )


# ---------------------------------------------------------
# HTML table
# ---------------------------------------------------------

def create_task_table(
    tasks,
    task_lookup,
    include_blocked_reason=False,
):

    if not tasks:
        return """
        <div class="empty">
            No tasks found.
        </div>
        """

    rows = []

    for task in tasks:

        task_number = safe(
            task["task_number"]
        )

        description = safe(
            task["short_description"]
        )

        hierarchy = hierarchy_to_html(
            task,
            task_lookup,
        )

        status = format_status(
            task["status"]
        )

        priority = format_status(
            task["priority"]
        )

        category = safe(
            task["category"]
        )

        start_date = format_datetime(
            task["planned_start_date"]
        )

        end_date = format_datetime(
            task["planned_end_date"]
        )

        progress = (
            task["progress_percentage"]
            if task["progress_percentage"]
            is not None
            else 0
        )

        blocked_reason_html = ""

        if include_blocked_reason:

            reason = safe(
                task["blocked_reason"]
            )

            blocked_reason_html = (
                f"<td>{reason}</td>"
            )

        rows.append(
            f"""
            <tr>

                <td class="task-number">
                    {task_number}
                </td>

                <td class="description">
                    {description}
                </td>

                <td class="hierarchy">
                    {hierarchy}
                </td>

                <td>
                    <span class="status">
                        {safe(status)}
                    </span>
                </td>

                <td>
                    {safe(priority)}
                </td>

                <td>
                    {category}
                </td>

                <td>
                    {safe(start_date)}
                </td>

                <td>
                    {safe(end_date)}
                </td>

                <td>
                    {progress}%
                </td>

                {blocked_reason_html}

            </tr>
            """
        )

    blocked_header = ""

    if include_blocked_reason:

        blocked_header = (
            "<th>Blocked Reason</th>"
        )

    return f"""
    <div class="table-wrapper">

        <table>

            <thead>

                <tr>
                    <th>Task</th>

                    <th>Description</th>

                    <th>Hierarchy</th>

                    <th>Status</th>

                    <th>Priority</th>

                    <th>Category</th>

                    <th>Planned Start</th>

                    <th>Planned End</th>

                    <th>Progress</th>

                    {blocked_header}
                </tr>

            </thead>

            <tbody>

                {''.join(rows)}

            </tbody>

        </table>

    </div>
    """


# ---------------------------------------------------------
# Generate HTML
# ---------------------------------------------------------

def generate_html():

    (
        starts_today,
        blocked_tasks,
        open_tasks,
        task_lookup,
    ) = read_tasks()

    today_display = (
        date.today()
        .strftime(
            "%d %B %Y"
        )
    )

    generated_time = (
        datetime.now()
        .strftime(
            "%d-%b-%Y %H:%M"
        )
    )

    html = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <title>
        Task Manager Report
    </title>

    <style>

        body {{
            font-family:
                Arial,
                Helvetica,
                sans-serif;

            background: #f5f7fa;

            margin: 0;

            padding: 30px;
        }}

        .container {{
            max-width: 1600px;

            margin: auto;
        }}

        h1 {{
            margin-bottom: 5px;
        }}

        .generated {{
            color: #666;

            margin-bottom: 30px;
        }}

        .section {{
            background: white;

            margin-bottom: 30px;

            padding: 22px;

            border-radius: 10px;

            box-shadow:
                0 2px 8px
                rgba(0, 0, 0, 0.08);
        }}

        .section-header {{
            display: flex;

            justify-content:
                space-between;

            align-items: center;

            margin-bottom: 15px;
        }}

        .section-header h2 {{
            margin: 0;
        }}

        .count {{
            font-size: 14px;

            padding:
                6px
                12px;

            background: #eef2f7;

            border-radius: 20px;

            font-weight: bold;
        }}

        .table-wrapper {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;

            border-collapse:
                collapse;
        }}

        th {{
            background: #f1f3f5;

            text-align: left;

            padding: 10px;

            border-bottom:
                2px solid #ddd;

            white-space: nowrap;
        }}

        td {{
            padding: 10px;

            border-bottom:
                1px solid #eee;

            vertical-align: top;
        }}

        tr:hover {{
            background: #fafafa;
        }}

        .task-number {{
            font-weight: bold;

            white-space: nowrap;
        }}

        .description {{
            min-width: 240px;
        }}

        .hierarchy {{
            min-width: 280px;

            font-size: 13px;

            line-height: 1.6;
        }}

        .hierarchy-item {{
            display: flex;

            align-items: flex-start;

            margin-bottom: 2px;
        }}

        .hierarchy-number {{
            display: inline-block;

            min-width: 65px;

            font-weight: bold;
        }}

        .hierarchy-description {{
            color: #444;
        }}

        .no-hierarchy {{
            color: #999;
        }}

        .empty {{
            padding: 20px;

            background: #fafafa;

            color: #777;

            border-radius: 6px;
        }}

        .starts-today {{
            border-left:
                5px solid #198754;
        }}

        .blocked {{
            border-left:
                5px solid #dc3545;
        }}

        .open {{
            border-left:
                5px solid #0d6efd;
        }}

    </style>

</head>


<body>

<div class="container">

    <h1>
        Task Manager Report
    </h1>

    <div class="generated">

        Date:

        <strong>
            {today_display}
        </strong>

        &nbsp; | &nbsp;

        Generated:

        {generated_time}

    </div>


    <!-- ======================================= -->
    <!-- STARTING TODAY -->
    <!-- ======================================= -->

    <div class="section starts-today">

        <div class="section-header">

            <h2>
                Tasks Starting Today
            </h2>

            <div class="count">
                {len(starts_today)} Tasks
            </div>

        </div>

        {
            create_task_table(
                starts_today,
                task_lookup,
            )
        }

    </div>


    <!-- ======================================= -->
    <!-- BLOCKED -->
    <!-- ======================================= -->

    <div class="section blocked">

        <div class="section-header">

            <h2>
                Blocked Tasks
            </h2>

            <div class="count">
                {len(blocked_tasks)} Tasks
            </div>

        </div>

        {
            create_task_table(
                blocked_tasks,
                task_lookup,
                include_blocked_reason=True,
            )
        }

    </div>


    <!-- ======================================= -->
    <!-- OPEN / ACTIVE -->
    <!-- ======================================= -->

    <div class="section open">

        <div class="section-header">

            <h2>
                Open Tasks Already Started
            </h2>

            <div class="count">
                {len(open_tasks)} Tasks
            </div>

        </div>

        <p>
            Started before today and planned end
            is today or later.
        </p>

        {
            create_task_table(
                open_tasks,
                task_lookup,
            )
        }

    </div>

</div>

</body>

</html>
"""

    OUTPUT_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        html,
        encoding="utf-8",
    )

    return OUTPUT_FILE.resolve()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    report_file = generate_html()

    print(
        f"Report created: {report_file}"
    )

    webbrowser.open(
        report_file.as_uri()
    )