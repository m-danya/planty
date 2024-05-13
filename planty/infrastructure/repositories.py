from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from planty.domain.entities import Task, User
from planty.infrastructure.models import TaskModel


class ITaskRepository(ABC):
    @abstractmethod
    async def add(self, task: Task) -> None: ...
    async def get(self, task_id: UUID) -> Optional[Task]: ...


class SQLAlchemyTaskRepository(ITaskRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def add(self, task: Task) -> None:
        task_model = TaskModel(
            id=task.id,
            user_id=task.user.id,
            # section_id=task.section_id,
            added_at=task.added_at,
            title=task.title,
            description=task.description,
            is_completed=task.is_completed,
            due_to_next=task.due_to_next,
            due_to_days_period=task.due_to_days_period,
        )
        self._db_session.add(task_model)

    async def get(self, task_id: UUID) -> Optional[Task]:
        result = await self._db_session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        task_model: Optional[TaskModel] = result.scalar_one_or_none()
        if task_model is None:
            return None

        # TODO: load user with SQLAlchemy relationship!
        user = User(username="temp_user")

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
