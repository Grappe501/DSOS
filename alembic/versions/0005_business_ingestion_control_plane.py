"""Business-wide ingestion control plane: registry, jobs, tags, validation, promotion, generic segments."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005_business_ingestion_control_plane"
down_revision = "0004_legal_unit_chunk_source_version"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingestion_sources",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("stable_key", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("business_domain", sa.String(), nullable=False, server_default="general"),
        sa.Column("owner_steward", sa.String(), nullable=True),
        sa.Column("authority_tier", sa.String(), nullable=False, server_default="internal"),
        sa.Column("lifecycle_status", sa.String(), nullable=False, server_default="registered"),
        sa.Column("title", sa.String(), nullable=False, server_default=""),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_ingestion_sources_stable_key", "ingestion_sources", ["stable_key"], unique=True)
    op.create_index("idx_ingestion_sources_type", "ingestion_sources", ["source_type"])
    op.create_index("idx_ingestion_sources_lifecycle", "ingestion_sources", ["lifecycle_status"])

    op.create_table(
        "ingestion_source_versions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("ingestion_source_id", sa.String(), sa.ForeignKey("ingestion_sources.id"), nullable=False),
        sa.Column("version_label", sa.String(), nullable=False),
        sa.Column("content_checksum", sa.String(), nullable=True),
        sa.Column("storage_uri", sa.String(), nullable=True),
        sa.Column("parser_profile_key", sa.String(), nullable=False),
        sa.Column("legal_document_id", sa.String(), sa.ForeignKey("legal_documents.id"), nullable=True),
        sa.Column("legal_source_version_id", sa.String(), sa.ForeignKey("legal_source_versions.id"), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("retrieval_ready", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_ingestion_source_versions_source",
        "ingestion_source_versions",
        ["ingestion_source_id"],
    )
    op.create_index(
        "idx_ingestion_source_versions_legal_doc",
        "ingestion_source_versions",
        ["legal_document_id"],
    )
    op.create_index(
        "idx_ingestion_source_versions_legal_ver",
        "ingestion_source_versions",
        ["legal_source_version_id"],
    )

    op.create_table(
        "ingestion_segments",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "ingestion_source_version_id",
            sa.String(),
            sa.ForeignKey("ingestion_source_versions.id"),
            nullable=False,
        ),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("heading", sa.String(), nullable=True),
        sa.Column("body_text", sa.Text(), nullable=False),
        sa.Column("anchor_key", sa.String(), nullable=True),
        sa.Column("retrieval_ready", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_ingestion_segments_version",
        "ingestion_segments",
        ["ingestion_source_version_id"],
    )

    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("ingestion_source_id", sa.String(), sa.ForeignKey("ingestion_sources.id"), nullable=False),
        sa.Column(
            "ingestion_source_version_id",
            sa.String(),
            sa.ForeignKey("ingestion_source_versions.id"),
            nullable=True,
        ),
        sa.Column("parser_profile_key", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("stage", sa.String(), nullable=True),
        sa.Column("overall_validation_status", sa.String(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "linked_legal_ingestion_job_id",
            sa.String(),
            sa.ForeignKey("legal_ingestion_jobs.id"),
            nullable=True,
        ),
        sa.Column("counts_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_ingestion_jobs_source", "ingestion_jobs", ["ingestion_source_id"])
    op.create_index("idx_ingestion_jobs_status", "ingestion_jobs", ["status"])
    op.create_index("idx_ingestion_jobs_linked_legal_job", "ingestion_jobs", ["linked_legal_ingestion_job_id"])

    op.create_table(
        "ingestion_job_events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("ingestion_job_id", sa.String(), sa.ForeignKey("ingestion_jobs.id"), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_ingestion_job_events_job", "ingestion_job_events", ["ingestion_job_id"])

    op.create_table(
        "ingestion_validations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("ingestion_job_id", sa.String(), sa.ForeignKey("ingestion_jobs.id"), nullable=False, unique=True),
        sa.Column("overall_status", sa.String(), nullable=False),
        sa.Column("failures_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("warnings_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("precheck_json", sa.Text(), nullable=True),
        sa.Column("structure_json", sa.Text(), nullable=True),
        sa.Column("db_counts_json", sa.Text(), nullable=True),
        sa.Column("retrieval_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "ingestion_promotions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "ingestion_source_version_id",
            sa.String(),
            sa.ForeignKey("ingestion_source_versions.id"),
            nullable=False,
        ),
        sa.Column("from_status", sa.String(), nullable=False),
        sa.Column("to_status", sa.String(), nullable=False),
        sa.Column("promotion_outcome", sa.String(), nullable=False, server_default="pending"),
        sa.Column("actor", sa.String(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_ingestion_promotions_version",
        "ingestion_promotions",
        ["ingestion_source_version_id"],
    )

    op.create_table(
        "ingestion_tag_definitions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("dimension", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("parent_id", sa.String(), sa.ForeignKey("ingestion_tag_definitions.id"), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "uq_ingestion_tag_definitions_dimension_slug",
        "ingestion_tag_definitions",
        ["dimension", "slug"],
        unique=True,
    )
    op.create_index("idx_ingestion_tag_definitions_dimension", "ingestion_tag_definitions", ["dimension"])

    op.create_table(
        "ingestion_tag_assignments",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tag_definition_id", sa.String(), sa.ForeignKey("ingestion_tag_definitions.id"), nullable=False),
        sa.Column("target_kind", sa.String(), nullable=False),
        sa.Column("target_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_ingestion_tag_assignments_target",
        "ingestion_tag_assignments",
        ["target_kind", "target_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_ingestion_tag_assignments_target", table_name="ingestion_tag_assignments")
    op.drop_table("ingestion_tag_assignments")
    op.drop_index("idx_ingestion_tag_definitions_dimension", table_name="ingestion_tag_definitions")
    op.drop_index("uq_ingestion_tag_definitions_dimension_slug", table_name="ingestion_tag_definitions")
    op.drop_table("ingestion_tag_definitions")
    op.drop_index("idx_ingestion_promotions_version", table_name="ingestion_promotions")
    op.drop_table("ingestion_promotions")
    op.drop_table("ingestion_validations")
    op.drop_index("idx_ingestion_job_events_job", table_name="ingestion_job_events")
    op.drop_table("ingestion_job_events")
    op.drop_index("idx_ingestion_jobs_linked_legal_job", table_name="ingestion_jobs")
    op.drop_index("idx_ingestion_jobs_status", table_name="ingestion_jobs")
    op.drop_index("idx_ingestion_jobs_source", table_name="ingestion_jobs")
    op.drop_table("ingestion_jobs")
    op.drop_index("idx_ingestion_segments_version", table_name="ingestion_segments")
    op.drop_table("ingestion_segments")
    op.drop_index("idx_ingestion_source_versions_legal_ver", table_name="ingestion_source_versions")
    op.drop_index("idx_ingestion_source_versions_legal_doc", table_name="ingestion_source_versions")
    op.drop_index("idx_ingestion_source_versions_source", table_name="ingestion_source_versions")
    op.drop_table("ingestion_source_versions")
    op.drop_index("idx_ingestion_sources_lifecycle", table_name="ingestion_sources")
    op.drop_index("idx_ingestion_sources_type", table_name="ingestion_sources")
    op.drop_index("idx_ingestion_sources_stable_key", table_name="ingestion_sources")
    op.drop_table("ingestion_sources")
