import os
import json
from uuid import UUID
import pytest
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol, TypeVar


# substitute the `PLANTY_MODE` _before_ the Settings object is created.
os.environ["PLANTY_MODE"] = "TEST"

from planty.domain.task import Attachment, Section, Task, User  # noqa: E402
from planty.infrastructure.models import (  # noqa: E402
    AttachmentModel,
    SectionModel,
    TaskModel,
    UserModel,
)

# These fixtures are shared across different test sets:


# supports datetimes copied from dbeaver
TEST_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


@pytest.fixture(scope="session")
def test_data() -> dict[str, list[dict[str, Any]]]:
    return _load_json_with_data("data.json")


@pytest.fixture(scope="session")
def additional_test_data() -> dict[str, Any]:
    return _load_json_with_data("additional_data.json")


def _load_json_with_data(filename: str) -> dict[str, Any]:
    with open(Path(__file__).parent / "resources" / filename) as f:
        test_data: dict[str, Any] = json.load(f)
    for table_key in test_data:
        last_idx: int = 0
        for row in test_data[table_key]:
            for column in row:
                if row[column] is None:
                    continue
                if column.endswith("_at"):
                    row[column] = datetime.strptime(row[column], TEST_DATETIME_FORMAT)
                if column == "due_to" and row[column]:
                    row[column] = datetime.strptime(row[column], "%Y-%m-%d").date()
                if column == "index":
                    # Prevent forgetting to change index in json
                    idx = row[column]
                    assert (
                        idx == last_idx + 1 or idx == 0
                    ), f"Unexpected index in entity with id {row['id']}"
                    last_idx = idx

    # TODO: make this dict immutable to prevent accidental modification
    return test_data


@pytest.fixture(scope="session")
def users_data(
    test_data: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    return test_data["users"]


@pytest.fixture(scope="session")
def tasks_data(
    test_data: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    return test_data["tasks"]


@pytest.fixture(scope="session")
def sections_data(
    test_data: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    return test_data["sections"]


@pytest.fixture(scope="session")
def attachments_data(
    test_data: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    return test_data["attachments"]


@pytest.fixture(scope="session")
def all_users(users_data: list[dict[str, Any]]) -> list[User]:
    return [UserModel(**user).to_entity() for user in users_data]


@pytest.fixture(scope="session")
def all_attachments(attachments_data: list[dict[str, Any]]) -> list[Attachment]:
    return [
        AttachmentModel(**attachment).to_entity() for attachment in attachments_data
    ]


@pytest.fixture
def all_tasks(
    tasks_data: list[dict[str, Any]], all_attachments: list[Attachment]
) -> list[Task]:
    tasks = []
    for task_data in tasks_data:
        task = TaskModel(**task_data).to_entity(
            attachments=[
                a for a in all_attachments if str(a.task_id) == task_data["id"]
            ]
        )
        tasks.append(task)
    return tasks


@pytest.fixture
def all_sections(
    sections_data: list[dict[str, Any]], all_tasks: list[Task]
) -> list[Section]:
    sections = []
    for section_data in sections_data:
        section = SectionModel(**section_data).to_entity(
            tasks=[
                task for task in all_tasks if str(task.section_id) == section_data["id"]
            ]
        )
        sections.append(section)
    return sections


class HasId(Protocol):
    id: UUID


T = TypeVar("T", bound=HasId)


def _find_by_id(all_entities: list[T], id_: UUID) -> T:
    return next(entity for entity in all_entities if entity.id == id_)


@pytest.fixture
def nonperiodic_task(all_tasks: list[Task]) -> Task:
    return _find_by_id(all_tasks, UUID("f4186c04-3f2d-4217-a6ed-5c40bc9946d2"))


@pytest.fixture
def everyday_task(all_tasks: list[Task]) -> Task:
    return _find_by_id(all_tasks, UUID("0c6865ac-6bba-4837-8d48-6a057d4b12bf"))


@pytest.fixture
def flexible_recurrence_task(all_tasks: list[Task]) -> Task:
    return _find_by_id(all_tasks, UUID("7874f13d-ef4b-4fbd-87a8-db6bbf407976"))


@pytest.fixture
def task_from_2001(all_tasks: list[Task]) -> Task:
    return _find_by_id(all_tasks, UUID("fe03f915-a5d8-4b4a-9ee6-93dacb2bf08e"))


@pytest.fixture
def task_with_due_to_and_no_recurrence(all_tasks: list[Task]) -> Task:
    return _find_by_id(all_tasks, UUID("2c5f3244-ec03-4ddd-b78c-cc4ab5db4d42"))


@pytest.fixture
def nonempty_section(all_sections: list[Section]) -> Section:
    return _find_by_id(all_sections, UUID("a5b2010d-c27c-4f22-be47-828e065f9607"))


@pytest.fixture
def another_nonempty_section(all_sections: list[Section]) -> Section:
    return _find_by_id(all_sections, UUID("6ff6e896-5da3-46ec-bf66-0a317c5496fa"))


@pytest.fixture(scope="session")
def test_user(all_users: list[User]) -> User:
    # WARNING: do not modify this object
    return _find_by_id(all_users, UUID("38df4136-36b2-4171-8459-27f411af8323"))


@pytest.fixture(scope="session")
def another_test_user(all_users: list[User]) -> User:
    # WARNING: do not modify this object
    return _find_by_id(all_users, UUID("73ca2340-76bd-4abe-b872-7e82a9528c45"))
