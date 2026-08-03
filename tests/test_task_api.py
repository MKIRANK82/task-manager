from fastapi.testclient import TestClient


API_BASE = "/api/v1/tasks"


def create_task(
    client: TestClient,
    *,
    parent_task_id: int = 0,
    short_description: str = "Test task",
    status: str = "not_started",
    priority: str = "medium",
) -> dict:
    response = client.post(
        API_BASE,
        json={
            "parent_task_id": parent_task_id,
            "short_description": short_description,
            "status": status,
            "priority": priority,
            "created_by": "Kiran",
        },
    )

    assert response.status_code == 201

    response_body = response.json()

    assert response_body["success"] is True
    assert response_body["code"] == "TASK_CREATED"
    assert response_body["data"] is not None

    return response_body["data"]


def test_health_endpoint(
    client: TestClient,
) -> None:
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["code"] == "API_HEALTHY"
    assert body["data"]["status"] == "healthy"
    assert body["correlation_id"]


def test_create_root_task(
    client: TestClient,
) -> None:
    task = create_task(
        client,
        short_description="Build task manager",
    )

    assert task["task_id"] == 1
    assert task["task_number"] == "1"
    assert task["parent_task_id"] == 0
    assert task["short_description"] == "Build task manager"
    assert task["status"] == "not_started"
    assert task["is_active"] is True


def test_create_child_task(
    client: TestClient,
) -> None:
    parent = create_task(
        client,
        short_description="Parent task",
    )

    child = create_task(
        client,
        parent_task_id=parent["task_id"],
        short_description="Child task",
    )

    assert child["task_id"] == 2
    assert child["task_number"] == "1.1"
    assert child["parent_task_id"] == parent["task_id"]


def test_create_multiple_child_tasks(
    client: TestClient,
) -> None:
    parent = create_task(
        client,
        short_description="Parent task",
    )

    first_child = create_task(
        client,
        parent_task_id=parent["task_id"],
        short_description="First child",
    )

    second_child = create_task(
        client,
        parent_task_id=parent["task_id"],
        short_description="Second child",
    )

    assert first_child["task_number"] == "1.1"
    assert second_child["task_number"] == "1.2"


def test_create_third_level_task(
    client: TestClient,
) -> None:
    root = create_task(
        client,
        short_description="Root task",
    )

    child = create_task(
        client,
        parent_task_id=root["task_id"],
        short_description="Child task",
    )

    grandchild = create_task(
        client,
        parent_task_id=child["task_id"],
        short_description="Grandchild task",
    )

    assert grandchild["task_number"] == "1.1.1"
    assert grandchild["parent_task_id"] == child["task_id"]


