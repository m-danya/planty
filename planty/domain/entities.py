from datetime import date, datetime, timedelta
import random
from typing import Annotated, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    NonNegativeInt,
    RootModel,
    field_validator,
)

from planty.utils import generate_uuid, get_datetime_now
from planty.domain.exceptions import MovingTaskIndexError

UsernameType = Annotated[str, Field(min_length=3, max_length=50)]


class Username(RootModel[UsernameType]):
    root: UsernameType

    @field_validator("root")
    def validate_username(cls, s: str) -> str:
        for c in s:
            if not (c.isalnum() or c == "_"):
                raise ValueError(f"Symbol '{c}' is not allowed in username")
        return s

    def __str__(self) -> str:
        return str(self.root)

    model_config = ConfigDict(frozen=True)


class User(BaseModel):
    id: UUID = Field(default_factory=generate_uuid)
    username: Username
    added_at: datetime = Field(default_factory=get_datetime_now)


class Task(BaseModel):
    id: UUID = Field(default_factory=generate_uuid)
    user_id: UUID
    section_id: UUID
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    added_at: datetime = Field(default_factory=get_datetime_now)
    due_to_next: Optional[date] = None
    due_to_days_period: Optional[int] = None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Task) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def mark_completed(self) -> None:
        if self.due_to_days_period:
            assert self.due_to_next
            self.due_to_next += timedelta(days=self.due_to_days_period)
        else:
            self.is_completed = True

    def toggle_completed(self) -> None:
        if self.is_completed:
            self.is_completed = False
        else:
            self.mark_completed()

    def update_due_date(
        self, due_to_next: Optional[date], due_to_days_period: Optional[int]
    ) -> None:
        self.due_to_next = due_to_next
        self.due_to_days_period = due_to_days_period


class Section(BaseModel):
    id: UUID = Field(default_factory=generate_uuid)
    title: str
    parent_id: Optional[UUID] = None
    tasks: list[Task]
    added_at: datetime = Field(default_factory=get_datetime_now)

    def insert_task(self, task: Task, index: Optional[NonNegativeInt] = None):
        if index is None:
            index = len(self.tasks)
        if index > len(self.tasks):
            raise MovingTaskIndexError()
        task.section_id = self.id
        self.tasks.insert(index, task)

    def remove_task(self, task: Task) -> Task:
        self.tasks = [t for t in self.tasks if t.id != task.id]
        return task

    @staticmethod
    def move_task(
        task_to_move: Task,
        section_from: "Section",
        section_to: "Section",
        index: NonNegativeInt,
    ):
        task_to_move = section_from.remove_task(task_to_move)
        section_to.insert_task(task_to_move, index)

    def shuffle_tasks(self):
        random.shuffle(self.tasks)
