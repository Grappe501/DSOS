"""Regulation knowledge tables (v0) — handbook ingestion / citations / traces."""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_regulation_knowledge_foundation"
down_revision = "0001_v070_department_workflow"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "regulation_sources",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("stable_key", sa.String(), nullable=False, unique=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("issuing_authority", sa.String(), nullable=True),
        sa.Column("jurisdiction", sa.String(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_regulation_sources_jurisdiction",
        "regulation_sources",
        ["jurisdiction"],
    )

    op.create_table(
        "regulation_source_versions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("source_id", sa.String(), sa.ForeignKey("regulation_sources.id"), nullable=False),
        sa.Column("version_label", sa.String(), nullable=False),
        sa.Column("effective_date", sa.String(), nullable=True),
        sa.Column("superseded_at", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("content_checksum", sa.String(), nullable=True),
        sa.Column("storage_uri", sa.String(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_regulation_source_versions_source",
        "regulation_source_versions",
        ["source_id"],
    )
    op.create_index(
        "idx_regulation_source_versions_status",
        "regulation_source_versions",
        ["status"],
    )

    op.create_table(
        "regulation_chunks",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "source_version_id",
            sa.String(),
            sa.ForeignKey("regulation_source_versions.id"),
            nullable=False,
        ),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("heading_path", sa.String(), nullable=True),
        sa.Column("rule_type", sa.String(), nullable=True),
        sa.Column("plain_summary", sa.Text(), nullable=True),
        sa.Column("body_text", sa.Text(), nullable=False),
        sa.Column("char_start", sa.Integer(), nullable=True),
        sa.Column("char_end", sa.Integer(), nullable=True),
        sa.Column("retrieval_ready", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("embedding_ref", sa.String(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_regulation_chunks_version_ordinal",
        "regulation_chunks",
        ["source_version_id", "ordinal"],
    )

    op.create_table(
        "regulation_citations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("chunk_id", sa.String(), sa.ForeignKey("regulation_chunks.id"), nullable=False),
        sa.Column("citation_key", sa.String(), nullable=False),
        sa.Column("anchor_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "uq_regulation_citations_key",
        "regulation_citations",
        ["citation_key"],
        unique=True,
    )
    op.create_index(
        "idx_regulation_citations_chunk",
        "regulation_citations",
        ["chunk_id"],
    )

    op.create_table(
        "regulation_tags",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False, unique=True),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("parent_id", sa.String(), sa.ForeignKey("regulation_tags.id"), nullable=True),
    )

    op.create_table(
        "regulation_chunk_tags",
        sa.Column("chunk_id", sa.String(), sa.ForeignKey("regulation_chunks.id"), nullable=False),
        sa.Column("tag_id", sa.String(), sa.ForeignKey("regulation_tags.id"), nullable=False),
        sa.PrimaryKeyConstraint("chunk_id", "tag_id"),
    )
    op.create_index(
        "idx_regulation_chunk_tags_tag",
        "regulation_chunk_tags",
        ["tag_id"],
    )

    op.create_table(
        "regulation_ingestion_jobs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "source_version_id",
            sa.String(),
            sa.ForeignKey("regulation_source_versions.id"),
            nullable=True,
        ),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("stage", sa.String(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_regulation_ingestion_jobs_status",
        "regulation_ingestion_jobs",
        ["status"],
    )

    op.create_table(
        "regulation_answer_traces",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("proposal_id", sa.String(), sa.ForeignKey("malone_proposals.id"), nullable=True),
        sa.Column("query_fingerprint", sa.String(), nullable=True),
        sa.Column("chunk_ids_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("model_id", sa.String(), nullable=True),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_regulation_answer_traces_proposal",
        "regulation_answer_traces",
        ["proposal_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_regulation_answer_traces_proposal", table_name="regulation_answer_traces")
    op.drop_table("regulation_answer_traces")

    op.drop_index("idx_regulation_ingestion_jobs_status", table_name="regulation_ingestion_jobs")
    op.drop_table("regulation_ingestion_jobs")

    op.drop_index("idx_regulation_chunk_tags_tag", table_name="regulation_chunk_tags")
    op.drop_table("regulation_chunk_tags")

    op.drop_table("regulation_tags")

    op.drop_index("idx_regulation_citations_chunk", table_name="regulation_citations")
    op.drop_index("uq_regulation_citations_key", table_name="regulation_citations")
    op.drop_table("regulation_citations")

    op.drop_index("idx_regulation_chunks_version_ordinal", table_name="regulation_chunks")
    op.drop_table("regulation_chunks")

    op.drop_index("idx_regulation_source_versions_status", table_name="regulation_source_versions")
    op.drop_index("idx_regulation_source_versions_source", table_name="regulation_source_versions")
    op.drop_table("regulation_source_versions")

    op.drop_index("idx_regulation_sources_jurisdiction", table_name="regulation_sources")
    op.drop_table("regulation_sources")
