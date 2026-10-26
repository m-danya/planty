from datetime import date
from pathlib import Path
from typing import Any

from httpx import AsyncClient
import pytest
from pytest_mock import MockerFixture
from sqlalchemy import func, select

from planty.application.services.todoist_import import _parse_todoist_date
from planty.application.tests.fixtures.generate_todoist_backup import (
    build_todoist_backup_zip,
)
from planty.infrastructure.database import raw_async_session_maker
from planty.infrastructure.models import SectionModel


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("1 нояб.", date(2026, 11, 1)),
        ("19 нояб", date(2026, 11, 19)),
        ("1 февр 2027", date(2027, 2, 1)),
        ("13 нояб. 2026", date(2026, 11, 13)),
        ("21 февр 2027", date(2027, 2, 21)),
        ("8 нояб", date(2026, 11, 8)),
    ],
)
def test_parse_todoist_date_supports_common_month_abbreviations(
    raw_value: str, expected: date
) -> None:
    due_to, recurrence = _parse_todoist_date(raw_value, date(2026, 10, 25))

    assert due_to == expected
    assert recurrence is None


@pytest.mark.parametrize(
    ("raw_value", "period", "period_type", "flexible_mode"),
    [
        ("каждые 2 недели", 2, "weeks", False),
        ("каждый 2 недели", 2, "weeks", False),
        ("каждый 2 недели 15:00", 2, "weeks", False),
        ("каждый 3 месяца!", 3, "months", True),
        ("каждый год", 1, "years", False),
        ("каждый месяц", 1, "months", False),
        ("каждый! месяц", 1, "months", True),
    ],
)
def test_parse_todoist_date_supports_interval_recurrences(
    raw_value: str, period: int, period_type: str, flexible_mode: bool
) -> None:
    today = date(2026, 10, 25)

    due_to, recurrence = _parse_todoist_date(raw_value, today)

    assert due_to == today
    assert recurrence is not None
    assert recurrence.model_dump() == {
        "period": period,
        "type": period_type,
        "flexible_mode": flexible_mode,
    }


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("каждый 2 янв", date(2027, 1, 2)),
        ("каждый 23 фев", date(2027, 2, 23)),
        ("каждый 1 марта", date(2027, 3, 1)),
        ("каждый 12 апр", date(2027, 4, 12)),
        ("каждое 11 апреля", date(2027, 4, 11)),
        ("каждое 15 мая", date(2027, 5, 15)),
        ("каждый 28 июня", date(2027, 6, 28)),
        ("каждый 16 июля", date(2027, 7, 16)),
        ("каждый 7 окт", date(2027, 10, 7)),
        ("каждый 10 ноя", date(2026, 11, 10)),
        ("каждый 10 дек", date(2026, 12, 10)),
        ("кажд 6 янв", date(2027, 1, 6)),
    ],
)
def test_parse_todoist_date_supports_annual_calendar_dates(
    raw_value: str, expected: date
) -> None:
    due_to, recurrence = _parse_todoist_date(raw_value, date(2026, 10, 25))

    assert due_to == expected
    assert recurrence is not None
    assert recurrence.model_dump() == {
        "period": 1,
        "type": "years",
        "flexible_mode": False,
    }


@pytest.mark.parametrize(
    ("raw_value", "expected", "period"),
    [
        (
            "каждый 15 марта, 15 июня, 15 сентября, 15 декабря",
            date(2026, 12, 15),
            3,
        ),
        ("каждый 10 фев, 10 авг", date(2027, 2, 10), 6),
    ],
)
def test_parse_todoist_date_supports_evenly_spaced_annual_dates(
    raw_value: str, expected: date, period: int
) -> None:
    due_to, recurrence = _parse_todoist_date(raw_value, date(2026, 10, 25))

    assert due_to == expected
    assert recurrence is not None
    assert recurrence.model_dump() == {
        "period": period,
        "type": "months",
        "flexible_mode": False,
    }


def _find_section(tree: list[dict[str, Any]], title: str) -> dict[str, Any]:
    pending = list(tree)
    while pending:
        section = pending.pop()
        if section["title"] == title:
            return section
        pending.extend(section["subsections"])
    raise AssertionError(f"Section {title!r} was not imported")


