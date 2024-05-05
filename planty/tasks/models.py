from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from planty.database import Base


def get_datetime_now():
    return datetime.now(timezone.utc)


def get_today():
    return datetime.now(timezone.utc).date()


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_datetime_now)
    username: Mapped[str] = mapped_column(unique=True)


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=get_datetime_now)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    section_id: Mapped[int] = mapped_column(ForeignKey("section.id"))
    title: Mapped[str]
    description: Mapped[Optional[str]]
    is_completed: Mapped[bool]

    due_to_next: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    due_to_days_period: Mapped[Optional[int]]


class Section(Base):
    __tablename__ = "section"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_section_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("section.id"), nullable=True
    )
    title: Mapped[str]
    parent_section = relationship("Section", remote_side=[id], backref="subsections")
