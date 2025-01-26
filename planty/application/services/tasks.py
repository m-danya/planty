from datetime import date
from uuid import UUID

import aiobotocore
import aiobotocore.session

from planty.application.exceptions import (
    AttachmentNotFoundException,
    ForbiddenException,
    IncorrectDateInterval,
    TaskNotFoundException,
)
from planty.application.schemas import (
    ArchivedTasks,
    AttachmentUploadInfo,
    RequestAttachmentUpload,
    ArchivedTasksResponse,
    SectionCreateRequest,
    SectionMoveRequest,
    SectionResponse,
    SectionUpdateRequest,
    ShuffleSectionRequest,
    TaskCreateRequest,
    TaskMoveRequest,
    TaskResponse,
    TasksByDatesResponse,
    TaskUpdateRequest,
    TaskSearchResponse,
    SectionsListResponse,
)
from planty.application.services.attachments import (
    delete_attachment,
    generate_presigned_post_url,
)
from planty.application.services.responses_converter import (
    convert_to_response,
)
from planty.application.uow import IUnitOfWork
from planty.domain.calendar import get_tasks_by_dates
from planty.domain.exceptions import (
    ChangingRootSectionError,
    MisplaceSectionHierarchyError,
)
from planty.domain.task import Attachment, Section, Task


class TaskService:
    def __init__(self, uow: IUnitOfWork):
        self._task_repo = uow.task_repo
        self._user_repo = uow.user_repo
        self._s3_session = aiobotocore.session.get_session()

    async def update_task(
        self, user_id: UUID, task_update_request: TaskUpdateRequest
    ) -> TaskResponse:
        task: Task = await self._task_repo.get(task_update_request.id)
        if task.user_id != user_id:
            raise ForbiddenException()
        updated_task_data = task_update_request.model_dump(exclude_unset=True)

        # Avoid triggering validation on every field assignment. Otherwise, this
        # can trigger validation error because of partial attributes update,
        # e.g. if `due_to` is set to `None` before `recurrence` is set to
        # `None`.
        task_data = task.model_dump()
        task_data.update(updated_task_data)
        task = Task.model_validate(task_data)

        await self._task_repo.update_or_create(task)
        return convert_to_response(task)

    async def get_tasks_by_date(
        self,
        user_id: UUID,
        not_before: date,
        not_after: date,
    ) -> TasksByDatesResponse:
        if not_before > not_after:
            raise IncorrectDateInterval()
        tasks = await self._task_repo.get_tasks_by_due_to(
            not_before=not_before,
            not_after=not_after,
            user_id=user_id,
        )
        tasks_by_dates = get_tasks_by_dates(tasks, not_before, not_after)
        return convert_to_response(tasks_by_dates)

    async def get_archived_tasks(self, user_id: UUID) -> ArchivedTasksResponse:
        tasks = await self._task_repo.get_archived_tasks(user_id)
        tasks = ArchivedTasks(tasks=tasks)
        return convert_to_response(tasks)

    async def get_tasks_by_search_query(
        self, user_id: UUID, query: str
    ) -> TaskSearchResponse:
        tasks = await self._task_repo.search(user_id, query)
        return convert_to_response(tasks)

    async def add_attachment(
        self, user_id: UUID, request: RequestAttachmentUpload
    ) -> AttachmentUploadInfo:
        task = await self._task_repo.get(request.task_id)
        if task.user_id != user_id:
            raise ForbiddenException()
        post_url, post_fields, file_key = await generate_presigned_post_url(
            self._s3_session
        )
        task.add_attachment(
            Attachment(
                task_id=task.id,
                aes_key_b64=request.aes_key_b64,
                aes_iv_b64=request.aes_iv_b64,
                s3_file_key=file_key,
            )
        )
        await self._task_repo.update_or_create(task)
        return AttachmentUploadInfo(post_url=post_url, post_fields=post_fields)

    async def remove_attachment(
        self, user_id: UUID, task_id: UUID, attachment_id: UUID
    ) -> None:
        task = await self._task_repo.get(task_id)
        if task.user_id != user_id:
            raise ForbiddenException()
        try:
            attachment: Attachment = next(
                a for a in task.attachments if a.id == attachment_id
            )
        except StopIteration:
            raise AttachmentNotFoundException(id=attachment_id)
        # remove from minio
        await delete_attachment(self._s3_session, attachment.s3_file_key)
        task.remove_attachment(attachment)
        await self._task_repo.update_or_create(task)
        await self._task_repo.delete_attachment(attachment)


