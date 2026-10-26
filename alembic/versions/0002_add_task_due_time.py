"""add task due time

Revision ID: 0002_due_time
Revises: 0001_initial
Create Date: 2026-10-26 12:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0002_due_time"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("task", sa.Column("due_time", sa.Time(), nullable=True))


def downgrade() -> None:
    op.drop_column("task", "due_time")
