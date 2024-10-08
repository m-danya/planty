from datetime import date
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, NonNegativeInt

from planty.domain.task import RecurrenceInfo, Task
from planty.utils import generate_uuid, get_today

TASK_CREATE_EXAMPLES = [
    {
        "user_id": generate_uuid(),
        "section_id": generate_uuid(),
        "title": "Read something interesting",
        "description": None,
        "due_to_next": str(get_today()),
        "due_to_days_period": 1,
    },
    {
        "user_id": generate_uuid(),
        "section_id": generate_uuid(),
        "title": "Plant waters",
        "description": None,
        "due_to_next": str(get_today()),
        "due_to_days_period": 3,
    },
]


class TaskCreateRequest(BaseModel):
    user_id: UUID
    section_id: UUID
    title: str
    description: Optional[str] = None
    due_to: Optional[date] = None
    recurrence: Optional[RecurrenceInfo] = None

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": TASK_CREATE_EXAMPLES},  # type: ignore
    )


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

    model_config = ConfigDict(
        extra="forbid",
    )


class TaskToggleCompletedResponse(BaseModel):
    is_completed: bool

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
    user_id: UUID = None  #                       type: ignore
    section_id: UUID = None  #                    type: ignore
    title: str = None  #                          type: ignore
    description: Optional[str] = None
    due_to_next: Optional[date] = None
    due_to_days_period: Optional[int] = None

    model_config = ConfigDict(extra="forbid")


class TaskUpdateResponse(BaseModel):
    task: Task


class SectionCreateRequest(BaseModel):
    user_id: UUID
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
