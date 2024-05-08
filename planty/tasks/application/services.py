"""Services representing usecases of an application"""

from planty.tasks.domain.entities import Task
from planty.tasks.application.schemas import TaskCreateModel
from planty.tasks.domain.repositories import ITaskRepository
from planty.utils import generate_uuid


class TaskService:
    def __init__(self, task_repository: ITaskRepository):
        self._task_repository = task_repository

    # async def get_task_by_id(self, task_id: int) -> Task:
    #     return self._task_repository.get_by_id(task_id)

    async def add_task(self, task: TaskCreateModel) -> None:
        task = Task(
            id=generate_uuid(),
            user_id=task.user_id,
            section_id=task.user_id,
            title=task.title,
            is_completed=False,
            due_to_next=task.due_to_next,
            due_to_days_period=task.due_to_days_period,
        )
        await self._task_repository.add(task)