async def _upload(ac: AsyncClient, archive_path: Path, *, erase_existing: bool) -> Any:
    with archive_path.open("rb") as archive:
        return await ac.post(
            "/api/import/todoist",
            files={"file": (archive_path.name, archive, "application/zip")},
            data={"erase_existing": str(erase_existing).lower()},
        )


async def test_import_todoist_backup_replaces_current_user_data(
    ac: AsyncClient,
    tmp_path: Path,
    mocker: MockerFixture,
    test_data: dict[str, list[dict[str, Any]]],
) -> None:
    mocker.patch(
        "planty.application.services.todoist_import.get_today",
        return_value=date(2026, 10, 25),
    )
    archive_path = build_todoist_backup_zip(tmp_path / "todoist.zip")
    other_user_id = test_data["users"][1]["id"]
    async with raw_async_session_maker() as session:
        other_sections_before = await session.scalar(
            select(func.count())
            .select_from(SectionModel)
            .where(SectionModel.user_id == other_user_id)
        )

    response = await _upload(ac, archive_path, erase_existing=True)

    assert response.status_code == 200
    assert response.json() == {"projects": 4, "sections": 6, "tasks": 23}
    tree_response = await ac.get("/api/sections")
    tree = tree_response.json()
    root = next(section for section in tree if section["parent_id"] is None)
    assert [section["title"] for section in root["subsections"]] == [
        "Inbox",
        "🌴 Тестовый проект",
        "Календарь",
        "Пустой проект",
    ]

    inbox = _find_section(tree, "Inbox")
    inbox_response = await ac.get(f"/api/section/{inbox['id']}")
    inbox_tasks = inbox_response.json()["tasks"]
    assert len(inbox_tasks) == 11
    assert (
        next(
            task for task in inbox_tasks if task["title"] == "Подзадача тестового плана"
        )["parent_task_id"]
        == next(
            task
            for task in inbox_tasks
            if task["title"] == "Тестовая задача с низким приоритетом"
        )["id"]
    )
    assert (
        next(
            task for task in inbox_tasks if task["title"] == "Тестовая задача с датой"
        )["due_to"]
        == "2026-11-15"
    )

    calendar = _find_section(tree, "Календарь")
    calendar_response = await ac.get(f"/api/section/{calendar['id']}")
    calendar_tasks = calendar_response.json()["tasks"]
    daily = next(
        task
        for task in calendar_tasks
        if task["title"] == "Каждый день: тестовая привычка"
    )
    assert daily["due_to"] == "2026-10-25"
    assert daily["recurrence"] == {
        "period": 1,
        "type": "days",
        "flexible_mode": True,
    }

    async with raw_async_session_maker() as session:
        other_sections_after = await session.scalar(
            select(func.count())
            .select_from(SectionModel)
            .where(SectionModel.user_id == other_user_id)
        )
    assert other_sections_after == other_sections_before


async def test_import_todoist_backup_can_append_to_existing_data(
    ac: AsyncClient, tmp_path: Path
) -> None:
    before_response = await ac.get("/api/sections")
    before_root = next(
        section for section in before_response.json() if section["parent_id"] is None
    )
    original_titles = [section["title"] for section in before_root["subsections"]]
    archive_path = build_todoist_backup_zip(tmp_path / "todoist.zip")

    response = await _upload(ac, archive_path, erase_existing=False)

    assert response.status_code == 200
    after_response = await ac.get("/api/sections")
    after_root = next(
        section for section in after_response.json() if section["parent_id"] is None
    )
    after_titles = [section["title"] for section in after_root["subsections"]]
    assert after_titles[: len(original_titles)] == original_titles
    assert after_titles[-4:] == [
        "Inbox",
        "🌴 Тестовый проект",
        "Календарь",
        "Пустой проект",
    ]


async def test_invalid_todoist_backup_does_not_erase_data(
    ac: AsyncClient,
) -> None:
    before_response = (await ac.get("/api/sections")).json()
    before = {
        (section["id"], section["title"])
        for section in _flatten_sections(before_response)
    }

    response = await ac.post(
        "/api/import/todoist",
        files={"file": ("broken.zip", b"not a zip", "application/zip")},
        data={"erase_existing": "true"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid Todoist backup"
    after_response = (await ac.get("/api/sections")).json()
    after = {
        (section["id"], section["title"])
        for section in _flatten_sections(after_response)
    }
    assert after == before


def _flatten_sections(tree: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        section
        for item in tree
        for section in [item, *_flatten_sections(item["subsections"])]
    ]
