from typing import Any, Optional
import pytest
from httpx import AsyncClient


# TODO: test task creation with `recurrence`
@pytest.mark.parametrize(
    "status_code,error_detail",
    [
        (201, None),
    ],
)
async def test_create_task(
    status_code: int,
    error_detail: Optional[str],
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

    if status_code == 201:
        data = response.json()
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
    error_detail: Optional[str],
    ac: AsyncClient,
    tasks_data: list[dict[str, Any]],
) -> None:
    existing_task_data = tasks_data[2]
    task_data = {
        "id": existing_task_data["id"] if task_id == "existing" else task_id,
        "description": "Bravo, Vince",
    }

    response = await ac.patch("/api/task", json=task_data)

    assert response.status_code == status_code

    if status_code == 200:
        data = response.json()

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
    assert response.status_code == 201
    data = response.json()
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
    error_detail: Optional[str],
    ac: AsyncClient,
    tasks_data: list[dict[str, Any]],
) -> None:
    response = await ac.get(f"/api/section/{id_}")
    assert response.status_code == status_code
    if not response.is_success:
        assert response.json()["detail"] == error_detail
        return
    expected_tasks_n = sum(task["section_id"] == id_ for task in tasks_data)
    assert expected_tasks_n == len(response.json()["tasks"])


@pytest.mark.parametrize(
    "task_id,section_id,index,status_code,error_detail",
    [
        (
            "e6a76c36-7dae-47ee-b657-1a0b02ca40df",
            "36ea0a4f-0334-464d-8066-aa359ecfdcba",
            0,  # move to the beginning of empty section
            200,
            None,
        ),
        (
            "e6a76c36-7dae-47ee-b657-1a0b02ca40df",
            "36ea0a4f-0334-464d-8066-aa359ecfdcba",
            123,  # move to an incorrect index
            422,
            "The task can't be moved to the specified index",
        ),
    ],
)
async def test_move_task(
    task_id: str,
    section_id: str,
    index: int,
    status_code: int,
    error_detail: Optional[str],
    ac: AsyncClient,
) -> None:
    response = await ac.post(
        "/api/task/move",
        json={
            "task_id": task_id,
            "section_to_id": section_id,
            "index": index,
        },
    )
    assert response.status_code == status_code
    if not response.is_success:
        assert response.json()["detail"] == error_detail
        return


@pytest.mark.parametrize(
    "task_id",
    ["f4186c04-3f2d-4217-a6ed-5c40bc9946d2"],
)
async def test_toggle_completed_task(
    task_id: str,
    ac: AsyncClient,
) -> None:
    for expected_is_completed in [True, False, True]:
        response = await ac.post(
            "/api/task/toggle_completed",
            json={
                "task_id": task_id,
            },
        )
        data = response.json()
        assert data["is_completed"] is expected_is_completed


@pytest.mark.parametrize(
    "user_id, not_before, not_after, n_tasks_expected, status_code, error_detail",
    [
        # TODO: nonexisting user -> 404
        (
            "38df4136-36b2-4171-8459-27f411af8323",
            "2001-01-01",
            "2002-12-31",
            244,
            200,
            None,
        ),
        (
            "38df4136-36b2-4171-8459-27f411af8323",
            "2002-12-31",
            "2001-01-01",
            0,
            422,
            "Incorrect date interval",
        ),
    ],
)
async def test_get_tasks_by_date(
    user_id: str,
    not_before: str,
    not_after: str,
    n_tasks_expected: int,
    status_code: int,
    error_detail: Optional[str],
    ac: AsyncClient,
) -> None:
    response = await ac.get(
        "/api/task/by_date",
        params={
            "user_id": user_id,
            "not_before": not_before,
            "not_after": not_after,
        },
    )
    assert response.status_code == status_code
    if not response.is_success:
        assert response.json()["detail"] == error_detail
        return
    tasks_by_date = response.json()

    n_tasks = sum(len(tasks_by_date[date_]) for date_ in tasks_by_date)
    assert n_tasks == n_tasks_expected


@pytest.mark.parametrize(
    "task_id, status_code,error_detail",
    [
        ("existing", 200, None),
        (
            "f8b057ea-8c3c-4d14-9b95-ef9acbccffa6",  # random UUID
            404,
            "There is no task with {'task_id': UUID('f8b057ea-8c3c-4d14-9b95-ef9acbccffa6')}",
        ),
    ],
)
async def test_add_attachment(
    task_id: str,
    status_code: int,
    error_detail: Optional[str],
    ac: AsyncClient,
    tasks_data: list[dict[str, Any]],
) -> None:
    # NOTE: running S3 is not required for this test, as this endpoint just
    # generates pre-signed link "offline"
    existing_task_data = tasks_data[2]
    task_id = existing_task_data["id"] if task_id == "existing" else task_id

    request_data = {
        "task_id": task_id,
        "aes_key_b64": "someBase64EncodedAESKey==",
        "aes_iv_b64": "someBase64EncodedIV==",
    }

    response = await ac.post("/api/task/attachment", json=request_data)

    assert response.status_code == status_code

    if status_code == 200:
        data = response.json()
        assert "post_url" in data
        assert "post_fields" in data
        assert isinstance(data["post_fields"], dict)

    if error_detail:
        data = response.json()
        assert "detail" in data
        assert data["detail"] == error_detail
        return

    section_id = existing_task_data["section_id"]
    response = await ac.get(f"/api/section/{section_id}")
    task_got = next(t for t in response.json()["tasks"] if t["id"] == task_id)
    assert len(task_got["attachments"]) == 1
    assert task_got["attachments"][0]["aes_key_b64"] == request_data["aes_key_b64"]
    assert task_got["attachments"][0]["aes_iv_b64"] == request_data["aes_iv_b64"]
    assert task_got["attachments"][0]["s3_file_key"]
    assert task_got["attachments"][0]["task_id"] == task_id
