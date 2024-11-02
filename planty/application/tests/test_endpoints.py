from typing import Any, Optional
import httpx
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
        assert data["detail"] == error_detail


async def test_update_another_user_task(
    ac_another_user: AsyncClient,
    tasks_data: list[dict[str, Any]],
) -> None:
    existing_task_data = tasks_data[2]
    task_data = {
        "id": existing_task_data["id"],
        "description": "Bravo, Vince",
    }

    response = await ac_another_user.patch("/api/task", json=task_data)

    assert response.status_code == 403


async def test_get_sections(
    ac: AsyncClient,
) -> None:
    response = await ac.get("/api/sections")
    assert response.is_success


async def test_get_archived_tasks(
    ac: AsyncClient,
    tasks_data: list[dict[str, Any]],
) -> None:
    response = await ac.get("/api/tasks/archived")
    assert response.is_success
    tasks = response.json()
    expected_tasks_n = sum(task["is_archived"] for task in tasks_data)
    assert len(tasks) == expected_tasks_n


async def test_create_section(
    ac: AsyncClient,
    additional_test_data: dict[str, Any],
) -> None:
    section_data = {
        "title": str(additional_test_data["sections"][0]["title"]),
        "parent_id": "0d966845-254b-4b5c-b8a7-8d34dcd3d527",
    }
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
    expected_tasks_n = sum(
        task["section_id"] == id_ for task in tasks_data if not task["is_archived"]
    )
    assert expected_tasks_n == len(response.json()["tasks"])


async def test_get_another_user_section(
    ac_another_user: AsyncClient,
) -> None:
    id_ = "6ff6e896-5da3-46ec-bf66-0a317c5496fa"
    response = await ac_another_user.get(f"/api/section/{id_}")
    assert response.status_code == 403


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
    "section_id,section_to,index,status_code,error_detail",
    [
        (
            "090eda97-dd2d-45bb-baa0-7814313e5a38",
            "36ea0a4f-0334-464d-8066-aa359ecfdcba",
            0,  # move to the beginning
            200,
            None,
        ),
        (
            "090eda97-dd2d-45bb-baa0-7814313e5a38",
            "6ff6e896-5da3-46ec-bf66-0a317c5496fa",
            123,  # move to an incorrect index
            422,
            "The section can't be moved to the specified index",
        ),
        (
            "7e98e010-9d89-4dd2-be8e-773808e1ad85",
            "0d966845-254b-4b5c-b8a7-8d34dcd3d527",  # move inside the root section
            0,
            200,
            None,
        ),
        (
            "0d966845-254b-4b5c-b8a7-8d34dcd3d527",  # move the root section itself
            "7e98e010-9d89-4dd2-be8e-773808e1ad85",
            2,
            422,
            "The root section can't be modified",
        ),
    ],
)
async def test_move_section(
    section_id: str,
    section_to: str,
    index: int,
    status_code: int,
    error_detail: Optional[str],
    ac: AsyncClient,
) -> None:
    response = await ac.post(
        "/api/section/move",
        json={
            "section_id": section_id,
            "to_parent_id": section_to,
            "index": index,
        },
    )
    assert response.status_code == status_code
    if not response.is_success:
        assert response.json()["detail"] == error_detail
        return


async def test_move_another_user_task(
    ac_another_user: AsyncClient,
) -> None:
    task_id = "e6a76c36-7dae-47ee-b657-1a0b02ca40df"
    section_id = "36ea0a4f-0334-464d-8066-aa359ecfdcba"
    index = 0
    response = await ac_another_user.post(
        "/api/task/move",
        json={
            "task_id": task_id,
            "section_to_id": section_id,
            "index": index,
        },
    )
    assert response.status_code == 403


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
        # Task was auto-archived
        with pytest.raises(StopIteration):
            task = next(t for t in data["tasks"] if t["id"] == task_id)
        response = await ac.get("/api/tasks/archived")
        task = next(t for t in response.json() if t["id"] == task_id)
        is_completed = task["is_completed"]
        assert task["is_archived"]
        assert is_completed is expected_is_completed


async def test_mark_completed_another_user_task(
    ac_another_user: AsyncClient,
) -> None:
    task_id = "f4186c04-3f2d-4217-a6ed-5c40bc9946d2"
    response = await ac_another_user.post(
        "/api/task/toggle_completed",
        json={
            "task_id": task_id,
        },
    )
    assert response.status_code == 403


