from datetime import date
from typing import Optional

from pydantic import BaseModel

from planty.utils import get_today


class TaskCreateModel(BaseModel):
    user_id: int
    section_id: int
    title: str
    description: Optional[str] = None
    due_to_next: Optional[date] = None
    due_to_days_period: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": 1,
                    "section_id": 1,
                    "title": "Read something interesting",
                    "description": None,
                    "due_to_next": get_today(),
                    "due_to_days_period": 1,
                },
                {
                    "user_id": 1,
                    "section_id": 1,
                    "title": "Plant waters",
                    "description": None,
                    "due_to_next": get_today(),
                    "due_to_days_period": 3,
                },
            ]
        }
    }
