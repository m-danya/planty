from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from planty.application.exceptions import (
    SectionNotFoundException,
    TaskNotFoundException,
    UserNotFoundException,
)
from planty.domain.entities import Section, Task, User, Username
from planty.infrastructure.models import SectionModel, TaskModel


class IUserRepository(ABC):
    @abstractmethod
    async def add(self, user: User) -> None: ...
    @abstractmethod
    async def get(self, user_id: UUID) -> User: ...


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def add(self, user: User) -> None: ...
    async def get(self, user_id: UUID) -> User:
        return User(username=Username("test_user"))


class ITaskRepository(ABC):
    @abstractmethod
    async def add(self, task: Task) -> None: ...
    @abstractmethod
    async def get(self, task_id: UUID) -> Task: ...
    @abstractmethod
    async def update(self, task: Task) -> None: ...
    @abstractmethod
    async def get_tasks_by_section_id(self, section_id: UUID) -> list[Task]: ...


class SQLAlchemyTaskRepository(ITaskRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def add(self, task: Task) -> None:
        task_model = TaskModel.from_entity(task)
        self._db_session.add(task_model)

    async def get(self, task_id: UUID) -> Task:
        result = await self._db_session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        task_model: Optional[TaskModel] = result.scalar_one_or_none()
        if task_model is None:
            raise TaskNotFoundException(task_id=task_id)

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
            raise TaskNotFoundException(task_id=task.id)

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
    async def get(self, section_id: UUID) -> Section: ...
    @abstractmethod
    async def get_all(self, section_id: UUID) -> Section: ...
    @abstractmethod
    async def update(self, section: Section) -> None: ...


class SQLAlchemySectionRepository(ISectionRepository):
    def __init__(self, db_session: AsyncSession, task_repo: ITaskRepository):
        self._db_session = db_session
        self._task_repo = task_repo

    async def add(self, section: Section) -> None:
        section_model = SectionModel(
            id=section.id, title=section.title, parent_id=section.parent_id
        )
        self._db_session.add(section_model)

    async def get(self, section_id: UUID) -> Section:
        result = await self._db_session.execute(
            select(SectionModel).where(SectionModel.id == section_id)
        )
        section_model: Optional[SectionModel] = result.scalar_one_or_none()
        if section_model is None:
            raise SectionNotFoundException(section_id=section_id)

        tasks = await self._task_repo.get_tasks_by_section_id(section_id)

        return Section(
            id=section_model.id,
            title=section_model.title,
            parent_id=section_model.parent_id,
            tasks=tasks,
        )

    async def get_all(self) -> list[Section]:
        result = await self._db_session.execute(select(SectionModel))
        section_models = result.scalars()
        return [
            Section(
                id=section_model.id,
                title=section_model.title,
                parent_id=section_model.parent_id,
                tasks=await self._task_repo.get_tasks_by_section_id(section_model.id),
            )
            for section_model in section_models
        ]

    async def update(self, section: Section) -> None:
        # Warning: this method does not update `section.tasks`
        result = await self._db_session.execute(
            select(SectionModel).where(SectionModel.id == section.id)
        )
        section_model: Optional[SectionModel] = result.scalar_one_or_none()
        if section_model is None:
            raise SectionNotFoundException(section_id=section.id)

        section_model.title = section.title
        section_model.parent_id = section.parent_id

        self._db_session.add(section_model)
