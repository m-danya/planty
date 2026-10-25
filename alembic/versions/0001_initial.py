"""create the initial Planty schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-25 17:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from fastapi_users_db_sqlalchemy.generics import GUID as UserGUID
from fastapi_users_db_sqlalchemy.generics import TIMESTAMPAware

from alembic import op
from planty.infrastructure.utils import GUID

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("id", UserGUID(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_email", "user", ["email"], unique=True)

    op.create_table(
        "access_token",
        sa.Column("user_id", UserGUID(), nullable=False),
        sa.Column("token", sa.String(length=43), nullable=False),
        sa.Column("created_at", TIMESTAMPAware(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("token"),
    )
    op.create_index(
        "ix_access_token_created_at", "access_token", ["created_at"], unique=False
    )

    op.create_table(
        "section",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("parent_id", GUID(), nullable=True),
        sa.Column("user_id", UserGUID(), nullable=False),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("index", sa.Integer(), nullable=False),
        sa.Column("has_tasks", sa.Boolean(), nullable=False),
        sa.Column("has_subsections", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["section.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "task",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", UserGUID(), nullable=False),
        sa.Column("section_id", GUID(), nullable=False),
        sa.Column("parent_task_id", GUID(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.Column("is_archived", sa.Boolean(), nullable=False),
        sa.Column("index", sa.Integer(), nullable=False),
        sa.Column("due_to", sa.Date(), nullable=True),
        sa.Column("recurrence_period", sa.Integer(), nullable=True),
        sa.Column("recurrence_type", sa.String(), nullable=True),
        sa.Column("flexible_recurrence_mode", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["parent_task_id"], ["task.id"]),
        sa.ForeignKeyConstraint(["section_id"], ["section.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("task")
    op.drop_table("section")
    op.drop_index("ix_access_token_created_at", table_name="access_token")
    op.drop_table("access_token")
    op.drop_index("ix_user_email", table_name="user")
    op.drop_table("user")
