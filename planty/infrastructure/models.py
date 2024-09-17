from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import NonNegativeInt
from sqlalchemy import Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from planty.domain.entities import Section, Task, User
from planty.infrastructure.database import Base
from planty.infrastructure.utils import GUID  # type: ignore


class TaskModel(Base):
    __tablename__ = "task"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, unique=True)
    added_at: Mapped[datetime] = mapped_column(DateTime)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    section_id: Mapped[UUID] = mapped_column(ForeignKey("section.id"))
    title: Mapped[str]
    description: Mapped[Optional[str]]
    is_completed: Mapped[bool]
    index: Mapped[int]

    due_to_next: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    due_to_days_period: Mapped[Optional[int]]

    section = relationship("SectionModel", back_populates="tasks")
    user = relationship("UserModel", back_populates="tasks")

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
            due_to_next=task.due_to_next,
            due_to_days_period=task.due_to_days_period,
            index=index,
        )


# TODO: think about auth domain
class UserModel(Base):
    __tablename__ = "user"
    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, unique=True)
    added_at: Mapped[datetime] = mapped_column(DateTime)
    username: Mapped[str] = mapped_column(unique=True)

    # sections = relationship("SectionModel", back_populates="user")
    tasks = relationship("TaskModel", back_populates="user")

    @classmethod
    def from_entity(cls, user: User) -> "UserModel":
        return cls(
            id=user.id,
            added_at=user.added_at,
            username=str(user.username),
        )


class SectionModel(Base):
    __tablename__ = "section"
    id: Mapped[UUID] = mapped_column(GUID, primary_key=True)
    title: Mapped[str]
    parent_id: Mapped[Optional[GUID]] = mapped_column(
        ForeignKey("section.id"), nullable=True
    )
    added_at: Mapped[datetime] = mapped_column(DateTime)

    tasks = relationship("TaskModel", back_populates="section")

    @classmethod
    def from_entity(cls, section: Section) -> "SectionModel":
        return cls(
            id=section.id,
            title=section.title,
            parent_id=section.parent_id,
            added_at=section.added_at,
        )
