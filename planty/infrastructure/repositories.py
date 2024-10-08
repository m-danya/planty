from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import NonNegativeInt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from planty.application.exceptions import (
    SectionNotFoundException,
    TaskNotFoundException,
    UserNotFoundException,
)
from planty.domain.task import Attachment, Section, Task, User
from planty.infrastructure.models import (
    AttachmentModel,
    SectionModel,
    TaskModel,
    UserModel,
)


class SQLAlchemyUserRepository:
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def add(self, user: User) -> None:
        user_model = UserModel.from_entity(user)
        self._db_session.add(user_model)

    async def get(self, user_id: UUID) -> User:
        result = await self._db_session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model: Optional[UserModel] = result.scalar_one_or_none()
        if user_model is None:
            raise UserNotFoundException(user_id=user_id)

        return User(
            id=user_model.id,
            username=user_model.username,
            added_at=user_model.added_at,
        )


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

        if index is not None:
            task_model.index = index

        for i, attachment in enumerate(task.attachments):
            await self._persist_attachment(attachment, index=i)

        self._db_session.add(task_model)

    async def get_section_tasks(self, section_id: UUID) -> list[Task]:
        result = await self._db_session.execute(
            select(TaskModel).where(TaskModel.section_id == section_id)
        )
        task_models = result.scalars().all()
        return [
            await self.get_entity(task_model)
            for task_model in sorted(task_models, key=lambda t: t.index)
        ]

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

    async def get_tasks_by_due_date(
        self, not_before: date, not_after: date, user_id: UUID
    ) -> list[Task]:
        result = await self._db_session.execute(
            select(TaskModel).where(
                (TaskModel.user_id == user_id)
                & TaskModel.due_to.between(not_before, not_after)
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

        if task_model:
            await self._db_session.delete(task_model)


class SQLAlchemySectionRepository:
    def __init__(self, db_session: AsyncSession, task_repo: "ITaskRepository"):
        self._db_session = db_session
        self._task_repo = task_repo

    async def add(self, section: Section) -> None:
        section_model = SectionModel.from_entity(section)
        self._db_session.add(section_model)

    async def get(self, section_id: UUID) -> Section:
        result = await self._db_session.execute(
            select(SectionModel).where(SectionModel.id == section_id)
        )
        section_model: Optional[SectionModel] = result.scalar_one_or_none()
        if section_model is None:
            raise SectionNotFoundException(section_id=section_id)
        tasks = await self._task_repo.get_section_tasks(section_id)
        return section_model.to_entity(tasks=tasks)

    async def get_all(self) -> list[Section]:
        result = await self._db_session.execute(select(SectionModel))
        section_models = result.scalars()
        return [
            section_model.to_entity(
                tasks=await self._task_repo.get_section_tasks(section_model.id)
            )
            for section_model in section_models
        ]

    async def update_without_tasks(self, section: Section) -> None:
        result = await self._db_session.execute(
            select(SectionModel).where(SectionModel.id == section.id)
        )
        section_model: Optional[SectionModel] = result.scalar_one_or_none()
        if section_model is None:
            raise SectionNotFoundException(section_id=section.id)

        section_model.title = section.title
        section_model.parent_id = section.parent_id

        self._db_session.add(section_model)

    async def update(self, section: Section) -> None:
        # Warning: does not update any excluded tasks from section.tasks
        result = await self._db_session.execute(
            select(SectionModel).where(SectionModel.id == section.id)
        )
        section_model: Optional[SectionModel] = result.scalar_one_or_none()
        if section_model is None:
            raise SectionNotFoundException(section_id=section.id)

        section_model.title = section.title
        section_model.parent_id = section.parent_id

        for i, task in enumerate(section.tasks):
            await self._task_repo.update_or_create(task, index=i)

        self._db_session.add(section_model)


# NOTE: Replace with real interfaces if it becomes clear that other
# implementations may appear. For now interfaces are omitted in order to remove
# unnecessary duplication of method declarations
IUserRepository = SQLAlchemyUserRepository
ITaskRepository = SQLAlchemyTaskRepository
ISectionRepository = SQLAlchemySectionRepository
