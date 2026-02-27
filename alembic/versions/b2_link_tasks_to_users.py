"""Link tasks to users

Revision ID: b2_link_tasks_to_users
Revises: b1_add_users
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2_link_tasks_to_users"
down_revision: Union[str, Sequence[str], None] = "b1_add_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    op.create_index(op.f("ix_tasks_user_id"), "tasks", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tasks_user_id"), table_name="tasks")
    op.drop_column("tasks", "user_id")

