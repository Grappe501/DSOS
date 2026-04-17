"""
ORM models for business-wide ingestion control plane (Alembic 0005).

Sits alongside legal handbook tables: optional FKs link handbook ingests to
``legal_documents`` / ``legal_source_versions`` without replacing them.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.models import gen_id


class IngestionSource(Base):
    __tablename__ = "ingestion_sources"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    stable_key: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    business_domain: Mapped[str] = mapped_column(String, nullable=False, default="general")
    owner_steward: Mapped[str | None] = mapped_column(String, nullable=True)
    authority_tier: Mapped[str] = mapped_column(String, nullable=False, default="internal", index=True)
    lifecycle_status: Mapped[str] = mapped_column(String, nullable=False, default="registered", index=True)
    title: Mapped[str] = mapped_column(String, nullable=False, default="")
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


class IngestionSourceVersion(Base):
    __tablename__ = "ingestion_source_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    ingestion_source_id: Mapped[str] = mapped_column(String, ForeignKey("ingestion_sources.id"), nullable=False, index=True)
    version_label: Mapped[str] = mapped_column(String, nullable=False)
    content_checksum: Mapped[str | None] = mapped_column(String, nullable=True)
    storage_uri: Mapped[str | None] = mapped_column(String, nullable=True)
    parser_profile_key: Mapped[str] = mapped_column(String, nullable=False, index=True)
    legal_document_id: Mapped[str | None] = mapped_column(String, ForeignKey("legal_documents.id"), nullable=True, index=True)
    legal_source_version_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("legal_source_versions.id"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft", index=True)
    retrieval_ready: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
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


class IngestionSegment(Base):
    """Generic text segments for non-legal profiles (policy, SOP, etc.)."""

    __tablename__ = "ingestion_segments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    ingestion_source_version_id: Mapped[str] = mapped_column(
        String, ForeignKey("ingestion_source_versions.id"), nullable=False, index=True
    )
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    heading: Mapped[str | None] = mapped_column(String, nullable=True)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    anchor_key: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    retrieval_ready: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
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


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    ingestion_source_id: Mapped[str] = mapped_column(String, ForeignKey("ingestion_sources.id"), nullable=False, index=True)
    ingestion_source_version_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("ingestion_source_versions.id"), nullable=True, index=True
    )
    parser_profile_key: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending", index=True)
    stage: Mapped[str | None] = mapped_column(String, nullable=True)
    overall_validation_status: Mapped[str | None] = mapped_column(String, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    linked_legal_ingestion_job_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("legal_ingestion_jobs.id"), nullable=True, index=True
    )
    counts_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
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


class IngestionJobEvent(Base):
    __tablename__ = "ingestion_job_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    ingestion_job_id: Mapped[str] = mapped_column(String, ForeignKey("ingestion_jobs.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )


class IngestionValidation(Base):
    __tablename__ = "ingestion_validations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    ingestion_job_id: Mapped[str] = mapped_column(String, ForeignKey("ingestion_jobs.id"), nullable=False, unique=True)
    overall_status: Mapped[str] = mapped_column(String, nullable=False)
    failures_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    warnings_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    precheck_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    structure_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    db_counts_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    retrieval_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )


class IngestionPromotion(Base):
    __tablename__ = "ingestion_promotions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    ingestion_source_version_id: Mapped[str] = mapped_column(
        String, ForeignKey("ingestion_source_versions.id"), nullable=False, index=True
    )
    from_status: Mapped[str] = mapped_column(String, nullable=False)
    to_status: Mapped[str] = mapped_column(String, nullable=False)
    promotion_outcome: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    actor: Mapped[str | None] = mapped_column(String, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )


class IngestionTagDefinition(Base):
    __tablename__ = "ingestion_tag_definitions"
    __table_args__ = (UniqueConstraint("dimension", "slug", name="uq_ingestion_tag_definitions_dimension_slug"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    dimension: Mapped[str] = mapped_column(String, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[str | None] = mapped_column(String, ForeignKey("ingestion_tag_definitions.id"), nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )


class IngestionTagAssignment(Base):
    __tablename__ = "ingestion_tag_assignments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    tag_definition_id: Mapped[str] = mapped_column(String, ForeignKey("ingestion_tag_definitions.id"), nullable=False)
    target_kind: Mapped[str] = mapped_column(String, nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )
