from datetime import date
from typing import Optional, Sequence
from uuid import UUID

from pydantic import NonNegativeInt
from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from planty.application.exceptions import (
    SectionNotFoundException,
    TaskNotFoundException,
    UserNotFoundException,
)
from planty.application.schemas import UserStats
from planty.domain.task import Attachment, Section, Task
from planty.infrastructure.models import (
    AttachmentModel,
    SectionModel,
    TaskModel,
    UserModel,
)
from planty.utils import get_today


class SQLAlchemyUserRepository:
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def get_all_users(self) -> list[UserStats]:
        result = await self._db_session.execute(
            select(
                UserModel,
                func.count(TaskModel.id).label("tasks_count"),
                func.count(SectionModel.id).label("sections_count"),
                func.count(AttachmentModel.id).label("attachments_count"),
                UserModel.is_superuser.label("is_superuser"),  # type: ignore
                UserModel.is_verified.label("is_verified"),  # type: ignore
            )
            .outerjoin(TaskModel, UserModel.id == TaskModel.user_id)  # type: ignore
            .outerjoin(SectionModel, UserModel.id == SectionModel.user_id)  # type: ignore
            .outerjoin(AttachmentModel, TaskModel.attachments)
            .group_by(UserModel)  # type: ignore
            .order_by(desc(UserModel.added_at))
        )

        users = []
        for (
            user_model,
            tasks_count,
            sections_count,
            attachments_count,
            is_superuser,
            is_verified,
        ) in result:
            user = user_model.to_entity().model_dump()
            user["tasks_count"] = tasks_count
            user["sections_count"] = sections_count
            user["attachments_count"] = attachments_count
            user["is_superuser"] = is_superuser
            user["is_verified"] = is_verified
            users.append(UserStats.model_validate(user))

        return users

    async def verify_user(self, user_id: UUID) -> None:
        result = await self._db_session.execute(
            select(UserModel).where(UserModel.id == user_id)  # type: ignore
        )
        user_model: Optional[UserModel] = result.scalar_one_or_none()
        if user_model is None:
            raise UserNotFoundException(user_id=user_id)
        user_model.is_verified = True
        self._db_session.add(user_model)


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
            select(TaskModel)
            .where(TaskModel.id == task_id)
            .options(selectinload(TaskModel.attachments))
        )
        task_model: Optional[TaskModel] = result.scalar_one_or_none()
        if task_model is None:
            raise TaskNotFoundException(task_id=task_id)
        return await self.get_entity(task_model)

    async def get_entity(self, task_model: TaskModel) -> Task:
        return task_model.to_entity(
            attachments=[
                attachment.to_entity() for attachment in task_model.attachments
            ]
        )

    async def get_entities(self, task_models: Sequence[TaskModel]) -> list[Task]:
        return [
            task_model.to_entity(
                attachments=[
                    attachment.to_entity() for attachment in task_model.attachments
                ]
            )
            for task_model in task_models
        ]

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

        self._fill_in_model_except_index(task, task_model)

        # update index if it's meant to be updated
        if index is not None:
            task_model.index = index

        for i, attachment in enumerate(task.attachments):
            await self._persist_attachment(attachment, index=i)

        self._db_session.add(task_model)

    async def update_or_create_bulk(
        self,
        section_tasks: list[Task],
    ) -> None:
        # NOTE: it is assumed that indexes are 0..N-1 for given tasks
        tasks = section_tasks

        existing_ids = [t.id for t in tasks if t.id is not None]

        existing_tasks_result = await self._db_session.execute(
            select(TaskModel).where(TaskModel.id.in_(existing_ids))
        )

        existing_task_models = existing_tasks_result.scalars().all()
        existing_tasks_map = {tm.id: tm for tm in existing_task_models}

        for i, task in enumerate(tasks):
            if task.id in existing_tasks_map:
                task_model = existing_tasks_map[task.id]
            else:
                await self.add(task, index=i)
                continue

            self._fill_in_model_except_index(task, task_model)
            task_model.index = i

            for i, attachment in enumerate(task.attachments):
                await self._persist_attachment(attachment, index=i)

            self._db_session.add(task_model)

    def _fill_in_model_except_index(self, task: Task, task_model: TaskModel) -> None:
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

    async def search(self, user_id: UUID, query: str) -> list[Task]:
        # TODO: Reimplement search to improve performance. Possible options:
        # 1) Use PostgreSQL Full-text search ( => deal with SQLite separately.. )
        # 2) Use Whoosh (add volume for index persistence)
        # 3) Explore other options..

        query = f"%{query}%"

        query = (
            select(TaskModel)
            .where(
                (TaskModel.user_id == user_id)
                & (TaskModel.is_archived.is_(False))
                & (TaskModel.title.ilike(query) | TaskModel.description.ilike(query))
            )
            .options(selectinload(TaskModel.attachments))
        )
        result = await self._db_session.execute(query)
        task_models = result.scalars().all()
        return await self.get_entities(task_models)

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

    async def get_tasks_by_due_to(
        self, not_before: date, not_after: date, user_id: UUID
    ) -> list[Task]:
        result = await self._db_session.execute(
            select(TaskModel)
            .where(
                (TaskModel.user_id == user_id)
                & (TaskModel.due_to >= not_before)
                & (TaskModel.due_to <= not_after)
                & (TaskModel.is_archived.is_(False))
            )
            .options(selectinload(TaskModel.attachments))
        )
        task_models = result.scalars().all()
        return await self.get_entities(task_models)

    async def get_overdue_tasks(self, user_id: UUID) -> list[Task]:
        result = await self._db_session.execute(
            select(TaskModel)
            .where(
                (TaskModel.user_id == user_id)
                & (TaskModel.due_to < get_today())
                & (TaskModel.is_archived.is_(False))
            )
            .options(selectinload(TaskModel.attachments))
            .order_by(asc(TaskModel.due_to), asc(TaskModel.added_at))
        )
        task_models = result.scalars().all()
        return await self.get_entities(task_models)

    async def get_archived_tasks(self, user_id: UUID) -> list[Task]:
        result = await self._db_session.execute(
            select(TaskModel)
            .where((TaskModel.user_id == user_id) & (TaskModel.is_archived.is_(True)))
            .order_by(desc(TaskModel.added_at))
            .options(selectinload(TaskModel.attachments))
        )
        task_models = result.scalars().all()
        return await self.get_entities(task_models)

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

    async def get(
        self,
        section_id: UUID,
        with_direct_subsections: bool = False,
    ) -> Section:
        result = await self._db_session.execute(
            select(SectionModel)
            .where(SectionModel.id == section_id)
            .options(
                selectinload(SectionModel.tasks).selectinload(TaskModel.attachments)
            )
        )
        section_model: Optional[SectionModel] = result.scalar_one_or_none()
        if section_model is None:
            raise SectionNotFoundException(section_id=section_id)
        # filter out archived tasks from section tasks
        task_models = [tm for tm in section_model.tasks if not tm.is_archived]
        tasks = await self._task_repo.get_entities(task_models)
        subsections = []
        if with_direct_subsections:
            subsection_models = (
                (
                    await self._db_session.execute(
                        select(SectionModel).where(SectionModel.parent_id == section_id)
                    )
                )
                .scalars()
                .all()
            )
            direct_subsections = [
                s.to_entity(tasks=[], subsections=[]) for s in subsection_models
            ]
            subsections = direct_subsections
        return section_model.to_entity(tasks=tasks, subsections=subsections)

    async def get_all_without_tasks(
        self, user_id: UUID, leaves_only: bool, as_tree: bool
    ) -> list[Section]:
        result = await self._db_session.execute(
            select(SectionModel).where(SectionModel.user_id == user_id)
        )
        section_models = list(result.scalars().all())
        if leaves_only:
            return [
                model.to_entity(tasks=[], subsections=[])
                for model in section_models
                if not model.has_subsections
            ]
        else:
            return self.construct_sections_tree(section_models, return_flat=not as_tree)

    @staticmethod
    def construct_sections_tree(
        section_models: list[SectionModel], return_flat: bool = False
    ) -> list[Section]:
        # TODO: extract to generic function for other entities
        # TODO: sort using SQL in repository instead
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
        if return_flat:
            return all_sections
        else:
            return top_level_sections

    async def count_subsections(self, section_id: UUID) -> int:
        result = await self._db_session.execute(
            select(SectionModel).where(SectionModel.parent_id == section_id)
        )
        return len(result.all())

    async def update(
        self, section: Section, index: Optional[NonNegativeInt] = None
    ) -> None:
        result = await self._db_session.execute(
            select(SectionModel)
            .where(SectionModel.id == section.id)
            .options(selectinload(SectionModel.tasks))
        )
        section_model: Optional[SectionModel] = result.scalar_one_or_none()
        if section_model is None:
            raise SectionNotFoundException(section_id=section.id)

        section_model.title = section.title
        section_model.parent_id = section.parent_id

        section_model.has_tasks = section.has_tasks
        section_model.has_subsections = section.has_subsections

        # update index if it's meant to be updated
        if index is not None:
            section_model.index = index

        # Tasks can be loaded or not, it doesn't matter
        # Warning: does not update any excluded tasks from section.tasks

        await self._task_repo.update_or_create_bulk(section.tasks)

        for i, subsection in enumerate(section.subsections):
            await self.update(subsection, index=i)

        self._db_session.add(section_model)


# NOTE: Replace with real interfaces if it becomes clear that other
# implementations may appear. For now interfaces are omitted in order to remove
# unnecessary duplication of method declarations
IUserRepository = SQLAlchemyUserRepository
ITaskRepository = SQLAlchemyTaskRepository
ISectionRepository = SQLAlchemySectionRepository
