from datetime import date
from typing import Any, Optional
import httpx
import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture


# TODO: test task creation with `recurrence`
@pytest.mark.parametrize(
    "section_id, status_code, error_detail",
    [
        ("febd1d82-b872-4b67-a15b-961b9aa24ed6", 201, None),
        (
            "6ff6e896-5da3-46ec-bf66-0a317c5496fa",
            422,
            "Section can't have both tasks and subsections",
        ),
    ],
)
async def test_create_task(
    section_id: str,
    status_code: int,
    error_detail: Optional[str],
    ac: AsyncClient,
    additional_test_data: dict[str, Any],
) -> None:
    task_data = {
        "section_id": section_id,
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
    tasks = response.json()["tasks"]
    expected_tasks_n = sum(task["is_archived"] for task in tasks_data)
    assert len(tasks) == expected_tasks_n


@pytest.mark.parametrize(
    "parent_id, status_code, error_detail",
    [
        ("0d966845-254b-4b5c-b8a7-8d34dcd3d527", 201, None),
        ("45561eb6-3570-44de-af8a-54212e2981e6", 201, None),
        (
            "090eda97-dd2d-45bb-baa0-7814313e5a38",
            422,
            "Section can't have both tasks and subsections",
        ),
    ],
)
async def test_create_section(
    parent_id: str,
    status_code: int,
    error_detail: Optional[str],
    ac: AsyncClient,
    additional_test_data: dict[str, Any],
) -> None:
    # Do it twice to check that the `has_subsections` flag is updated correctly
    # (there is no other way to check it using endpoints)
    for _ in range(2):
        section_data = {
            "title": str(additional_test_data["sections"][0]["title"]),
            "parent_id": parent_id,
        }
        response = await ac.post("/api/section", json=section_data)
        assert response.status_code == status_code
        if not response.is_success:
            assert response.json()["detail"] == error_detail
            return

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
            "b9547aee-cba5-418e-b450-7914e44c9231",
            0,  # move to the beginning of empty section
            200,
            None,
        ),
        (
            "e6a76c36-7dae-47ee-b657-1a0b02ca40df",
            "36ea0a4f-0334-464d-8066-aa359ecfdcba",
            0,
            422,
            "Section can't have both tasks and subsections",
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
    "section_id,section_to,index,parent_id_before_move,status_code,error_detail",
    [
        (
            "090eda97-dd2d-45bb-baa0-7814313e5a38",
            "36ea0a4f-0334-464d-8066-aa359ecfdcba",
            0,  # move to the beginning
            "6ff6e896-5da3-46ec-bf66-0a317c5496fa",
            200,
            None,
        ),
        (
            "090eda97-dd2d-45bb-baa0-7814313e5a38",
            "6ff6e896-5da3-46ec-bf66-0a317c5496fa",
            123,  # move to an incorrect index
            "6ff6e896-5da3-46ec-bf66-0a317c5496fa",
            422,
            "The section can't be placed at the specified index",
        ),
        (
            "7e98e010-9d89-4dd2-be8e-773808e1ad85",
            "0d966845-254b-4b5c-b8a7-8d34dcd3d527",  # move inside the root section
            0,
            "0d966845-254b-4b5c-b8a7-8d34dcd3d527",
            200,
            None,
        ),
        (
            "0d966845-254b-4b5c-b8a7-8d34dcd3d527",  # move the root section itself
            "7e98e010-9d89-4dd2-be8e-773808e1ad85",
            2,
            None,
            422,
            "The root section can't be modified",
        ),
        (
            # This test on incorrect code (with `with_direct_subsections=False`
            # in `SectionService.move_section`) could trigger 500 error in
            # validator `check_flags`, but it doesn't, even with
            # revalidate_instances='always' in both Schema and Entity classes
            "6754b40e-aa0d-4b0d-9dba-4d15c751b270",
            "5fa09005-4ba9-417b-a9cb-82f182cd1f26",
            0,
            "36ea0a4f-0334-464d-8066-aa359ecfdcba",
            200,
            None,
        ),
        (
            "36ea0a4f-0334-464d-8066-aa359ecfdcba",
            "5fa09005-4ba9-417b-a9cb-82f182cd1f26",
            0,
            "0d966845-254b-4b5c-b8a7-8d34dcd3d527",
            422,  # MisplaceSectionHierarchyError
            "The section can't be placed as a subsection of its own subsection",
        ),
        (
            "36ea0a4f-0334-464d-8066-aa359ecfdcba",
            "36ea0a4f-0334-464d-8066-aa359ecfdcba",
            0,
            "0d966845-254b-4b5c-b8a7-8d34dcd3d527",
            422,  # MisplaceSectionHierarchyError
            "The section can't be placed as a subsection of its own subsection",
        ),
    ],
)
async def test_move_section(
    section_id: str,
    section_to: str,
    index: int,
    parent_id_before_move: Optional[str],
    status_code: int,
    error_detail: Optional[str],
    ac: AsyncClient,
) -> None:
    # just an assertion
    response = await ac.get(f"/api/section/{section_id}")
    assert response.json()["parent_id"] == parent_id_before_move
    # the main test
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

    # check for possible 500 errors (with incorrectly updated flags)
    response = await ac.get("/api/sections")
    print(response.json())
    assert response.is_success
    for section_id_to_check in (section_id, section_to, parent_id_before_move):
        if section_id_to_check:
            response = await ac.get(f"/api/section/{section_id_to_check}")
            assert response.is_success


