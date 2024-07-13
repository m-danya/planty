import pytest

from planty.application.services import SectionService, TaskService
from planty.infrastructure.repositories import (
    FakeSectionRepository,
    FakeTaskRepository,
    FakeUserRepository,
    ISectionRepository,
    ITaskRepository,
    IUserRepository,
)


@pytest.fixture
def task_repo() -> ITaskRepository:
    return FakeTaskRepository()


@pytest.fixture
def section_repo(task_repo: ITaskRepository) -> ISectionRepository:
    return FakeSectionRepository(task_repo)


@pytest.fixture
def user_repo() -> IUserRepository:
    return FakeUserRepository()


@pytest.fixture
def task_service(task_repo: ITaskRepository, user_repo: IUserRepository) -> TaskService:
    return TaskService(task_repo, user_repo)


@pytest.fixture
def section_service(
    section_repo: ISectionRepository,
    task_repo: ITaskRepository,
) -> SectionService:
    return SectionService(section_repo, task_repo)
