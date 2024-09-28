"""Services representing usecases of an application"""

from datetime import date
from uuid import UUID

from planty.application.exceptions import IncorrectDateInterval, TaskNotFoundException
from planty.application.schemas import (
    SectionCreateRequest,
    ShuffleSectionRequest,
    TaskCreateRequest,
    TaskMoveRequest,
    TaskUpdateRequest,
)
from planty.application.uow import IUnitOfWork
from planty.domain.calendar import multiply_tasks_with_recurrences
from planty.domain.task import Section, Task


class TaskService:
    def __init__(self, uow: IUnitOfWork):
        self._task_repo = uow.task_repo
        self._user_repo = uow.user_repo

    async def update_task(self, task_data: TaskUpdateRequest) -> Task:
        task = await self._task_repo.get(task_data.id)
        task_data = task_data.model_dump(exclude_unset=True)
        for key, value in task_data.items():
            setattr(task, key, value)
        await self._task_repo.update_or_create(task)
        return task

    async def toggle_task_completed(self, task_id: UUID) -> bool:
        task = await self._task_repo.get(task_id)
        if not task:
            raise TaskNotFoundException(task_id=task_id)
        task.toggle_completed()
        await self._task_repo.update_or_create(task)
        return task.is_completed

    async def get_tasks_by_date(
        self,
        user_id: UUID,
        not_before: date,
        not_after: date,
    ) -> dict[date, list[Task]]:
        if not_before > not_after:
            raise IncorrectDateInterval()
        prefiltered_tasks = await self._task_repo.get_tasks_by_due_date(
            not_before=not_before,
            not_after=not_after,
            user_id=user_id,
        )
        return multiply_tasks_with_recurrences(prefiltered_tasks, not_after)


class SectionService:
    def __init__(self, uow: IUnitOfWork):
        self._section_repo = uow.section_repo
        self._task_repo = uow.task_repo

    async def add(self, section_data: SectionCreateRequest) -> Section:
        section = Section(title=section_data.title, parent_id=None, tasks=[])
        await self._section_repo.add(section)
        return section

    async def get_section(self, section_id: UUID) -> Section:
        return await self._section_repo.get(section_id)

    async def get_all_sections(self) -> list[Section]:
        return await self._section_repo.get_all()

    async def create_task(self, task: TaskCreateRequest) -> UUID:
        task = Task(
            user_id=task.user_id,
            section_id=task.section_id,
            title=task.title,
            is_completed=False,
            due_to=task.due_to,
            recurrence=task.recurrence,
        )
        section = await self._section_repo.get(task.section_id)
        section.insert_task(task)
        await self._section_repo.update(section)
        return task.id

    async def remove_task(self, task_id: UUID) -> None:
        task = await self._task_repo.get(task_id)
        section = await self._section_repo.get(task.section_id)
        task = section.remove_task(task)
        await self._task_repo.remove(task)
        await self._section_repo.update(section)

    async def move_task(self, request: TaskMoveRequest) -> None:
        task = await self._task_repo.get(request.task_id)
        section_from = await self._section_repo.get(task.section_id)
        same_section = request.section_to_id == section_from.id
        if same_section:
            section_to = section_from
        else:
            section_to = await self._section_repo.get(request.section_to_id)

        Section.move_task(task, section_from, section_to, request.index)

        if same_section:
            await self._section_repo.update(section_from)
        else:
            await self._section_repo.update(section_from)
            await self._section_repo.update(section_to)

    async def shuffle(self, request: ShuffleSectionRequest) -> Section:
        section = await self._section_repo.get(request.section_id)
        section.shuffle_tasks()
        await self._section_repo.update(section)
        return section
