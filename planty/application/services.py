"""Services representing usecases of an application"""

from typing import Optional
from uuid import UUID

from planty.application.exceptions import TaskNotFoundException
from planty.application.schemas import SectionCreateRequest, TaskCreateRequest
from planty.domain.entities import Section, Task
from planty.infrastructure.repositories import (
    ISectionRepository,
    ITaskRepository,
    IUserRepository,
)


class TaskService:
    def __init__(self, task_repo: ITaskRepository, user_repo: IUserRepository):
        self._task_repo = task_repo
        self._user_repo = user_repo

    async def add_task(self, task: TaskCreateRequest) -> UUID:
        task = Task(
            user_id=task.user_id,
            section_id=task.section_id,
            title=task.title,
            is_completed=False,
            due_to_next=task.due_to_next,
            due_to_days_period=task.due_to_days_period,
        )
        await self._task_repo.add(task)
        return task.id

    async def get_task(self, task_id: UUID) -> Task:
        task = await self._task_repo.get(task_id)
        if not task:
            raise TaskNotFoundException(task_id=task_id)
        return task

    async def mark_task_completed(self, task_id: UUID) -> None:
        task = await self._task_repo.get(task_id)
        if not task:
            raise TaskNotFoundException(task_id=task_id)
        task.mark_completed()
        await self._task_repo.update(task)


class SectionService:
    def __init__(self, section_repo: ISectionRepository, task_repo: ITaskRepository):
        self._section_repo = section_repo
        self._task_repo = task_repo

    async def add(self, section_data: SectionCreateRequest) -> Section:
        section = Section(title=section_data.title, parent_id=None, tasks=[])
        await self._section_repo.add(section)
        return section

    async def get_section(self, section_id: UUID) -> Optional[Section]:
        section = await self._section_repo.get(section_id)
        return section
