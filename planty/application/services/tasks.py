from datetime import date
from uuid import UUID

import aiobotocore
import aiobotocore.session

from planty.application.exceptions import (
    AttachmentNotFoundException,
    IncorrectDateInterval,
    TaskNotFoundException,
)
from planty.application.schemas import (
    AttachmentUploadInfo,
    RequestAttachmentUpload,
    SectionCreateRequest,
    SectionResponse,
    ShuffleSectionRequest,
    TaskCreateRequest,
    TaskMoveRequest,
    TaskUpdateRequest,
    SectionsListResponse,
)
from planty.application.services.attachments import (
    delete_attachment,
    generate_presigned_post_url,
)
from planty.application.uow import IUnitOfWork
from planty.domain.calendar import multiply_tasks_with_recurrences
from planty.domain.task import Attachment, Section, Task
from planty.config import settings


class TaskService:
    def __init__(self, uow: IUnitOfWork):
        self._task_repo = uow.task_repo
        self._user_repo = uow.user_repo
        self._s3_session = aiobotocore.session.get_session()

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

    async def add_attachment(
        self, request: RequestAttachmentUpload
    ) -> AttachmentUploadInfo:
        task = await self._task_repo.get(request.task_id)
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

    async def remove_attachment(self, task_id: UUID, attachment_id: UUID) -> None:
        task = await self._task_repo.get(task_id)
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

    async def add(self, section_data: SectionCreateRequest) -> Section:
        section = Section(title=section_data.title, parent_id=None, tasks=[])
        await self._section_repo.add(section)
        return section

    async def get_section(self, section_id: UUID) -> SectionResponse:
        section: Section = await self._section_repo.get(section_id)
        return await self._convert_to_response(section)

    async def get_all_sections(self) -> SectionsListResponse:
        sections: list[Section] = await self._section_repo.get_all()
        sections: SectionsListResponse = await self._convert_list_to_response(sections)
        return sections

    async def _convert_to_response(self, section: Section) -> SectionResponse:
        section = section.model_dump()
        for task in section.get("tasks", []):
            for attachment in task.get("attachments", []):
                attachment["url"] = (
                    f"{settings.aws_url}/{settings.aws_attachments_bucket}/{attachment['s3_file_key']}"
                )
        return SectionResponse(**section)

    async def _convert_list_to_response(
        self, sections: list[Section]
    ) -> SectionsListResponse:
        return [await self._convert_to_response(section) for section in sections]

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
