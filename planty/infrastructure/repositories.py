from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from planty.domain.entities import Task, User, Username
from planty.infrastructure.models import TaskModel


class ITaskRepository(ABC):
    @abstractmethod
    async def add(self, task: Task) -> None: ...
    @abstractmethod
    async def get(self, user: User, task_id: UUID) -> Optional[Task]: ...


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


class FakeTaskRepository(ITaskRepository):
    def __init__(self) -> None:
        self._tasks: list[Task] = []

    async def add(self, task: Task) -> None:
        self._tasks.append(task)

    async def get(self, user: User, task_id: UUID) -> Optional[Task]:
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None


class SQLAlchemyTaskRepository(ITaskRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def add(self, task: Task) -> None:
        task_model = TaskModel.from_entity(task)
        self._db_session.add(task_model)

    async def get(self, user: User, task_id: UUID) -> Optional[Task]:
        # TODO: make `user` optional, get it from UserRepository
        result = await self._db_session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        task_model: Optional[TaskModel] = result.scalar_one_or_none()
        if task_model is None:
            return None

        return Task(
            id=task_model.id,
            user=user,
            title=task_model.title,
            description=task_model.description,
            is_completed=task_model.is_completed,
            added_at=task_model.added_at,
            due_to_next=task_model.due_to_next,
            due_to_days_period=task_model.due_to_days_period,
        )
