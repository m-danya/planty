"""add task parent

Revision ID: a83e12c24f97
Revises: 8c2e68301fff
Create Date: 2026-10-25 12:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from planty.infrastructure.utils import GUID


revision: str = "a83e12c24f97"
down_revision: Union[str, None] = "8c2e68301fff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("task") as batch_op:
        batch_op.add_column(sa.Column("parent_task_id", GUID(), nullable=True))
        batch_op.create_foreign_key(
            "fk_task_parent_task_id", "task", ["parent_task_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("task") as batch_op:
        batch_op.drop_constraint("fk_task_parent_task_id", type_="foreignkey")
        batch_op.drop_column("parent_task_id")
