from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import NonNegativeInt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from planty.application.exceptions import (
    SectionNotFoundException,
    TaskNotFoundException,
)
from planty.domain.task import Attachment, Section, Task
from planty.infrastructure.models import (
    AttachmentModel,
    SectionModel,
    TaskModel,
)


class SQLAlchemyUserRepository:
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session


class SQLAlchemyTaskRepository:
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def add(self, task: Task, index: NonNegativeInt) -> None:
        # assuming that task can't have attachments when created
        # (according to `TaskCreateRequest`)
        task_model = TaskModel.from_entity(task, index=index)
        self._db_session.add(task_model)

    async def get(self, task_id: UUID) -> Task:
        result = await self._db_session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        task_model: Optional[TaskModel] = result.scalar_one_or_none()
        if task_model is None:
            raise TaskNotFoundException(task_id=task_id)
        return await self.get_entity(task_model)

    async def get_entity(self, task_model: TaskModel) -> Task:
        return task_model.to_entity(
            attachments=await self._get_task_attachments(task_model.id)
        )

    async def update_or_create(
        self,
        task: Task,
        index: Optional[NonNegativeInt] = None,
        must_exist: bool = False,
    ) -> None:
        result = await self._db_session.execute(
            select(TaskModel).where(TaskModel.id == task.id)
        )
        task_model: Optional[TaskModel] = result.scalar_one_or_none()
        if task_model is None:
            if must_exist:
                raise TaskNotFoundException(task_id=task.id)
            assert index is not None
            await self.add(task, index=index)
            return

        task_model.user_id = task.user_id
        task_model.section_id = task.section_id
        task_model.title = task.title
        task_model.description = task.description
        task_model.is_completed = task.is_completed
        task_model.is_archived = task.is_archived
        task_model.added_at = task.added_at
        task_model.due_to = task.due_to

        if task.recurrence is None:
            task_model.recurrence_period = None
            task_model.recurrence_type = None
            task_model.flexible_recurrence_mode = None
        else:
            task_model.recurrence_period = task.recurrence.period
            task_model.recurrence_type = task.recurrence.type
            task_model.flexible_recurrence_mode = task.recurrence.flexible_mode

        # update index if it's meant to be updated
        if index is not None:
            task_model.index = index

        for i, attachment in enumerate(task.attachments):
            await self._persist_attachment(attachment, index=i)

        self._db_session.add(task_model)

    async def get_section_tasks(self, section_id: UUID) -> list[Task]:
        result = await self._db_session.execute(
            select(TaskModel).where(
                (TaskModel.section_id == section_id)
                & (TaskModel.is_archived.is_(False))
            )
        )
        task_models = result.scalars().all()
        return [
            await self.get_entity(task_model)
            for task_model in sorted(task_models, key=lambda t: t.index)
        ]

    async def search(self, user_id: UUID, query: str) -> list[Task]:
        # TODO: Reimplement search to improve performance. Possible options:
        # 1) Use PostgreSQL Full-text search ( => deal with SQLite separately.. )
        # 2) Use Whoosh (add volume for index persistence)
        # 3) Explore other options..

        query = f"%{query}%"

        query = select(TaskModel).where(
            (TaskModel.user_id == user_id)
            & (TaskModel.is_archived.is_(False))
            & (TaskModel.title.ilike(query) | TaskModel.description.ilike(query))
        )

        result = await self._db_session.execute(query)
        task_models = result.scalars().all()

        return [await self.get_entity(task_model) for task_model in task_models]

    async def _get_task_attachments(self, task_id: UUID) -> list[Attachment]:
        result = await self._db_session.execute(
            select(AttachmentModel).where(AttachmentModel.task_id == task_id)
        )
        attachment_models = result.scalars().all()
        return [
            attachment_model.to_entity()
            for attachment_model in sorted(attachment_models, key=lambda t: t.index)
        ]

    async def _persist_attachment(
        self, attachment: Attachment, index: NonNegativeInt
    ) -> None:
        result = await self._db_session.execute(
            select(AttachmentModel).where(AttachmentModel.id == attachment.id)
        )
        attachment_model: Optional[AttachmentModel] = result.scalar_one_or_none()
        if attachment_model is not None:
            # attachment exists -> ok (attachments can't be updated)
            return
        attachment_model = AttachmentModel.from_entity(attachment, index=index)
        self._db_session.add(attachment_model)

    async def delete_attachment(self, attachment: Attachment) -> None:
        result = await self._db_session.execute(
            select(AttachmentModel).where(AttachmentModel.id == attachment.id)
        )
        attachment_model: Optional[AttachmentModel] = result.scalar_one_or_none()
        await self._db_session.delete(attachment_model)

    async def get_tasks_by_due_date(
        self, not_before: date, not_after: date, user_id: UUID
    ) -> list[Task]:
        result = await self._db_session.execute(
            select(TaskModel).where(
                (TaskModel.user_id == user_id)
                & TaskModel.due_to.between(not_before, not_after)
                & (TaskModel.is_archived.is_(False))
            )
        )
        task_models = result.scalars().all()
        return [await self.get_entity(task_model) for task_model in task_models]

    async def get_archived_tasks(self, user_id: UUID) -> list[Task]:
        result = await self._db_session.execute(
            select(TaskModel).where(
                (TaskModel.user_id == user_id) & (TaskModel.is_archived.is_(True))
            )
        )
        task_models = result.scalars().all()
        return [await self.get_entity(task_model) for task_model in task_models]

    async def remove(self, task: Task) -> None:
        result = await self._db_session.execute(
            select(TaskModel).where(TaskModel.id == task.id)
        )
        task_model = result.scalar_one_or_none()
        if task_model is None:
            raise TaskNotFoundException(task_id=task.id)
        await self._db_session.delete(task_model)


