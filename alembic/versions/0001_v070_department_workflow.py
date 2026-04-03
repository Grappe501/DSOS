"""v0.7.0 department/workflow migration starter"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_v070_department_workflow"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("code", sa.String(), nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "user_department_memberships",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("department_id", sa.String(), sa.ForeignKey("departments.id"), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("can_approve", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    # TODO: add schedule approval fields and audit before/after fields.
    # TODO: backfill departments from existing users.department and schedules.department.


def downgrade() -> None:
    op.drop_table("user_department_memberships")
    op.drop_table("departments")
