from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID
import uuid

from pydantic import BaseModel, ConfigDict, NonNegativeInt

from planty.domain.task import Attachment, RecurrenceInfo, Task

from fastapi_users import schemas as fastapi_users_schemas


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TaskCreateRequest(Schema):
    section_id: UUID
    title: str
    description: Optional[str] = None
    due_to: Optional[date] = None
    recurrence: Optional[RecurrenceInfo] = None


class TaskCreateResponse(Schema):
    id: UUID


class TaskRemoveRequest(Schema):
    task_id: UUID


class TaskMoveRequest(Schema):
    task_id: UUID
    section_to_id: UUID
    index: NonNegativeInt


class SectionMoveRequest(Schema):
    section_id: UUID
    to_parent_id: UUID
    index: NonNegativeInt


class TaskToggleCompletedRequest(Schema):
    task_id: UUID
    auto_archive: bool = True


class TaskToggleArchivedRequest(Schema):
    task_id: UUID


class ShuffleSectionRequest(Schema):
    section_id: UUID


"""
[!!!]

If pydantic models' field with non-Optional type hinting the has None value by
default, it makes it optional, but user can't set it to None explicitly, which
is very convenient for using it with
`update_request.model_dump(exclude_unset=True)` in SmthUpdateRequest.

Default values are not validated in pydantic, but this hack requires to write
"type: ignore" for each non-optional field's assignment to None to calm down
mypy.
"""


class TaskUpdateRequest(Schema):
    id: UUID
    title: str = None  # type: ignore
    description: Optional[str] = None
    due_to: Optional[date] = None
    recurrence: Optional[RecurrenceInfo] = None


class TaskUpdateResponse(Schema):
    task: "TaskResponse"


class SectionUpdateRequest(Schema):
    id: UUID
    title: str = None  # type: ignore


class SectionUpdateResponse(Schema):
    section: "SectionResponse"


class SectionCreateRequest(Schema):
    title: str
    parent_id: UUID


class SectionCreateResponse(Schema):
    id: UUID


class RequestAttachmentUpload(Schema):
    task_id: UUID
    aes_key_b64: str
    aes_iv_b64: str


class AttachmentUploadInfo(Schema):
    post_url: str
    post_fields: dict[str, Any]


class RequestAttachmentRemove(Schema):
    task_id: UUID
    attachment_id: UUID


class AttachmentResponse(Attachment):
    aes_key_b64: str
    aes_iv_b64: str
    s3_file_key: str
    task_id: UUID
    added_at: datetime

    url: str


class TaskResponse(Schema):
    id: UUID
    section_id: UUID
    title: str
    description: Optional[str]
    content: Optional[str]
    is_completed: bool
    is_archived: bool
    added_at: datetime
    due_to: Optional[date]
    recurrence: Optional[RecurrenceInfo]

    attachments: list[AttachmentResponse]


class SectionResponse(Schema):
    id: UUID
    title: str
    parent_id: Optional[UUID]
    added_at: datetime

    subsections: list["SectionResponse"]
    tasks: list[TaskResponse]


SectionsListResponse = list[SectionResponse]


class TasksByDate(Schema):
    date: date
    tasks: list[Task]


class TasksByDates(Schema):
    by_dates: list[TasksByDate]
    overdue: list[Task]


class TasksByDateResponse(Schema):
    date: date
    tasks: list[TaskResponse]


class TasksByDatesResponse(Schema):
    by_dates: list[TasksByDateResponse]
    overdue: list[TaskResponse]


# TODO: remove if response_converted will be rewritten
class ArchivedTasks(Schema):  # almost like `Section`
    tasks: list[Task]


class ArchivedTasksResponse(Schema):
    title: str = "Archived tasks"
    tasks: list[TaskResponse]


TaskSearchResponse = list[TaskResponse]


class UserRead(fastapi_users_schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(fastapi_users_schemas.BaseUserCreate):
    pass


class UserUpdate(fastapi_users_schemas.BaseUserUpdate):
    pass


class UserStats(Schema):
    id: UUID
    email: str
    tasks_count: int
    sections_count: int
    attachments_count: int
    model_config = ConfigDict(extra="allow")


StatsResponse = list[UserStats]
