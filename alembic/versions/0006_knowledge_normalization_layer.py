"""Knowledge normalization layer: runs, units, review events (above ingestion evidence)."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0006_knowledge_normalization_layer"
down_revision = "0005_business_ingestion_control_plane"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "normalization_runs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("profile_key", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("ingestion_source_id", sa.String(), sa.ForeignKey("ingestion_sources.id"), nullable=True),
        sa.Column(
            "ingestion_source_version_id",
            sa.String(),
            sa.ForeignKey("ingestion_source_versions.id"),
            nullable=True,
        ),
        sa.Column("legal_document_id", sa.String(), sa.ForeignKey("legal_documents.id"), nullable=True),
        sa.Column(
            "legal_source_version_id",
            sa.String(),
            sa.ForeignKey("legal_source_versions.id"),
            nullable=True,
        ),
        sa.Column("validation_status", sa.String(), nullable=False, server_default="PENDING"),
        sa.Column("unit_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failures_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("warnings_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_norm_runs_profile", "normalization_runs", ["profile_key"])
    op.create_index("idx_norm_runs_source_type", "normalization_runs", ["source_type"])
    op.create_index("idx_norm_runs_ing_src", "normalization_runs", ["ingestion_source_id"])
    op.create_index("idx_norm_runs_ing_ver", "normalization_runs", ["ingestion_source_version_id"])
    op.create_index("idx_norm_runs_legal_doc", "normalization_runs", ["legal_document_id"])
    op.create_index("idx_norm_runs_legal_ver", "normalization_runs", ["legal_source_version_id"])
    op.create_index("idx_norm_runs_val", "normalization_runs", ["validation_status"])

    op.create_table(
        "normalized_knowledge_units",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "normalization_run_id",
            sa.String(),
            sa.ForeignKey("normalization_runs.id"),
            nullable=False,
        ),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("normalized_unit_type", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("ingestion_source_id", sa.String(), sa.ForeignKey("ingestion_sources.id"), nullable=True),
        sa.Column(
            "ingestion_source_version_id",
            sa.String(),
            sa.ForeignKey("ingestion_source_versions.id"),
            nullable=True,
        ),
        sa.Column(
            "ingestion_segment_id",
            sa.String(),
            sa.ForeignKey("ingestion_segments.id"),
            nullable=True,
        ),
        sa.Column("legal_document_id", sa.String(), sa.ForeignKey("legal_documents.id"), nullable=True),
        sa.Column(
            "legal_source_version_id",
            sa.String(),
            sa.ForeignKey("legal_source_versions.id"),
            nullable=True,
        ),
        sa.Column("legal_unit_id", sa.String(), sa.ForeignKey("legal_units.id"), nullable=True),
        sa.Column("legal_unit_chunk_id", sa.String(), sa.ForeignKey("legal_unit_chunks.id"), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("source_text", sa.Text(), nullable=False),
        sa.Column("plain_language_summary", sa.Text(), nullable=True),
        sa.Column("applies_to_role", sa.String(), nullable=True),
        sa.Column("action_type", sa.String(), nullable=True),
        sa.Column("requirement_level", sa.String(), nullable=True),
        sa.Column("condition_text", sa.Text(), nullable=True),
        sa.Column("exception_text", sa.Text(), nullable=True),
        sa.Column("escalation_text", sa.Text(), nullable=True),
        sa.Column("output_outcome_text", sa.Text(), nullable=True),
        sa.Column("citation_keys_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("anchor_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("structured_facets_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("confidence_level", sa.String(), nullable=False, server_default="medium"),
        sa.Column("review_state", sa.String(), nullable=False, server_default="system_generated"),
        sa.Column("superseded", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column(
            "superseded_by_unit_id",
            sa.String(),
            sa.ForeignKey("normalized_knowledge_units.id"),
            nullable=True,
        ),
        sa.Column("retrieval_headline", sa.String(), nullable=True),
        sa.Column("retrieval_blob", sa.Text(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("normalization_run_id", "ordinal", name="uq_norm_knowledge_run_ordinal"),
    )
    op.create_index("idx_nku_run", "normalized_knowledge_units", ["normalization_run_id"])
    op.create_index("idx_nku_type", "normalized_knowledge_units", ["normalized_unit_type"])
    op.create_index("idx_nku_stype", "normalized_knowledge_units", ["source_type"])
    op.create_index("idx_nku_ing_ver", "normalized_knowledge_units", ["ingestion_source_version_id"])
    op.create_index("idx_nku_legal_ver", "normalized_knowledge_units", ["legal_source_version_id"])
    op.create_index("idx_nku_chunk", "normalized_knowledge_units", ["legal_unit_chunk_id"])
    op.create_index("idx_nku_seg", "normalized_knowledge_units", ["ingestion_segment_id"])
    op.create_index("idx_nku_role", "normalized_knowledge_units", ["applies_to_role"])
    op.create_index("idx_nku_conf", "normalized_knowledge_units", ["confidence_level"])
    op.create_index("idx_nku_review", "normalized_knowledge_units", ["review_state"])
    op.create_index("idx_nku_super", "normalized_knowledge_units", ["superseded"])

    op.create_table(
        "normalized_knowledge_review_events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "normalized_knowledge_unit_id",
            sa.String(),
            sa.ForeignKey("normalized_knowledge_units.id"),
            nullable=False,
        ),
        sa.Column("from_state", sa.String(), nullable=True),
        sa.Column("to_state", sa.String(), nullable=False),
        sa.Column("actor", sa.String(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_nkrev_unit", "normalized_knowledge_review_events", ["normalized_knowledge_unit_id"])


def downgrade() -> None:
    op.drop_table("normalized_knowledge_review_events")
    op.drop_table("normalized_knowledge_units")
    op.drop_table("normalization_runs")
