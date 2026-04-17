"""Malone scenario memory + decision trace (audit / comparison support)."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0007_scenario_memory_decision_trace"
down_revision = "0006_knowledge_normalization_layer"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "malone_scenario_memories",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("proposal_id", sa.String(), sa.ForeignKey("malone_proposals.id"), nullable=False),
        sa.Column("actor_user_id", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("prompt_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("prompt_fingerprint", sa.String(), nullable=False),
        sa.Column("scenario_type", sa.String(), nullable=False, server_default="unknown"),
        sa.Column("intent_target", sa.String(), nullable=True),
        sa.Column("source_types_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("source_version_snapshot_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("memory_status", sa.String(), nullable=False, server_default="active"),
        sa.Column("review_audit_status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("delivery_mode", sa.String(), nullable=True),
        sa.Column("delivery_status", sa.String(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_malone_scenario_memories_proposal_id", "malone_scenario_memories", ["proposal_id"])
    op.create_index("ix_malone_scenario_memories_prompt_fingerprint", "malone_scenario_memories", ["prompt_fingerprint"])
    op.create_index("ix_malone_scenario_memories_scenario_type", "malone_scenario_memories", ["scenario_type"])
    op.create_index("ix_malone_scenario_memories_intent_target", "malone_scenario_memories", ["intent_target"])
    op.create_index("ix_malone_scenario_memories_memory_status", "malone_scenario_memories", ["memory_status"])
    op.create_index("ix_malone_scenario_memories_review_audit_status", "malone_scenario_memories", ["review_audit_status"])

    op.create_table(
        "malone_decision_traces",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("scenario_memory_id", sa.String(), sa.ForeignKey("malone_scenario_memories.id"), nullable=False),
        sa.Column("answer_pattern_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("deterministic_legal_mode", sa.String(), nullable=False, server_default="unknown"),
        sa.Column("decision_workflow_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("source_evidence_map_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("normalized_unit_refs_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("fallback_flags_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("packet_meta_snapshot_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("operating_copilot_snapshot_json", sa.Text(), nullable=True),
        sa.Column("verification_snapshot_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_malone_decision_traces_scenario_memory_id",
        "malone_decision_traces",
        ["scenario_memory_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_malone_decision_traces_scenario_memory_id", table_name="malone_decision_traces")
    op.drop_table("malone_decision_traces")
    op.drop_index("ix_malone_scenario_memories_review_audit_status", table_name="malone_scenario_memories")
    op.drop_index("ix_malone_scenario_memories_memory_status", table_name="malone_scenario_memories")
    op.drop_index("ix_malone_scenario_memories_intent_target", table_name="malone_scenario_memories")
    op.drop_index("ix_malone_scenario_memories_scenario_type", table_name="malone_scenario_memories")
    op.drop_index("ix_malone_scenario_memories_prompt_fingerprint", table_name="malone_scenario_memories")
    op.drop_index("ix_malone_scenario_memories_proposal_id", table_name="malone_scenario_memories")
    op.drop_table("malone_scenario_memories")
