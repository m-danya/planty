from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

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
    due_to_next: Optional[date] = None
    due_to_days_period: Optional[int] = None

    model_config = {"json_schema_extra": {"examples": TASK_CREATE_EXAMPLES}}  # type: ignore
