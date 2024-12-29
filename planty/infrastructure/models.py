from datetime import date, datetime
from typing import Optional
from uuid import UUID


from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from pydantic import NonNegativeInt
from sqlalchemy import Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyBaseAccessTokenTableUUID,
)
from planty.domain.task import Attachment, RecurrenceInfo, Section, Task, User
from planty.infrastructure.database import Base
from planty.infrastructure.utils import GUID  # type: ignore
from planty.utils import get_datetime_now


class TaskModel(Base):
    __tablename__ = "task"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, unique=True)
    added_at: Mapped[datetime] = mapped_column(DateTime)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    section_id: Mapped[UUID] = mapped_column(ForeignKey("section.id"))
    title: Mapped[str]
    description: Mapped[Optional[str]]
    is_completed: Mapped[bool]
    is_archived: Mapped[bool]
    index: Mapped[int]  # ignored if `is_archived`

    due_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    recurrence_period: Mapped[Optional[int]]
    recurrence_type: Mapped[Optional[str]]
    flexible_recurrence_mode: Mapped[Optional[bool]]

    section = relationship("SectionModel", back_populates="tasks")
    user = relationship("UserModel", back_populates="tasks")
    attachments = relationship(
        "AttachmentModel",
        back_populates="task",
        order_by="AttachmentModel.index",
    )

    @classmethod
    def from_entity(cls, task: Task, index: NonNegativeInt) -> "TaskModel":
        return cls(
            id=task.id,
            user_id=task.user_id,
            section_id=task.section_id,
            added_at=task.added_at,
            title=task.title,
            description=task.description,
            is_completed=task.is_completed,
            is_archived=task.is_archived,
            due_to=task.due_to,
            recurrence_period=task.recurrence.period if task.recurrence else None,
            recurrence_type=task.recurrence.type if task.recurrence else None,
            flexible_recurrence_mode=(
                task.recurrence.flexible_mode if task.recurrence else None
            ),
            index=index,
        )

    def to_entity(self, attachments: list[Attachment]) -> Task:
        recurrence = (
            RecurrenceInfo(
                period=self.recurrence_period,
                type=self.recurrence_type,
                flexible_mode=self.flexible_recurrence_mode,
            )
            if self.recurrence_period is not None
            else None
        )
        return Task(
            id=self.id,
            user_id=self.user_id,
            section_id=self.section_id,
            title=self.title,
            description=self.description,
            is_completed=self.is_completed,
            is_archived=self.is_archived,
            added_at=self.added_at,
            due_to=self.due_to,
            recurrence=recurrence,
            attachments=attachments,
        )


class UserModel(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user"
    added_at: Mapped[datetime] = mapped_column(DateTime, default=get_datetime_now)

    sections = relationship("SectionModel", back_populates="user")
    tasks = relationship("TaskModel", back_populates="user")

    def to_entity(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            added_at=self.added_at,
        )


class AccessTokenModel(SQLAlchemyBaseAccessTokenTableUUID, Base):
    __tablename__ = "access_token"


class SectionModel(Base):
    __tablename__ = "section"
    id: Mapped[UUID] = mapped_column(GUID, primary_key=True)
    title: Mapped[str]
    parent_id: Mapped[Optional[GUID]] = mapped_column(
        ForeignKey("section.id"), nullable=True
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    added_at: Mapped[datetime] = mapped_column(DateTime)

    index: Mapped[int]  # ordering inside parent

    tasks: Mapped[list[TaskModel]] = relationship(
        "TaskModel",
        back_populates="section",
        order_by="TaskModel.index",
    )
    user = relationship("UserModel", back_populates="sections")

    has_tasks: Mapped[bool]
    has_subsections: Mapped[bool]

    @classmethod
    def from_entity(cls, section: Section, index: NonNegativeInt) -> "SectionModel":
        return cls(
            id=section.id,
            title=section.title,
            user_id=section.user_id,
            parent_id=section.parent_id,
            added_at=section.added_at,
            index=index,
            has_tasks=section.has_tasks,
            has_subsections=section.has_subsections,
        )

    def to_entity(self, tasks: list[Task], subsections: list[Section]) -> Section:
        return Section(
            id=self.id,
            title=self.title,
            user_id=self.user_id,
            parent_id=self.parent_id,
            tasks=tasks,
            subsections=subsections,
            has_tasks=self.has_tasks,
            has_subsections=self.has_subsections,
        )


class AttachmentModel(Base):
    __tablename__ = "attachment"
    id: Mapped[UUID] = mapped_column(GUID, primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime)
    index: Mapped[int]
    task_id: Mapped[UUID] = mapped_column(ForeignKey("task.id"))

    aes_key_b64: Mapped[str]
    aes_iv_b64: Mapped[str]
    s3_file_key: Mapped[str]

    task = relationship("TaskModel", back_populates="attachments")

    @classmethod
    def from_entity(
        cls, attachment: Attachment, index: NonNegativeInt
    ) -> "AttachmentModel":
        return cls(
            id=attachment.id,
            added_at=attachment.added_at,
            index=index,
            task_id=attachment.task_id,
            aes_key_b64=attachment.aes_key_b64,
            aes_iv_b64=attachment.aes_iv_b64,
            s3_file_key=attachment.s3_file_key,
        )

    def to_entity(self) -> Attachment:
        return Attachment(
            id=self.id,
            added_at=self.added_at,
            task_id=self.task_id,
            aes_key_b64=self.aes_key_b64,
            aes_iv_b64=self.aes_iv_b64,
            s3_file_key=self.s3_file_key,
        )
