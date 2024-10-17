import os
import json
import pytest
from datetime import datetime
from pathlib import Path
from typing import Any


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


@pytest.fixture
def all_users(users_data: list[dict[str, Any]]) -> list[User]:
    return [UserModel(**user).to_entity() for user in users_data]


@pytest.fixture
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


@pytest.fixture
def nonperiodic_task(all_tasks: list[Task]) -> Task:
    return all_tasks[2]


@pytest.fixture
def everyday_task(all_tasks: list[Task]) -> Task:
    return all_tasks[0]


@pytest.fixture
def flexible_recurrence_task(all_tasks: list[Task]) -> Task:
    return all_tasks[3]


@pytest.fixture
def task_from_2001(all_tasks: list[Task]) -> Task:
    return all_tasks[8]


@pytest.fixture
def task_with_due_to_and_no_recurrence(all_tasks: list[Task]) -> Task:
    return all_tasks[9]


@pytest.fixture
def nonempty_section(all_sections: list[Section]) -> Section:
    return all_sections[2]


@pytest.fixture
def another_nonempty_section(all_sections: list[Section]) -> Section:
    return all_sections[0]


@pytest.fixture
def test_user(all_users: list[User]) -> User:
    return all_users[0]
