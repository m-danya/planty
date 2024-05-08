from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional

from planty.utils import get_datetime_now


@dataclass(kw_only=True)
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

    def __post_init__(self):
        if not self.is_completed:
            if self.due_to_days_period and not self.due_to_next:
                raise ValueError("Redundant information is given")

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
