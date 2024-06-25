"""Services representing usecases of an application"""

from planty.application.exceptions import UserNotFoundException
from planty.application.schemas import TaskCreateRequest
from planty.domain.entities import Task
from planty.infrastructure.repositories import ITaskRepository, IUserRepository


class TaskService:
    def __init__(self, task_repo: ITaskRepository, user_repo: IUserRepository):
        self._task_repo = task_repo
        self._user_repo = user_repo

    async def add_task(self, task: TaskCreateRequest) -> None:
        user = await self._user_repo.get(task.user_id)
        if not user:
            raise UserNotFoundException(id=task.user_id)
        task = Task(
            user=user,
            # section_id=task.user_id,
            title=task.title,
            is_completed=False,
            due_to_next=task.due_to_next,
            due_to_days_period=task.due_to_days_period,
        )
        await self._task_repo.add(task)
