from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID
import uuid

from pydantic import BaseModel, ConfigDict, NonNegativeInt

from planty.domain.task import Attachment, RecurrenceInfo
from planty.utils import generate_uuid, get_today

from fastapi_users import schemas as fastapi_users_schemas


class TaskCreateRequest(BaseModel):
    section_id: UUID
    title: str
    description: Optional[str] = None
    due_to: Optional[date] = None
    recurrence: Optional[RecurrenceInfo] = None

    model_config = ConfigDict(extra="forbid")


class TaskCreateResponse(BaseModel):
    id: UUID

    model_config = ConfigDict(extra="forbid")


class TaskRemoveRequest(BaseModel):
    task_id: UUID


class TaskMoveRequest(BaseModel):
    task_id: UUID
    section_to_id: UUID
    index: NonNegativeInt

    model_config = ConfigDict(
        extra="forbid",
    )


class TaskToggleCompletedRequest(BaseModel):
    task_id: UUID
    auto_archive: bool = True

    model_config = ConfigDict(
        extra="forbid",
    )


class ShuffleSectionRequest(BaseModel):
    section_id: UUID

    model_config = ConfigDict(
        extra="forbid",
    )


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


class TaskUpdateRequest(BaseModel):
    id: UUID
    section_id: UUID = None  #                    type: ignore
    title: str = None  #                          type: ignore
    description: Optional[str] = None
    due_to_next: Optional[date] = None
    due_to_days_period: Optional[int] = None

    model_config = ConfigDict(extra="forbid")


class TaskUpdateResponse(BaseModel):
    task: "TaskResponse"


class SectionCreateRequest(BaseModel):
    title: str
    parent_id: Optional[UUID] = None

    model_config = ConfigDict(extra="forbid")


class SectionCreateResponse(BaseModel):
    id: UUID


class RequestAttachmentUpload(BaseModel):
    task_id: UUID
    aes_key_b64: str
    aes_iv_b64: str


class AttachmentUploadInfo(BaseModel):
    post_url: str
    post_fields: dict[str, Any]


class RequestAttachmentRemove(BaseModel):
    task_id: UUID
    attachment_id: UUID


class AttachmentResponse(Attachment):
    aes_key_b64: str
    aes_iv_b64: str
    s3_file_key: str
    task_id: UUID
    added_at: datetime

    url: str


class TaskResponse(BaseModel):
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


class SectionResponse(BaseModel):
    id: UUID
    title: str
    parent_id: Optional[UUID]
    added_at: datetime

    tasks: list[TaskResponse]


SectionsListResponse = list[SectionResponse]
TasksByDateResponse = dict[date, list[TaskResponse]]

ArchivedTasksResponse = list[TaskResponse]


class UserRead(fastapi_users_schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(fastapi_users_schemas.BaseUserCreate):
    pass


class UserUpdate(fastapi_users_schemas.BaseUserUpdate):
    pass