def test_create_task_with_invalid_parent(
    client: TestClient,
) -> None:
    response = client.post(
        API_BASE,
        json={
            "parent_task_id": 999,
            "short_description": "Invalid child",
            "created_by": "Kiran",
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["code"] == "INVALID_PARENT_TASK"
    assert "does not exist" in body["message"]


def test_validation_error_response(
    client: TestClient,
) -> None:
    response = client.post(
        API_BASE,
        json={
            "parent_task_id": -1,
            "short_description": "",
            "created_by": "Kiran",
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["success"] is False
    assert body["code"] == "VALIDATION_ERROR"
    assert body["data"] is None
    assert body["details"]
    assert body["correlation_id"]


def test_get_task_by_id(
    client: TestClient,
) -> None:
    created_task = create_task(
        client,
        short_description="Retrieve this task",
    )

    response = client.get(
        f"{API_BASE}/{created_task['task_id']}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["code"] == "TASK_RETRIEVED"
    assert body["data"]["task_id"] == created_task["task_id"]
    assert (
        body["data"]["short_description"]
        == "Retrieve this task"
    )


def test_get_missing_task(
    client: TestClient,
) -> None:
    response = client.get(f"{API_BASE}/999")

    assert response.status_code == 404

    body = response.json()

    assert body["success"] is False
    assert body["code"] == "TASK_NOT_FOUND"
    assert body["data"] is None


def test_get_tasks_with_pagination(
    client: TestClient,
) -> None:
    create_task(client, short_description="Task one")
    create_task(client, short_description="Task two")
    create_task(client, short_description="Task three")

    response = client.get(
        API_BASE,
        params={
            "page": 1,
            "page_size": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 2


def test_filter_tasks_by_status(
    client: TestClient,
) -> None:
    create_task(
        client,
        short_description="Pending task",
        status="not_started",
    )

    create_task(
        client,
        short_description="Active task",
        status="in_progress",
    )

    response = client.get(
        API_BASE,
        params={
            "status": "in_progress",
        },
    )

    assert response.status_code == 200

    items = response.json()["data"]["items"]

    assert len(items) == 1
    assert items[0]["status"] == "in_progress"
    assert items[0]["short_description"] == "Active task"


def test_search_tasks(
    client: TestClient,
) -> None:
    create_task(
        client,
        short_description="Learn FastAPI",
    )

    create_task(
        client,
        short_description="Complete office work",
    )

    response = client.get(
        API_BASE,
        params={
            "search": "FastAPI",
        },
    )

    assert response.status_code == 200

    items = response.json()["data"]["items"]

    assert len(items) == 1
    assert items[0]["short_description"] == "Learn FastAPI"


def test_update_task_status(
    client: TestClient,
) -> None:
    task = create_task(
        client,
        short_description="Start this task",
    )

    response = client.put(
        f"{API_BASE}/{task['task_id']}",
        json={
            "status": "in_progress",
            "progress_percentage": 25,
        },
    )

    assert response.status_code == 200

    updated_task = response.json()["data"]

    assert updated_task["status"] == "in_progress"
    assert updated_task["progress_percentage"] == 25
    assert updated_task["actual_start_date"] is not None


def test_complete_task(
    client: TestClient,
) -> None:
    task = create_task(
        client,
        short_description="Complete this task",
    )

    response = client.put(
        f"{API_BASE}/{task['task_id']}",
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 200

    completed_task = response.json()["data"]

    assert completed_task["status"] == "completed"
    assert completed_task["progress_percentage"] == 100
    assert completed_task["remaining_effort_hours"] == 0
    assert completed_task["actual_start_date"] is not None
    assert completed_task["actual_end_date"] is not None


def test_delete_task(
    client: TestClient,
) -> None:
    task = create_task(
        client,
        short_description="Delete this task",
    )

    delete_response = client.delete(
        f"{API_BASE}/{task['task_id']}"
    )

    assert delete_response.status_code == 200

    delete_body = delete_response.json()

    assert delete_body["success"] is True
    assert delete_body["code"] == "TASK_DELETED"

    get_response = client.get(
        f"{API_BASE}/{task['task_id']}"
    )

    assert get_response.status_code == 404


def test_cannot_delete_task_with_active_children(
    client: TestClient,
) -> None:
    parent = create_task(
        client,
        short_description="Parent task",
    )

    create_task(
        client,
        parent_task_id=parent["task_id"],
        short_description="Child task",
    )

    response = client.delete(
        f"{API_BASE}/{parent['task_id']}"
    )

    assert response.status_code == 409

    body = response.json()

    assert body["success"] is False
    assert body["code"] == "TASK_HAS_ACTIVE_CHILDREN"


def test_task_tree(
    client: TestClient,
) -> None:
    root = create_task(
        client,
        short_description="Root task",
    )

    child = create_task(
        client,
        parent_task_id=root["task_id"],
        short_description="Child task",
    )

    create_task(
        client,
        parent_task_id=child["task_id"],
        short_description="Grandchild task",
    )

    response = client.get(f"{API_BASE}/tree")

    assert response.status_code == 200

    tree = response.json()["data"]

    assert len(tree) == 1
    assert tree[0]["task_number"] == "1"

    assert len(tree[0]["children"]) == 1
    assert tree[0]["children"][0]["task_number"] == "1.1"

    assert len(tree[0]["children"][0]["children"]) == 1
    assert (
        tree[0]["children"][0]["children"][0]["task_number"]
        == "1.1.1"
    )


def test_dashboard(
    client: TestClient,
) -> None:
    create_task(
        client,
        short_description="In-progress task",
        status="in_progress",
    )

    create_task(
        client,
        short_description="Blocked task",
        status="blocked",
        priority="high",
    )

    response = client.get(f"{API_BASE}/dashboard")

    assert response.status_code == 200

    dashboard = response.json()["data"]

    assert dashboard["total_active"] == 2
    assert dashboard["in_progress"] == 1
    assert dashboard["blocked"] == 1
    assert dashboard["high_priority"] == 1


def test_correlation_id_is_returned(
    client: TestClient,
) -> None:
    correlation_id = "test-correlation-id-123"

    response = client.get(
        "/health",
        headers={
            "X-Correlation-ID": correlation_id,
        },
    )

    assert response.status_code == 200
    assert (
        response.headers["X-Correlation-ID"]
        == correlation_id
    )
    assert response.json()["correlation_id"] == correlation_id