class SQLAlchemySectionRepository:
    def __init__(self, db_session: AsyncSession, task_repo: "ITaskRepository"):
        self._db_session = db_session
        self._task_repo = task_repo

    async def add(self, section: Section, index: NonNegativeInt) -> None:
        section_model = SectionModel.from_entity(section, index=index)
        self._db_session.add(section_model)

    async def get(self, section_id: UUID) -> Section:
        result = await self._db_session.execute(
            select(SectionModel).where(SectionModel.id == section_id)
        )
        section_model: Optional[SectionModel] = result.scalar_one_or_none()
        if section_model is None:
            raise SectionNotFoundException(section_id=section_id)
        tasks = await self._task_repo.get_section_tasks(section_id)
        return section_model.to_entity(tasks=tasks, subsections=[])

    async def get_all_without_tasks(self, user_id: UUID) -> list[Section]:
        result = await self._db_session.execute(
            select(SectionModel).where(SectionModel.user_id == user_id)
        )
        section_models = list(result.scalars().all())
        top_level_sections = self.get_sections_tree(section_models)
        return top_level_sections

    @staticmethod
    def get_sections_tree(
        section_models: list[SectionModel], return_as_tree: bool = True
    ) -> list[Section]:
        # TODO: extract to generic function for other entities
        section_models.sort(key=lambda s: s.index)
        # TODO: use delay_validation here
        id_to_section: dict[UUID, Section] = {
            section_model.id: section_model.to_entity(tasks=[], subsections=[])
            for section_model in section_models
        }
        top_level_sections = []
        all_sections = []
        for section in id_to_section.values():
            if (parent_id := section.parent_id) is None:
                top_level_sections.append(section)
            else:
                parent_section = id_to_section[parent_id]
                parent_section.subsections.append(section)
            all_sections.append(section)
        if return_as_tree:
            return top_level_sections
        else:
            return all_sections

    async def count_subsections(self, section_id: UUID) -> int:
        result = await self._db_session.execute(
            select(SectionModel).where(SectionModel.parent_id == section_id)
        )
        return len(result.all())

    async def update(
        self, section: Section, index: Optional[NonNegativeInt] = None
    ) -> None:
        result = await self._db_session.execute(
            select(SectionModel).where(SectionModel.id == section.id)
        )
        section_model: Optional[SectionModel] = result.scalar_one_or_none()
        if section_model is None:
            raise SectionNotFoundException(section_id=section.id)

        section_model.title = section.title
        section_model.parent_id = section.parent_id

        # update index if it's meant to be updated
        if index is not None:
            section_model.index = index

        # Tasks can be loaded or not, it doesn't matter
        # Warning: does not update any excluded tasks from section.tasks
        for i, task in enumerate(section.tasks):
            await self._task_repo.update_or_create(task, index=i)

        self._db_session.add(section_model)


# NOTE: Replace with real interfaces if it becomes clear that other
# implementations may appear. For now interfaces are omitted in order to remove
# unnecessary duplication of method declarations
IUserRepository = SQLAlchemyUserRepository
ITaskRepository = SQLAlchemyTaskRepository
ISectionRepository = SQLAlchemySectionRepository
