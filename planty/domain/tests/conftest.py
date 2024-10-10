from typing import Any

import pytest

from planty.domain.task import Attachment, Section, Task, User
from planty.infrastructure.models import (
    AttachmentModel,
    SectionModel,
    TaskModel,
    UserModel,
)


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