class SectionService:
    def __init__(self, uow: IUnitOfWork):
        self._section_repo = uow.section_repo
        self._task_repo = uow.task_repo

    # TODO: when writing "update_section" don't forget to raise
    # ChangingRootSectionError if root section is being updated

    async def add(self, user_id: UUID, section_data: SectionCreateRequest) -> Section:
        if parent_id := section_data.parent_id:
            parent_section = await self._section_repo.get(
                parent_id, with_direct_subsections=True
            )
            if parent_section.user_id != user_id:
                raise ForbiddenException()
            # add to the end of parent section:
            index = await self._section_repo.count_subsections(parent_section.id)
        else:
            index = 0
        section = Section(
            user_id=user_id,
            title=section_data.title,
            parent_id=section_data.parent_id,
            tasks=[],
            subsections=[],
            has_subsections=False,
            has_tasks=False,
        )
        parent_section.insert_subsection(
            section, index
        )  # this line checks constraints of parent_section
        await self._section_repo.add(section, index=index)
        return section

    async def update_section(
        self, user_id: UUID, section_data: SectionUpdateRequest
    ) -> SectionResponse:
        section: Section = await self._section_repo.get(section_data.id)
        if section.user_id != user_id:
            raise ForbiddenException()
        section_data = section_data.model_dump(exclude_unset=True)
        for key, value in section_data.items():
            setattr(section, key, value)
        await self._section_repo.update(section)
        return convert_to_response(section)

    async def get_section(self, user_id: UUID, section_id: UUID) -> SectionResponse:
        section: Section = await self._section_repo.get(section_id)
        if section.user_id != user_id:
            raise ForbiddenException()
        return convert_to_response(section)

    async def get_all_sections(
        self, user_id: UUID, leaves_only: bool, as_tree: bool
    ) -> SectionsListResponse:
        sections: list[Section] = await self._section_repo.get_all_without_tasks(
            user_id, leaves_only=leaves_only, as_tree=as_tree
        )
        # TODO: remove tasks=[] from this schema to avoid confusion! use new
        # schema, e.g. "SectionSummary"
        return convert_to_response(sections)

    async def create_task(self, user_id: UUID, task: TaskCreateRequest) -> UUID:
        task = Task(
            user_id=user_id,
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

    async def create_tasks_bulk(
        self, user_id: UUID, task_requests: list[TaskCreateRequest]
    ) -> list[UUID]:
        if not task_requests:
            return []
        # assuming tasks[i].section_id are the same:
        assert all(
            task.section_id == task_requests[0].section_id for task in task_requests
        )
        task_ids = []
        tasks = []
        for task_request in task_requests:
            task = Task(
                user_id=user_id,
                section_id=task_request.section_id,
                title=task_request.title,
                is_completed=False,
                due_to=task_request.due_to,
                recurrence=task_request.recurrence,
            )
            task_ids.append(task.id)
            tasks.append(task)
        section = await self._section_repo.get(tasks[0].section_id)
        for task in tasks:
            section.insert_task(task)
        await self._section_repo.update(section)
        return task_ids

    async def remove_task(self, user_id: UUID, task_id: UUID) -> None:
        task = await self._task_repo.get(task_id)
        if task.user_id != user_id:
            raise ForbiddenException()
        section = await self._section_repo.get(task.section_id)
        task = section.remove_task(task)
        await self._task_repo.remove(task)
        await self._section_repo.update(section)

    async def move_task(self, user_id: UUID, request: TaskMoveRequest) -> None:
        task = await self._task_repo.get(request.task_id)
        if task.user_id != user_id:
            raise ForbiddenException()
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

    async def move_section(self, user_id: UUID, request: SectionMoveRequest) -> None:
        # move `section` from `section_from` to `section to` with given `index``
        section = await self._section_repo.get(
            request.section_id, with_direct_subsections=True
        )
        if section.user_id != user_id:
            raise ForbiddenException()
        if section.is_root():
            raise ChangingRootSectionError()
        assert section.parent_id  # (because it's not root, assert for type checking)
        section_to = await self._section_repo.get(
            request.to_parent_id, with_direct_subsections=True
        )
        if section_to.user_id != user_id:
            raise ForbiddenException()
        same_section = request.to_parent_id == section.parent_id
        if same_section:
            section_from = section_to
        else:
            section_from = await self._section_repo.get(
                section.parent_id, with_direct_subsections=True
            )

        is_valid_moving = await self.is_hierarchically_valid_moving(
            user_id, section.id, section_to.id
        )
        if not is_valid_moving:
            raise MisplaceSectionHierarchyError()

        Section.move_section(section, section_from, section_to, request.index)

        await self._section_repo.update(section)
        if same_section:
            await self._section_repo.update(section_from)
        else:
            await self._section_repo.update(section_from)
            await self._section_repo.update(section_to)

    async def is_hierarchically_valid_moving(
        self, user_id: UUID, section_id: UUID, section_to_id: UUID
    ) -> bool:
        sections = await self._section_repo.get_all_without_tasks(
            user_id=user_id, leaves_only=False, as_tree=False
        )

        def find_section_by_id(section_id: UUID) -> Section:
            return next(s for s in sections if s.id == section_id)

        section_to = find_section_by_id(section_to_id)
        if section_to.id == section_id:
            return False
        s = section_to
        while s.parent_id:
            if s.id == section_id:
                return False
            s = find_section_by_id(s.parent_id)
        return True

    async def toggle_task_completed(
        self, user_id: UUID, task_id: UUID, auto_archive: bool
    ) -> SectionResponse:
        task = await self._task_repo.get(task_id)
        if task.user_id != user_id:
            raise ForbiddenException()
        section = await self._section_repo.get(task.section_id)
        if not task:
            raise TaskNotFoundException(task_id=task_id)
        task_is_archived_before = task.is_archived

        task.toggle_completed(auto_archive=auto_archive)

        if task.is_archived != task_is_archived_before:
            if task.is_archived:
                # "remove" task from section to update others' indices:
                section.remove_task(task)
            else:
                # unarchiving task => add to section end
                section.insert_task(task)
            await self._section_repo.update(section)
        await self._task_repo.update_or_create(task)
        return convert_to_response(section)

    async def toggle_task_archived(
        self, user_id: UUID, task_id: UUID
    ) -> SectionResponse:
        task = await self._task_repo.get(task_id)
        if task.user_id != user_id:
            raise ForbiddenException()
        section = await self._section_repo.get(task.section_id)
        if not task:
            raise TaskNotFoundException(task_id=task_id)

        task.toggle_archived()

        if task.is_archived:
            # just became archived =>
            # "remove" task from section to update others' indices:
            section.remove_task(task)
        else:
            # unarchiving task => add to section end
            section.insert_task(task)
        await self._section_repo.update(section)
        await self._task_repo.update_or_create(task)
        return convert_to_response(section)

    async def shuffle(
        self, user_id: UUID, request: ShuffleSectionRequest
    ) -> SectionResponse:
        section = await self._section_repo.get(request.section_id)
        if section.user_id != user_id:
            raise ForbiddenException()
        section.shuffle_tasks()
        await self._section_repo.update(section)
        return convert_to_response(section)

    async def create_root_section(self, user_id: UUID) -> Section:
        section = Section.create_root_section(user_id)
        await self._section_repo.add(section, index=0)
        return section
