"""Legal handbook knowledge tables (v0) — families, units, citations, cross-refs, date layers."""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_legal_handbook_knowledge_foundation"
down_revision = "0002_regulation_knowledge_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "legal_documents",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("stable_key", sa.String(), nullable=False, unique=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("original_filename", sa.String(), nullable=True),
        sa.Column("storage_uri", sa.String(), nullable=True),
        sa.Column("content_checksum", sa.String(), nullable=True),
        sa.Column("compiled_edition_label", sa.String(), nullable=True),
        sa.Column("cover_metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(), nullable=False, server_default="registered"),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_legal_documents_status", "legal_documents", ["status"])

    op.create_table(
        "legal_source_versions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("legal_document_id", sa.String(), sa.ForeignKey("legal_documents.id"), nullable=False),
        sa.Column("version_label", sa.String(), nullable=False),
        sa.Column("compiled_publication_date", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("content_checksum", sa.String(), nullable=True),
        sa.Column("storage_uri", sa.String(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_legal_source_versions_document",
        "legal_source_versions",
        ["legal_document_id"],
    )

    op.create_table(
        "legal_document_families",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("legal_document_id", sa.String(), sa.ForeignKey("legal_documents.id"), nullable=False),
        sa.Column("family_code", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("toc_page_start", sa.Integer(), nullable=True),
        sa.Column("toc_page_end", sa.Integer(), nullable=True),
        sa.Column("embedded_source_revision_label", sa.String(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "uq_legal_document_families_doc_code",
        "legal_document_families",
        ["legal_document_id", "family_code"],
        unique=True,
    )

    op.create_table(
        "legal_units",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "legal_document_family_id",
            sa.String(),
            sa.ForeignKey("legal_document_families.id"),
            nullable=False,
        ),
        sa.Column("parent_legal_unit_id", sa.String(), sa.ForeignKey("legal_units.id"), nullable=True),
        sa.Column("unit_kind", sa.String(), nullable=False),
        sa.Column("primary_citation", sa.String(), nullable=True),
        sa.Column("heading_raw", sa.String(), nullable=True),
        sa.Column("toc_path", sa.String(), nullable=True),
        sa.Column("subsection_path", sa.String(), nullable=True),
        sa.Column("page_start", sa.Integer(), nullable=True),
        sa.Column("page_end", sa.Integer(), nullable=True),
        sa.Column("ordinal", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("body_text", sa.Text(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_legal_units_family",
        "legal_units",
        ["legal_document_family_id"],
    )
    op.create_index(
        "idx_legal_units_parent",
        "legal_units",
        ["parent_legal_unit_id"],
    )
    op.create_index("idx_legal_units_citation", "legal_units", ["primary_citation"])

    op.create_table(
        "legal_unit_chunks",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("legal_unit_id", sa.String(), sa.ForeignKey("legal_units.id"), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("subsection_path", sa.String(), nullable=True),
        sa.Column("body_text", sa.Text(), nullable=False),
        sa.Column("char_start", sa.Integer(), nullable=True),
        sa.Column("char_end", sa.Integer(), nullable=True),
        sa.Column("page_start", sa.Integer(), nullable=True),
        sa.Column("page_end", sa.Integer(), nullable=True),
        sa.Column("retrieval_ready", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("embedding_ref", sa.String(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_legal_unit_chunks_unit_ord",
        "legal_unit_chunks",
        ["legal_unit_id", "ordinal"],
    )

    op.create_table(
        "legal_citations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "legal_unit_chunk_id",
            sa.String(),
            sa.ForeignKey("legal_unit_chunks.id"),
            nullable=False,
        ),
        sa.Column("citation_key", sa.String(), nullable=False),
        sa.Column("citation_kind", sa.String(), nullable=True),
        sa.Column("normalized_citation", sa.String(), nullable=True),
        sa.Column("authority_type", sa.String(), nullable=True),
        sa.Column("anchor_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "uq_legal_citations_key",
        "legal_citations",
        ["citation_key"],
        unique=True,
    )
    op.create_index(
        "idx_legal_citations_chunk",
        "legal_citations",
        ["legal_unit_chunk_id"],
    )

    op.create_table(
        "legal_cross_references",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "from_legal_unit_chunk_id",
            sa.String(),
            sa.ForeignKey("legal_unit_chunks.id"),
            nullable=False,
        ),
        sa.Column("raw_reference_text", sa.Text(), nullable=True),
        sa.Column("to_citation_key", sa.String(), nullable=True),
        sa.Column("to_legal_unit_id", sa.String(), sa.ForeignKey("legal_units.id"), nullable=True),
        sa.Column("resolution_status", sa.String(), nullable=False, server_default="unresolved"),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_legal_xref_from",
        "legal_cross_references",
        ["from_legal_unit_chunk_id"],
    )
    op.create_index(
        "idx_legal_xref_to_unit",
        "legal_cross_references",
        ["to_legal_unit_id"],
    )

    op.create_table(
        "legal_date_layers",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("scope_type", sa.String(), nullable=False),
        sa.Column("scope_id", sa.String(), nullable=False),
        sa.Column("layer_kind", sa.String(), nullable=False),
        sa.Column("raw_label", sa.String(), nullable=True),
        sa.Column("iso_date", sa.String(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_legal_date_layers_scope",
        "legal_date_layers",
        ["scope_type", "scope_id"],
    )

    op.create_table(
        "legal_tags",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False, unique=True),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("parent_id", sa.String(), sa.ForeignKey("legal_tags.id"), nullable=True),
    )

    op.create_table(
        "legal_chunk_tags",
        sa.Column("chunk_id", sa.String(), sa.ForeignKey("legal_unit_chunks.id"), nullable=False),
        sa.Column("tag_id", sa.String(), sa.ForeignKey("legal_tags.id"), nullable=False),
        sa.PrimaryKeyConstraint("chunk_id", "tag_id"),
    )
    op.create_index("idx_legal_chunk_tags_tag", "legal_chunk_tags", ["tag_id"])

    op.create_table(
        "legal_ingestion_jobs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("legal_document_id", sa.String(), sa.ForeignKey("legal_documents.id"), nullable=True),
        sa.Column(
            "legal_source_version_id",
            sa.String(),
            sa.ForeignKey("legal_source_versions.id"),
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
        "idx_legal_ingestion_jobs_status",
        "legal_ingestion_jobs",
        ["status"],
    )

    op.create_table(
        "legal_answer_traces",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("proposal_id", sa.String(), sa.ForeignKey("malone_proposals.id"), nullable=True),
        sa.Column("query_fingerprint", sa.String(), nullable=True),
        sa.Column("chunk_ids_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("citation_keys_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("model_id", sa.String(), nullable=True),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "idx_legal_answer_traces_proposal",
        "legal_answer_traces",
        ["proposal_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_legal_answer_traces_proposal", table_name="legal_answer_traces")
    op.drop_table("legal_answer_traces")

    op.drop_index("idx_legal_ingestion_jobs_status", table_name="legal_ingestion_jobs")
    op.drop_table("legal_ingestion_jobs")

    op.drop_index("idx_legal_chunk_tags_tag", table_name="legal_chunk_tags")
    op.drop_table("legal_chunk_tags")

    op.drop_table("legal_tags")

    op.drop_index("idx_legal_date_layers_scope", table_name="legal_date_layers")
    op.drop_table("legal_date_layers")

    op.drop_index("idx_legal_xref_to_unit", table_name="legal_cross_references")
    op.drop_index("idx_legal_xref_from", table_name="legal_cross_references")
    op.drop_table("legal_cross_references")

    op.drop_index("idx_legal_citations_chunk", table_name="legal_citations")
    op.drop_index("uq_legal_citations_key", table_name="legal_citations")
    op.drop_table("legal_citations")

    op.drop_index("idx_legal_unit_chunks_unit_ord", table_name="legal_unit_chunks")
    op.drop_table("legal_unit_chunks")

    op.drop_index("idx_legal_units_citation", table_name="legal_units")
    op.drop_index("idx_legal_units_parent", table_name="legal_units")
    op.drop_index("idx_legal_units_family", table_name="legal_units")
    op.drop_table("legal_units")

    op.drop_index("uq_legal_document_families_doc_code", table_name="legal_document_families")
    op.drop_table("legal_document_families")

    op.drop_index("idx_legal_source_versions_document", table_name="legal_source_versions")
    op.drop_table("legal_source_versions")

    op.drop_index("idx_legal_documents_status", table_name="legal_documents")
    op.drop_table("legal_documents")
