from typing import Any
import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "status_code,error_detail",
    [
        (200, None),
    ],
)
async def test_create_task(
    status_code: int,
    error_detail: str,
    ac: AsyncClient,
    additional_test_data: dict[str, Any],
) -> None:
    task_data = {
        "user_id": str(additional_test_data["tasks"][0]["user_id"]),
        "section_id": str(additional_test_data["tasks"][0]["section_id"]),
        "title": additional_test_data["tasks"][0]["title"],
        "description": additional_test_data["tasks"][0]["description"],
    }

    response = await ac.post("/api/task", json=task_data)

    assert response.status_code == status_code

    if status_code == 200:
        data = response.json()
        assert "message" in data
        assert data["message"] == "Task created"
        assert "id" in data

    if error_detail:
        data = response.json()
        assert "detail" in data
        assert data["detail"] == error_detail


@pytest.mark.parametrize(
    "task_id, status_code, error_detail",
    [
        ("existing", 200, None),
        (
            # random UUID
            "f8b057ea-8c3c-4d14-9b95-ef9acbccffa6",
            404,
            "There is no task with {'task_id': UUID('f8b057ea-8c3c-4d14-9b95-ef9acbccffa6')}",
        ),
    ],
)
async def test_update_task(
    task_id: str,
    status_code: int,
    error_detail: str,
    ac: AsyncClient,
    db_tasks_data: list[dict[str, Any]],
) -> None:
    existing_task_data = db_tasks_data[2]
    task_data = {
        "id": existing_task_data["id"] if task_id == "existing" else task_id,
        "description": "Bravo, Vince",
    }

    response = await ac.patch("/api/task", json=task_data)

    assert response.status_code == status_code

    if status_code == 200:
        data = response.json()
        assert "message" in data
        assert data["message"] == "Task updated"

    if error_detail:
        data = response.json()
        assert "detail" in data
        assert data["detail"] == error_detail


async def test_create_section(
    ac: AsyncClient,
    additional_test_data: dict[str, Any],
) -> None:
    section_data = additional_test_data["sections"][0]
    response = await ac.post("/api/section", json=section_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Session created"
    assert "id" in data


@pytest.mark.parametrize(
    "id_,status_code,error_detail",
    [
        ("6ff6e896-5da3-46ec-bf66-0a317c5496fa", 200, None),
        (
            "2a931634-6941-4523-acbd-980c8ba622ca",
            404,
            "There is no section with {'section_id': UUID('2a931634-6941-4523-acbd-980c8ba622ca')}",
        ),
    ],
)
async def test_get_section(
    id_: str,
    status_code: int,
    error_detail: str,
    ac: AsyncClient,
    db_tasks_data: list[dict[str, Any]],
) -> None:
    response = await ac.get(f"/api/section/{id_}")
    assert response.status_code == status_code
    if not response.is_success:
        assert response.json()["detail"] == error_detail
        return
    expected_tasks_n = sum(task["section_id"] == id_ for task in db_tasks_data)
    assert expected_tasks_n == len(response.json()["tasks"])
