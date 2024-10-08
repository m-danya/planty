from typing import Any

import pytest

from planty.domain.task import Section, Task, User
from planty.infrastructure.models import SectionModel, TaskModel, UserModel


@pytest.fixture
def all_users(users_data: list[dict[str, Any]]) -> list[User]:
    return [UserModel(**user).to_entity() for user in users_data]


@pytest.fixture
def all_tasks(tasks_data: list[dict[str, Any]]) -> list[Task]:
    # TODO: get attachments from json too and append it here (as in
    # `all_sections` with tasks)
    return [TaskModel(**task).to_entity(attachments=[]) for task in tasks_data]


@pytest.fixture
def all_sections(
    sections_data: list[dict[str, Any]], all_tasks: list[Task]
) -> list[Section]:
    sections = []
    for section_data in sections_data:
        section = SectionModel(**section_data).to_entity(tasks=[])
        section.tasks = [task for task in all_tasks if task.section_id == section.id]
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
