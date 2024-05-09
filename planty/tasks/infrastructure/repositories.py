from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from planty.tasks.domain.entities import Task
from planty.tasks.infrastructure.models import TaskModel
from planty.utils import get_datetime_now


class ITaskRepository(ABC):
    @abstractmethod
    async def add(self, task: Task) -> None: ...


class SQLAlchemyTaskRepository(ITaskRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def add(self, task: Task) -> None:
        task_model = TaskModel(
            id=task.id,
            # user_id=task.user_id,
            # section_id=task.section_id,
            added_at=get_datetime_now(),
            title=task.title,
            description=task.description,
            is_completed=task.is_completed,
            due_to_next=task.due_to_next,
            due_to_days_period=task.due_to_days_period,
        )
        self._db_session.add(task_model)