@pytest.mark.parametrize(
    "not_before, not_after, n_tasks_expected, status_code, error_detail",
    [
        (
            "2001-01-01",
            "2002-12-31",
            244,
            200,
            None,
        ),
        (
            "2002-12-31",
            "2001-01-01",
            0,
            422,
            "Incorrect date interval",
        ),
    ],
)
async def test_get_tasks_by_date(
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
    minio_container: None,
) -> None:
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
        post_url = data["post_url"]
        post_fields = data["post_fields"]
        assert isinstance(post_fields, dict)

    if error_detail:
        data = response.json()
        assert data["detail"] == error_detail
        return

    section_id = existing_task_data["section_id"]
    response = await ac.get(f"/api/section/{section_id}")
    task_got = next(t for t in response.json()["tasks"] if t["id"] == task_id)
    assert len(task_got["attachments"]) == 1
    assert task_got["attachments"][0]["aes_key_b64"] == request_data["aes_key_b64"]
    assert task_got["attachments"][0]["aes_iv_b64"] == request_data["aes_iv_b64"]
    assert task_got["attachments"][0]["s3_file_key"]
    attachment_id = task_got["attachments"][0]["id"]
    assert task_got["attachments"][0]["task_id"] == task_id
    get_url = task_got["attachments"][0]["url"]

    # Try to upload image with given URL
    response = httpx.post(
        post_url,
        data={
            **post_fields,
            "Content-Disposition": 'attachment; filename="test_file.txt"',
        },
        files={"file": ("filename", b"some content")},
    )
    assert response.is_success

    # Try to download it
    response = httpx.get(get_url)
    assert response.is_success

    # Remove it
    response = await ac.delete(f"/api/task/{task_id}/attachment/{attachment_id}")
    assert response.is_success

    # Verify that it's removed
    response = httpx.get(get_url)
    assert not response.is_success


async def test_add_attachment_to_another_user_task(
    ac_another_user: AsyncClient,
    tasks_data: list[dict[str, Any]],
) -> None:
    existing_task_data = tasks_data[2]
    task_id = existing_task_data["id"]

    request_data = {
        "task_id": task_id,
        "aes_key_b64": "someBase64EncodedAESKey==",
        "aes_iv_b64": "someBase64EncodedIV==",
    }

    response = await ac_another_user.post("/api/task/attachment", json=request_data)
    assert response.status_code == 403


@pytest.mark.parametrize(
    "task_id, attachment_id, status_code, error_detail",
    [
        (
            "f8b057ea-8c3c-4d14-9b95-ef9acbccffa6",  # random UUID
            "f8b057ea-8c3c-4d14-9b95-ef9acbccffa6",  # random UUID
            404,
            "There is no task with {'task_id': UUID('f8b057ea-8c3c-4d14-9b95-ef9acbccffa6')}",
        ),
        (
            "f4186c04-3f2d-4217-a6ed-5c40bc9946d2",  # real task id
            "f8b057ea-8c3c-4d14-9b95-ef9acbccffa6",  # random UUID
            404,
            "There is no attachment with {'id': UUID('f8b057ea-8c3c-4d14-9b95-ef9acbccffa6')}",
        ),
        (
            "de59bdb5-5f91-48dc-a034-246b8f86be25",  # real task id
            "2bfa26ba-ed8c-4353-adb2-c451957fc3e1",  # real attachment id
            200,
            None,
        ),
    ],
)
async def test_remove_attachment(
    task_id: str,
    attachment_id: str,
    status_code: int,
    error_detail: Optional[str],
    ac: AsyncClient,
    minio_container: None,
) -> None:
    response = await ac.delete(f"/api/task/{task_id}/attachment/{attachment_id}")
    if error_detail:
        assert not response.is_success
        data = response.json()
        assert data["detail"] == error_detail
        return
    assert response.is_success


async def test_remove_attachment_from_another_user_task(
    ac_another_user: AsyncClient,
) -> None:
    task_id = "de59bdb5-5f91-48dc-a034-246b8f86be25"  # real task id
    attachment_id = "2bfa26ba-ed8c-4353-adb2-c451957fc3e1"  # real attachment id

    response = await ac_another_user.delete(
        f"/api/task/{task_id}/attachment/{attachment_id}"
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "query, n_tasks_expected", [("smth_nonexistent", 0), ("saul", 1), ("watch", 2)]
)
async def test_get_tasks_by_search(
    query: str,
    n_tasks_expected: int,
    ac: AsyncClient,
) -> None:
    response = await ac.get("/api/task/search", params={"query": query})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == n_tasks_expected


async def test_root_section_is_created(ac: AsyncClient) -> None:
    # this test ensures that `UserManager.on_after_register` doesn't crash
    user_data = {
        "email": "new_user@example.com",
        "password": "string",
    }
    response = await ac.post("/auth/register", json=user_data)
    assert response.is_success
