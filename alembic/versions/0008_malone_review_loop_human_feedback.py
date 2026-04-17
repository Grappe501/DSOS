"""Malone human review loop: feedback events + artifact heads."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0008_malone_review_loop_human_feedback"
down_revision = "0007_scenario_memory_decision_trace"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "malone_review_feedback_events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("artifact_type", sa.String(), nullable=False),
        sa.Column("artifact_id", sa.String(), nullable=False),
        sa.Column("reviewer_user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("outcome", sa.String(), nullable=False),
        sa.Column("review_state_before", sa.String(), nullable=True),
        sa.Column("review_state_after", sa.String(), nullable=True),
        sa.Column("trust_level", sa.String(), nullable=True),
        sa.Column("risk_flag", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_malone_review_feedback_events_artifact_type", "malone_review_feedback_events", ["artifact_type"])
    op.create_index("ix_malone_review_feedback_events_artifact_id", "malone_review_feedback_events", ["artifact_id"])
    op.create_index(
        "ix_malone_review_feedback_events_artifact_pair",
        "malone_review_feedback_events",
        ["artifact_type", "artifact_id"],
    )
    op.create_index("ix_malone_review_feedback_events_reviewer", "malone_review_feedback_events", ["reviewer_user_id"])
    op.create_index("ix_malone_review_feedback_events_outcome", "malone_review_feedback_events", ["outcome"])
    op.create_index("ix_malone_review_feedback_events_created", "malone_review_feedback_events", ["created_at"])

    op.create_table(
        "malone_review_artifact_heads",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("artifact_type", sa.String(), nullable=False),
        sa.Column("artifact_id", sa.String(), nullable=False),
        sa.Column("current_review_state", sa.String(), nullable=False, server_default="system_generated"),
        sa.Column("current_trust_level", sa.String(), nullable=True),
        sa.Column("last_outcome", sa.String(), nullable=True),
        sa.Column("last_reviewer_user_id", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("last_event_id", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("artifact_type", "artifact_id", name="uq_malone_review_artifact"),
    )
    op.create_index("ix_malone_review_heads_type", "malone_review_artifact_heads", ["artifact_type"])
    op.create_index("ix_malone_review_heads_state", "malone_review_artifact_heads", ["current_review_state"])


def downgrade() -> None:
    op.drop_index("ix_malone_review_heads_state", table_name="malone_review_artifact_heads")
    op.drop_index("ix_malone_review_heads_type", table_name="malone_review_artifact_heads")
    op.drop_table("malone_review_artifact_heads")
    op.drop_index("ix_malone_review_feedback_events_created", table_name="malone_review_feedback_events")
    op.drop_index("ix_malone_review_feedback_events_outcome", table_name="malone_review_feedback_events")
    op.drop_index("ix_malone_review_feedback_events_reviewer", table_name="malone_review_feedback_events")
    op.drop_index("ix_malone_review_feedback_events_artifact_pair", table_name="malone_review_feedback_events")
    op.drop_index("ix_malone_review_feedback_events_artifact_id", table_name="malone_review_feedback_events")
    op.drop_index("ix_malone_review_feedback_events_artifact_type", table_name="malone_review_feedback_events")
    op.drop_table("malone_review_feedback_events")
