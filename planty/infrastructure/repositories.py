from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from planty.domain.entities import Section, Task, User, Username
from planty.infrastructure.models import SectionModel, TaskModel


class IUserRepository(ABC):
    @abstractmethod
    async def add(self, user: User) -> None: ...
    @abstractmethod
    async def get(self, user_id: UUID) -> Optional[User]: ...


class FakeUserRepository(IUserRepository):
    def __init__(self) -> None:
        self._users: list[User] = []

    async def add(self, user: User) -> None:
        self._users.append(user)

    async def get(self, user_id: UUID) -> Optional[User]:
        for user in self._users:
            if user.id == user_id:
                return user
        return None


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def add(self, user: User) -> None: ...
    async def get(self, user_id: UUID) -> Optional[User]:
        return User(username=Username("test_user"))


class ITaskRepository(ABC):
    @abstractmethod
    async def add(self, task: Task) -> None: ...
    @abstractmethod
    async def get(self, task_id: UUID) -> Optional[Task]: ...
    @abstractmethod
    async def update(self, task: Task) -> None: ...
    @abstractmethod
    async def get_tasks_by_section_id(self, section_id: UUID) -> list[Task]: ...


class FakeTaskRepository(ITaskRepository):
    def __init__(self) -> None:
        self._tasks: list[Task] = []

    async def add(self, task: Task) -> None:
        self._tasks.append(task)

    async def get(self, task_id: UUID) -> Optional[Task]:
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    async def update(self, task: Task) -> None:
        for i, some_task in enumerate(self._tasks):
            if some_task.id == task.id:
                self._tasks[i] = task
                return
        raise ValueError(f"Task with id {task.id} not found")

    async def get_tasks_by_section_id(self, section_id: UUID) -> list[Task]:
        return [task for task in self._tasks if task.section_id == section_id]


class SQLAlchemyTaskRepository(ITaskRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def add(self, task: Task) -> None:
        task_model = TaskModel.from_entity(task)
        self._db_session.add(task_model)

    async def get(self, task_id: UUID) -> Optional[Task]:
        result = await self._db_session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        task_model: Optional[TaskModel] = result.scalar_one_or_none()
        if task_model is None:
            return None

        return Task(
            id=task_model.id,
            user_id=task_model.user_id,
            section_id=task_model.section_id,
            title=task_model.title,
            description=task_model.description,
            is_completed=task_model.is_completed,
            added_at=task_model.added_at,
            due_to_next=task_model.due_to_next,
            due_to_days_period=task_model.due_to_days_period,
        )

    async def update(self, task: Task) -> None:
        result = await self._db_session.execute(
            select(TaskModel).where(TaskModel.id == task.id)
        )
        task_model: Optional[TaskModel] = result.scalar_one_or_none()
        if task_model is None:
            raise ValueError(f"Task with id {task.id} not found")

        task_model.user_id = task.user_id
        task_model.section_id = task.section_id
        task_model.title = task.title
        task_model.description = task.description
        task_model.is_completed = task.is_completed
        task_model.added_at = task.added_at
        task_model.due_to_next = task.due_to_next
        task_model.due_to_days_period = task.due_to_days_period

        self._db_session.add(task_model)

    async def get_tasks_by_section_id(self, section_id: UUID) -> list[Task]:
        result = await self._db_session.execute(
            select(TaskModel).where(TaskModel.section_id == section_id)
        )
        task_models = result.scalars().all()
        return [
            Task(
                id=task_model.id,
                user_id=task_model.user_id,
                section_id=task_model.section_id,
                title=task_model.title,
                description=task_model.description,
                is_completed=task_model.is_completed,
                added_at=task_model.added_at,
                due_to_next=task_model.due_to_next,
                due_to_days_period=task_model.due_to_days_period,
            )
            for task_model in task_models
        ]


class ISectionRepository(ABC):
    @abstractmethod
    async def add(self, section: Section) -> None: ...
    @abstractmethod
    async def get(self, section_id: UUID) -> Optional[Section]: ...
    @abstractmethod
    async def update(self, section: Section) -> None: ...


class FakeSectionRepository(ISectionRepository):
    def __init__(self, task_repo: ITaskRepository) -> None:
        self._sections: list[Section] = []
        self._task_repo = task_repo

    async def add(self, section: Section) -> None:
        self._sections.append(section)

    async def get(self, section_id: UUID) -> Optional[Section]:
        for section in self._sections:
            if section.id == section_id:
                tasks = await self._task_repo.get_tasks_by_section_id(section_id)
                section.tasks = tasks
                return section
        return None

    async def update(self, section: Section) -> None:
        for i, some_section in enumerate(self._sections):
            if some_section.id == section.id:
                self._sections[i] = section
                return
        raise ValueError(f"Section with id {section.id} not found")


# TODO: TEST ACTUAL SQL REPOSITORIES
class SQLAlchemySectionRepository(ISectionRepository):
    def __init__(self, db_session: AsyncSession, task_repo: ITaskRepository):
        self._db_session = db_session
        self._task_repo = task_repo

    async def add(self, section: Section) -> None:
        section_model = SectionModel(
            id=section.id, title=section.title, parent_id=section.parent_id
        )
        self._db_session.add(section_model)

    async def get(self, section_id: UUID) -> Optional[Section]:
        result = await self._db_session.execute(
            select(SectionModel).where(SectionModel.id == section_id)
        )
        section_model: Optional[SectionModel] = result.scalar_one_or_none()
        if section_model is None:
            return None

        tasks = await self._task_repo.get_tasks_by_section_id(section_id)

        return Section(
            id=section_model.id,
            title=section_model.title,
            parent_id=section_model.parent_id,
            tasks=tasks,
        )

    async def update(self, section: Section) -> None:
        result = await self._db_session.execute(
            select(SectionModel).where(SectionModel.id == section.id)
        )
        section_model: Optional[SectionModel] = result.scalar_one_or_none()
        if section_model is None:
            raise ValueError(f"Section with id {section.id} not found")

        section_model.title = section.title
        section_model.parent_id = section.parent_id

        self._db_session.add(section_model)
