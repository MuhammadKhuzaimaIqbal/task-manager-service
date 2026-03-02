"""add attachments table and user_id to tasks

Revision ID: 0e2052aafc36
Revises: b2_link_tasks_to_users
Create Date: 2026-03-02 16:20:25.200682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e2052aafc36'
down_revision: Union[str, Sequence[str], None] = 'b2_link_tasks_to_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1️⃣ Add user_id column to tasks
    op.add_column(
        "tasks",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True)
    )

    # 2️⃣ Create attachments table
    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("task_id", sa.Integer, sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table("attachments")
    op.drop_column("tasks", "user_id")