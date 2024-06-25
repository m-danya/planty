import pytest

from planty.application.schemas import TaskCreateRequest
from planty.application.services import TaskService
from planty.domain.entities import Section, Task, User
from planty.infrastructure.repositories import (
    FakeTaskRepository,
    FakeUserRepository,
    ITaskRepository,
    IUserRepository,
)


@pytest.fixture
def task_repo() -> ITaskRepository:
    return FakeTaskRepository()


@pytest.fixture
def user_repo() -> IUserRepository:
    return FakeUserRepository()


@pytest.fixture
def task_service(task_repo: ITaskRepository, user_repo: IUserRepository) -> TaskService:
    return TaskService(task_repo, user_repo)


async def test_add_task(
    task_service: TaskService,
    nonperiodic_task: Task,
    user: User,
    section: Section,
    user_repo: IUserRepository,
) -> None:
    task = nonperiodic_task

    await user_repo.add(user)

    task_create_request = TaskCreateRequest(
        user_id=user.id,
        section_id=section.id,
        title=task.title,
        description=task.description,
        due_to_next=task.due_to_next,
        due_to_days_period=task.due_to_days_period,
    )

    await task_service.add_task(task_create_request)
    # TODO: test that task is actually in task_repo
