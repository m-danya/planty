from datetime import date, datetime, timedelta
import random
from typing import Any, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    NonNegativeInt,
    model_validator,
)

from planty.domain.types import RecurrencePeriodType
from planty.utils import generate_uuid, get_datetime_now
from planty.domain.exceptions import RemovingFromWrongSectionError, MovingTaskIndexError


class User(BaseModel):
    id: UUID = Field(default_factory=generate_uuid)
    email: str
    added_at: datetime = Field(default_factory=get_datetime_now)


class RecurrenceInfo(BaseModel):
    period: int
    type: RecurrencePeriodType
    flexible_mode: bool  # like an exclamation mark in Todoist


class Task(BaseModel):
    id: UUID = Field(default_factory=generate_uuid)
    user_id: UUID
    section_id: UUID
    title: str
    description: Optional[str] = None
    content: Optional[str] = None  # Markdown content
    is_completed: bool = False
    # TODO: create documentation and move this comment to it:
    # The archive is mainly for storing completed tasks, but it can also include uncompleted ones
    is_archived: bool = False
    added_at: datetime = Field(default_factory=get_datetime_now)

    due_to: Optional[date] = None
    recurrence: Optional[RecurrenceInfo] = None

    attachments: list["Attachment"] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def check_recurrence_due_date(cls, values: Any) -> Any:
        recurrence = values.get("recurrence")
        due_to = values.get("due_to")
        if recurrence is not None and due_to is None:
            raise ValueError("If recurrence is not None, due_to must also be not None")
        return values

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Task) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def mark_completed(self, auto_archive: bool = True) -> None:
        if self.recurrence is not None:
            assert self.due_to  # only for type checking, it's already validated
            days_delta = timedelta(days=self.recurrence.period)
            if self.recurrence.flexible_mode:
                self.due_to = get_datetime_now().date() + days_delta
            else:
                self.due_to += days_delta
        else:
            self.is_completed = True
            if auto_archive:
                self.archive()

    def toggle_completed(self, auto_archive: bool = True) -> None:
        if self.is_completed:
            self.is_completed = False
        else:
            self.mark_completed(auto_archive=auto_archive)

    def add_attachment(self, attachment: "Attachment") -> None:
        self.attachments.append(attachment)

    def remove_attachment(self, attachment: "Attachment") -> None:
        self.attachments.remove(attachment)

    def archive(self) -> None:
        self.is_archived = True

    def unarchive(self) -> None:
        self.is_archived = False


class Section(BaseModel):
    id: UUID = Field(default_factory=generate_uuid)
    title: str
    parent_id: Optional[UUID] = None
    tasks: list[Task]
    added_at: datetime = Field(default_factory=get_datetime_now)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Section) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def insert_task(self, task: Task, index: Optional[NonNegativeInt] = None) -> None:
        if index is None:
            index = len(self.tasks)
        if index > len(self.tasks):
            raise MovingTaskIndexError()
        task.section_id = self.id
        self.tasks.insert(index, task)

    def remove_task(self, task: Task) -> Task:
        if task.section_id != self.id:
            raise RemovingFromWrongSectionError()
        self.tasks = [t for t in self.tasks if t.id != task.id]
        return task

    @staticmethod
    def move_task(
        task_to_move: Task,
        section_from: "Section",
        section_to: "Section",
        index: NonNegativeInt,
    ) -> None:
        task_to_move = section_from.remove_task(task_to_move)
        section_to.insert_task(task_to_move, index)

    def shuffle_tasks(self) -> None:
        random.shuffle(self.tasks)


class Attachment(BaseModel):
    id: UUID = Field(default_factory=generate_uuid)
    aes_key_b64: str
    aes_iv_b64: str
    s3_file_key: str
    task_id: UUID

    added_at: datetime = Field(default_factory=get_datetime_now)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Attachment) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
