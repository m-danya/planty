from typing import Any

from httpx import AsyncClient


SECTION_ID = "febd1d82-b872-4b67-a15b-961b9aa24ed6"


async def _create_task(
    ac: AsyncClient, title: str, parent_task_id: str | None = None
) -> str:
    response = await ac.post(
        "/api/task",
        json={
            "section_id": SECTION_ID,
            "parent_task_id": parent_task_id,
            "title": title,
        },
    )
    assert response.is_success
    return str(response.json()["id"])


async def _section_tasks(ac: AsyncClient) -> dict[str, dict[str, Any]]:
    response = await ac.get(f"/api/section/{SECTION_ID}")
    assert response.is_success
    return {task["id"]: task for task in response.json()["tasks"]}


async def _archived_tasks(ac: AsyncClient) -> dict[str, dict[str, Any]]:
    response = await ac.get("/api/tasks/archived")
    assert response.is_success
    return {task["id"]: task for task in response.json()["tasks"]}


async def test_manual_archive_archives_the_entire_subtask_tree(
    ac: AsyncClient,
) -> None:
    root_id = await _create_task(ac, "Root")
    first_child_id = await _create_task(ac, "First child", root_id)
    grandchild_id = await _create_task(ac, "Grandchild", first_child_id)
    second_child_id = await _create_task(ac, "Second child", root_id)
    unrelated_id = await _create_task(ac, "Unrelated")

    response = await ac.post(
        "/api/task/toggle_completed",
        json={"task_id": grandchild_id, "auto_archive": False},
    )
    assert response.is_success

    response = await ac.post("/api/task/toggle_archived", json={"task_id": root_id})
    assert response.is_success

    active = await _section_tasks(ac)
    archived = await _archived_tasks(ac)
    subtree_ids = {root_id, first_child_id, grandchild_id, second_child_id}

    assert subtree_ids.isdisjoint(active)
    assert unrelated_id in active
    assert subtree_ids <= archived.keys()
    assert all(archived[task_id]["is_archived"] for task_id in subtree_ids)
    assert archived[root_id]["is_completed"] is False
    assert archived[first_child_id]["is_completed"] is False
    assert archived[grandchild_id]["is_completed"] is True
    assert archived[second_child_id]["is_completed"] is False
    assert archived[first_child_id]["parent_task_id"] == root_id
    assert archived[grandchild_id]["parent_task_id"] == first_child_id
    assert archived[second_child_id]["parent_task_id"] == root_id


async def test_auto_archive_archives_descendants_without_completing_them(
    ac: AsyncClient,
) -> None:
    root_id = await _create_task(ac, "Root")
    child_id = await _create_task(ac, "Child", root_id)
    grandchild_id = await _create_task(ac, "Grandchild", child_id)

    response = await ac.post(
        "/api/task/toggle_completed",
        json={"task_id": root_id, "auto_archive": True},
    )
    assert response.is_success

    active = await _section_tasks(ac)
    archived = await _archived_tasks(ac)
    subtree_ids = {root_id, child_id, grandchild_id}

    assert subtree_ids.isdisjoint(active)
    assert subtree_ids <= archived.keys()
    assert archived[root_id]["is_completed"] is True
    assert archived[child_id]["is_completed"] is False
    assert archived[grandchild_id]["is_completed"] is False
    assert archived[child_id]["parent_task_id"] == root_id
    assert archived[grandchild_id]["parent_task_id"] == child_id


async def test_completing_without_auto_archive_keeps_descendants_active(
    ac: AsyncClient,
) -> None:
    root_id = await _create_task(ac, "Root")
    child_id = await _create_task(ac, "Child", root_id)
    grandchild_id = await _create_task(ac, "Grandchild", child_id)

    response = await ac.post(
        "/api/task/toggle_completed",
        json={"task_id": root_id, "auto_archive": False},
    )
    assert response.is_success

    active = await _section_tasks(ac)
    archived = await _archived_tasks(ac)
    subtree_ids = {root_id, child_id, grandchild_id}

    assert subtree_ids <= active.keys()
    assert subtree_ids.isdisjoint(archived)
    assert active[root_id]["is_completed"] is True
    assert active[child_id]["is_completed"] is False
    assert active[grandchild_id]["is_completed"] is False