async def test_update_section(
    ac: AsyncClient,
) -> None:
    section_id = "090eda97-dd2d-45bb-baa0-7814313e5a38"
    new_title = "new title"
    update_data = {"id": section_id, "title": new_title}
    response = await ac.patch(
        "/api/section",
        json=update_data,
    )
    assert response.status_code == 200
    response = await ac.get(f"/api/section/{section_id}")
    assert response.json()["title"] == new_title


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
async def test_toggle_completed_nonperiodical_task(
    task_id: str,
    ac: AsyncClient,
) -> None:
    # TODO: exand this test to sequential requests when logics is established
    for expected_is_completed in [True]:
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
        task, _ = await _request_task_data(task_id, ac, from_archived=True)
        is_completed = task["is_completed"]
        assert task["is_archived"]
        assert is_completed is expected_is_completed


@pytest.mark.parametrize(
    "task_id, section_id, due_to, new_due_to",
    [
        (
            # Recurrence is "every day, non-flexible mode"
            "f15c4c32-3d85-4a64-a216-75bdf6f2d8c5",
            "a5b2010d-c27c-4f22-be47-828e065f9607",
            "2024-12-21",
            "2024-12-22",
        ),
        (
            # Recurrence is "every 3 days, non-flexible mode"
            "fe03f915-a5d8-4b4a-9ee6-93dacb2bf08e",
            "a5b2010d-c27c-4f22-be47-828e065f9607",
            "2001-01-01",
            "2001-01-04",
        ),
        (
            # Recurrence is "every 3 months, non-flexible mode"
            "effd5cea-038c-43d2-9363-d0aa15ce9e77",
            "a5b2010d-c27c-4f22-be47-828e065f9607",
            "2010-01-01",
            "2010-04-01",
        ),
    ],
)
async def test_toggle_completed_periodical_task(
    ac: AsyncClient,
    task_id: str,
    section_id: str,
    due_to: str,
    new_due_to: str,
) -> None:
    task, _ = await _request_task_data(task_id, ac, section_id)
    assert task["due_to"] == due_to

    await ac.post(
        "/api/task/toggle_completed",
        json={
            "task_id": task_id,
        },
    )
    task, _ = await _request_task_data(task_id, ac, section_id)
    assert task["is_completed"] is False
    assert task["is_archived"] is False
    assert task["due_to"] == new_due_to


async def test_unarchiving_ask_puts_it_to_the_section_end(
    tasks_data: list[dict[str, Any]],
    ac: AsyncClient,
) -> None:
    task_id = "e6a76c36-7dae-47ee-b657-1a0b02ca40df"
    section_id = "090eda97-dd2d-45bb-baa0-7814313e5a38"
    task_got, task_index = await _request_task_data(
        task_id, ac, section_id, from_archived=True
    )

    # task will be unarchived and will be put to the section end
    response = await ac.post(
        "/api/task/toggle_completed",
        json={
            "task_id": task_id,
        },
    )
    section_len = len(response.json()["tasks"])
    assert section_len > 3

    task_got, task_index = await _request_task_data(
        task_id, ac, section_id, from_archived=False
    )
    assert task_index == section_len - 1


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
    "not_before, not_after, n_tasks_expected, n_overdue_tasks_expected, status_code, error_detail",
    [
        (
            "2001-01-01",
            "2002-12-31",
            1,
            0,
            200,
            None,
        ),
        (
            "2001-02-01",
            "2002-12-31",
            0,
            1,
            200,
            None,
        ),
        (
            "2002-12-31",
            "2001-01-01",
            0,
            0,
            422,
            "Incorrect date interval",
        ),
        (
            "2002-12-31",
            "2025-01-01",
            11,  # 11 tasks to do in this range
            1,  # 1 overdue task before 2002-12-31
            200,
            None,
        ),
    ],
)
async def test_get_tasks_by_date(
    not_before: str,
    not_after: str,
    n_tasks_expected: int,
    n_overdue_tasks_expected: int,
    status_code: int,
    error_detail: Optional[str],
    ac: AsyncClient,
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        "planty.domain.calendar.get_today", return_value=date.fromisoformat(not_before)
    )
    mocker.patch(
        "planty.infrastructure.repositories.get_today",
        return_value=date.fromisoformat(not_before),
    )

    response = await ac.get(
        "/api/task/by_date",
        params={
            "not_before": not_before,
            "not_after": not_after,
            "with_overdue": True,
        },
    )
    assert response.status_code == status_code
    if not response.is_success:
        assert response.json()["detail"] == error_detail
        return
    tasks_by_dates = response.json()["by_dates"]
    overdue_tasks = response.json()["overdue"]

    n_tasks = sum(len(tasks_by_date["tasks"]) for tasks_by_date in tasks_by_dates)
    assert n_tasks == n_tasks_expected
    assert len(overdue_tasks) == n_overdue_tasks_expected


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
    task_got, _ = await _request_task_data(task_id, ac, section_id)
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


async def _request_task_data(
    task_id: str,
    ac: AsyncClient,
    section_id: Optional[str] = None,
    from_archived: bool = False,
) -> tuple[dict[str, Any], int]:
    if from_archived:
        response = await ac.get("/api/tasks/archived")
    else:
        response = await ac.get(f"/api/section/{section_id}")
    task_got, index = next(
        (t, i) for i, t in enumerate(response.json()["tasks"]) if t["id"] == task_id
    )
    return task_got, index


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
    response = await ac.post("/api/auth/register", json=user_data)
    assert response.is_success
