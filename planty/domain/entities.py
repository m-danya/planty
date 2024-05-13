from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from planty.utils import generate_uuid, get_datetime_now


class User(BaseModel):
    id: UUID = Field(default_factory=generate_uuid)
    username: str  # TODO: replace with Value Object with validation


class Task(BaseModel):
    id: UUID = Field(default_factory=generate_uuid)
    user: User
    # section_id: int
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    added_at: datetime = Field(default_factory=get_datetime_now)
    due_to_next: Optional[date] = None
    due_to_days_period: Optional[int] = None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Task) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def mark_completed(self):
        if self.due_to_days_period:
            self.due_to_next += timedelta(days=self.due_to_days_period)
        else:
            self.is_completed = True

    def update_due_date(
        self, due_to_next: Optional[date], due_to_days_period: Optional[int]
    ):
        self.due_to_next = due_to_next
        self.due_to_days_period = due_to_days_period