async def test_completing_subtask_does_not_auto_archive_it(
    ac: AsyncClient,
) -> None:
    root_id = await _create_task(ac, "Root")
    child_id = await _create_task(ac, "Child", root_id)
    grandchild_id = await _create_task(ac, "Grandchild", child_id)

    response = await ac.post(
        "/api/task/toggle_completed",
        json={"task_id": child_id, "auto_archive": True},
    )
    assert response.is_success

    active = await _section_tasks(ac)
    archived = await _archived_tasks(ac)
    subtree_ids = {root_id, child_id, grandchild_id}

    assert subtree_ids <= active.keys()
    assert subtree_ids.isdisjoint(archived)
    assert active[root_id]["is_completed"] is False
    assert active[child_id]["is_completed"] is True
    assert active[grandchild_id]["is_completed"] is False


async def test_archiving_subtask_only_archives_its_own_branch(
    ac: AsyncClient,
) -> None:
    root_id = await _create_task(ac, "Root")
    archived_child_id = await _create_task(ac, "Archived child", root_id)
    archived_grandchild_id = await _create_task(
        ac, "Archived grandchild", archived_child_id
    )
    active_child_id = await _create_task(ac, "Active child", root_id)
    active_grandchild_id = await _create_task(ac, "Active grandchild", active_child_id)

    response = await ac.post(
        "/api/task/toggle_archived", json={"task_id": archived_child_id}
    )
    assert response.is_success

    active = await _section_tasks(ac)
    archived = await _archived_tasks(ac)

    assert {root_id, active_child_id, active_grandchild_id} <= active.keys()
    assert {archived_child_id, archived_grandchild_id} <= archived.keys()
    assert root_id not in archived
    assert active_child_id not in archived
    assert active_grandchild_id not in archived

    response = await ac.post(
        "/api/task/toggle_archived", json={"task_id": archived_child_id}
    )
    assert response.is_success

    active = await _section_tasks(ac)
    archived = await _archived_tasks(ac)

    assert {
        root_id,
        archived_child_id,
        archived_grandchild_id,
        active_child_id,
        active_grandchild_id,
    } <= active.keys()
    assert archived_child_id not in archived
    assert archived_grandchild_id not in archived


async def test_archive_walks_through_an_already_archived_descendant(
    ac: AsyncClient,
) -> None:
    root_id = await _create_task(ac, "Root")
    child_id = await _create_task(ac, "Child", root_id)

    response = await ac.post("/api/task/toggle_archived", json={"task_id": child_id})
    assert response.is_success

    grandchild_id = await _create_task(ac, "Late grandchild", child_id)
    response = await ac.post("/api/task/toggle_archived", json={"task_id": root_id})
    assert response.is_success

    active = await _section_tasks(ac)
    archived = await _archived_tasks(ac)

    assert {root_id, child_id, grandchild_id}.isdisjoint(active)
    assert {root_id, child_id, grandchild_id} <= archived.keys()
    assert archived[grandchild_id]["parent_task_id"] == child_id


async def test_manual_unarchive_unarchives_the_entire_subtask_tree(
    ac: AsyncClient,
) -> None:
    root_id = await _create_task(ac, "Root")
    child_id = await _create_task(ac, "Child", root_id)
    grandchild_id = await _create_task(ac, "Grandchild", child_id)

    response = await ac.post(
        "/api/task/toggle_completed",
        json={"task_id": child_id, "auto_archive": True},
    )
    assert response.is_success
    response = await ac.post("/api/task/toggle_archived", json={"task_id": root_id})
    assert response.is_success
    response = await ac.post("/api/task/toggle_archived", json={"task_id": root_id})
    assert response.is_success

    active = await _section_tasks(ac)
    archived = await _archived_tasks(ac)
    subtree_ids = {root_id, child_id, grandchild_id}

    assert subtree_ids <= active.keys()
    assert subtree_ids.isdisjoint(archived)
    assert active[root_id]["is_completed"] is False
    assert active[child_id]["is_completed"] is True
    assert active[grandchild_id]["is_completed"] is False


async def test_uncompleting_auto_archived_parent_unarchives_descendants(
    ac: AsyncClient,
) -> None:
    root_id = await _create_task(ac, "Root")
    child_id = await _create_task(ac, "Child", root_id)
    grandchild_id = await _create_task(ac, "Grandchild", child_id)

    response = await ac.post(
        "/api/task/toggle_completed",
        json={"task_id": root_id, "auto_archive": True},
    )
    assert response.is_success
    response = await ac.post(
        "/api/task/toggle_completed",
        json={"task_id": root_id, "auto_archive": True},
    )
    assert response.is_success

    active = await _section_tasks(ac)
    archived = await _archived_tasks(ac)
    subtree_ids = {root_id, child_id, grandchild_id}

    assert subtree_ids <= active.keys()
    assert subtree_ids.isdisjoint(archived)
    assert active[root_id]["is_completed"] is False
    assert active[child_id]["is_completed"] is False
    assert active[grandchild_id]["is_completed"] is False
