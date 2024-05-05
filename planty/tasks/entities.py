from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from planty.utils import get_datetime_now


@dataclass
class Task:
    id: int
    user_id: int
    section_id: int
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    added_at: datetime = field(default_factory=get_datetime_now)
    due_to_next: Optional[date] = None
    due_to_days_period: Optional[int] = None

    def complete(self):
        if self.due_to_days_period:
            self.due_to_next += self.due_to_days_period
        else:
            self.is_completed = True

    def update_due_date(
        self, due_to_next: Optional[date], due_to_days_period: Optional[int]
    ):
        self.due_to_next = due_to_next
        self.due_to_days_period = due_to_days_period
