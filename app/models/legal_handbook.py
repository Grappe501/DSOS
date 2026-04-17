"""
SQLAlchemy models for legal handbook persistence (Alembic 0003).

Purpose:
    Mirror `schemas/legal_handbook_knowledge_v0.sql` so `Base.metadata.create_all`
    can provision tables in dev and ORM code can write the Arkansas vertical slice.

Role in Malone:
    `legal_unit_chunks` + `legal_citations` are the evidence spine for future
    truth-packet attachments; not consumed by Malone chat until explicitly wired.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.models import gen_id


class LegalDocument(Base):
    __tablename__ = "legal_documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    stable_key: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String, nullable=True)
    storage_uri: Mapped[str | None] = mapped_column(String, nullable=True)
    content_checksum: Mapped[str | None] = mapped_column(String, nullable=True)
    compiled_edition_label: Mapped[str | None] = mapped_column(String, nullable=True)
    cover_metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    status: Mapped[str] = mapped_column(String, nullable=False, default="registered", index=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
        server_default=func.now(),
    )


class LegalSourceVersion(Base):
    __tablename__ = "legal_source_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    legal_document_id: Mapped[str] = mapped_column(String, ForeignKey("legal_documents.id"), nullable=False, index=True)
    version_label: Mapped[str] = mapped_column(String, nullable=False)
    compiled_publication_date: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft", index=True)
    content_checksum: Mapped[str | None] = mapped_column(String, nullable=True)
    storage_uri: Mapped[str | None] = mapped_column(String, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
        server_default=func.now(),
    )


class LegalDocumentFamily(Base):
    __tablename__ = "legal_document_families"
    __table_args__ = (
        UniqueConstraint("legal_document_id", "family_code", name="uq_legal_document_families_doc_code"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    legal_document_id: Mapped[str] = mapped_column(String, ForeignKey("legal_documents.id"), nullable=False, index=True)
    family_code: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    toc_page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    toc_page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedded_source_revision_label: Mapped[str | None] = mapped_column(String, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
        server_default=func.now(),
    )


class LegalUnit(Base):
    __tablename__ = "legal_units"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    legal_document_family_id: Mapped[str] = mapped_column(
        String, ForeignKey("legal_document_families.id"), nullable=False, index=True
    )
    parent_legal_unit_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("legal_units.id"), nullable=True, index=True
    )
    unit_kind: Mapped[str] = mapped_column(String, nullable=False, index=True)
    primary_citation: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    heading_raw: Mapped[str | None] = mapped_column(String, nullable=True)
    toc_path: Mapped[str | None] = mapped_column(String, nullable=True)
    subsection_path: Mapped[str | None] = mapped_column(String, nullable=True)
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
        server_default=func.now(),
    )


class LegalUnitChunk(Base):
    __tablename__ = "legal_unit_chunks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    legal_unit_id: Mapped[str] = mapped_column(String, ForeignKey("legal_units.id"), nullable=False, index=True)
    legal_source_version_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("legal_source_versions.id"), nullable=True, index=True
    )
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    subsection_path: Mapped[str | None] = mapped_column(String, nullable=True)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    char_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    char_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    retrieval_ready: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    embedding_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
        server_default=func.now(),
    )


class LegalCitation(Base):
    __tablename__ = "legal_citations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    legal_unit_chunk_id: Mapped[str] = mapped_column(
        String, ForeignKey("legal_unit_chunks.id"), nullable=False, index=True
    )
    citation_key: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    citation_kind: Mapped[str | None] = mapped_column(String, nullable=True)
    normalized_citation: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    authority_type: Mapped[str | None] = mapped_column(String, nullable=True)
    anchor_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )


class LegalCrossReference(Base):
    __tablename__ = "legal_cross_references"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    from_legal_unit_chunk_id: Mapped[str] = mapped_column(
        String, ForeignKey("legal_unit_chunks.id"), nullable=False, index=True
    )
    raw_reference_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    to_citation_key: Mapped[str | None] = mapped_column(String, nullable=True)
    to_legal_unit_id: Mapped[str | None] = mapped_column(String, ForeignKey("legal_units.id"), nullable=True, index=True)
    resolution_status: Mapped[str] = mapped_column(String, nullable=False, default="unresolved", index=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )


class LegalDateLayer(Base):
    __tablename__ = "legal_date_layers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    scope_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    scope_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    layer_kind: Mapped[str] = mapped_column(String, nullable=False)
    raw_label: Mapped[str | None] = mapped_column(String, nullable=True)
    iso_date: Mapped[str | None] = mapped_column(String, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )


class LegalTag(Base):
    __tablename__ = "legal_tags"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    label: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[str | None] = mapped_column(String, ForeignKey("legal_tags.id"), nullable=True)


class LegalChunkTag(Base):
    __tablename__ = "legal_chunk_tags"

    chunk_id: Mapped[str] = mapped_column(String, ForeignKey("legal_unit_chunks.id"), primary_key=True)
    tag_id: Mapped[str] = mapped_column(String, ForeignKey("legal_tags.id"), primary_key=True)


class LegalIngestionJob(Base):
    __tablename__ = "legal_ingestion_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    legal_document_id: Mapped[str | None] = mapped_column(String, ForeignKey("legal_documents.id"), nullable=True)
    legal_source_version_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("legal_source_versions.id"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String, nullable=False, index=True)
    stage: Mapped[str | None] = mapped_column(String, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
        server_default=func.now(),
    )


class LegalAnswerTrace(Base):
    __tablename__ = "legal_answer_traces"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    proposal_id: Mapped[str | None] = mapped_column(String, ForeignKey("malone_proposals.id"), nullable=True, index=True)
    query_fingerprint: Mapped[str | None] = mapped_column(String, nullable=True)
    chunk_ids_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    citation_keys_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    model_id: Mapped[str | None] = mapped_column(String, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )
