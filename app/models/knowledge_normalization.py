"""
ORM models for the knowledge normalization layer (Alembic 0006).

Sits above raw ingestion (legal chunks, ingestion segments) without replacing evidence rows.
Each normalized unit retains source linkage and optional governance / review state.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.models import gen_id


class NormalizationRun(Base):
    """One execution of a normalization profile against a resolved source version."""

    __tablename__ = "normalization_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    profile_key: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    ingestion_source_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("ingestion_sources.id"), nullable=True, index=True
    )
    ingestion_source_version_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("ingestion_source_versions.id"), nullable=True, index=True
    )
    legal_document_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("legal_documents.id"), nullable=True, index=True
    )
    legal_source_version_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("legal_source_versions.id"), nullable=True, index=True
    )
    validation_status: Mapped[str] = mapped_column(String, nullable=False, default="PENDING", index=True)
    unit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failures_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    warnings_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )


class NormalizedKnowledgeUnit(Base):
    """Structured knowledge derived from ingested segments/chunks; auditable and reviewable."""

    __tablename__ = "normalized_knowledge_units"
    __table_args__ = (UniqueConstraint("normalization_run_id", "ordinal", name="uq_norm_knowledge_run_ordinal"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    normalization_run_id: Mapped[str] = mapped_column(
        String, ForeignKey("normalization_runs.id"), nullable=False, index=True
    )
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)

    normalized_unit_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False, index=True)

    ingestion_source_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("ingestion_sources.id"), nullable=True, index=True
    )
    ingestion_source_version_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("ingestion_source_versions.id"), nullable=True, index=True
    )
    ingestion_segment_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("ingestion_segments.id"), nullable=True, index=True
    )
    legal_document_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("legal_documents.id"), nullable=True, index=True
    )
    legal_source_version_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("legal_source_versions.id"), nullable=True, index=True
    )
    legal_unit_id: Mapped[str | None] = mapped_column(String, ForeignKey("legal_units.id"), nullable=True, index=True)
    legal_unit_chunk_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("legal_unit_chunks.id"), nullable=True, index=True
    )

    title: Mapped[str | None] = mapped_column(String, nullable=True)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    plain_language_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    applies_to_role: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    action_type: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    requirement_level: Mapped[str | None] = mapped_column(String, nullable=True, index=True)

    condition_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    exception_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    escalation_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_outcome_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    citation_keys_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    anchor_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    structured_facets_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    confidence_level: Mapped[str] = mapped_column(String, nullable=False, default="medium", index=True)
    review_state: Mapped[str] = mapped_column(String, nullable=False, default="system_generated", index=True)
    superseded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    superseded_by_unit_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("normalized_knowledge_units.id"), nullable=True
    )

    retrieval_headline: Mapped[str | None] = mapped_column(String, nullable=True)
    retrieval_blob: Mapped[str | None] = mapped_column(Text, nullable=True)

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


class NormalizedKnowledgeReviewEvent(Base):
    """Audit trail for review_state transitions (governance)."""

    __tablename__ = "normalized_knowledge_review_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    normalized_knowledge_unit_id: Mapped[str] = mapped_column(
        String, ForeignKey("normalized_knowledge_units.id"), nullable=False, index=True
    )
    from_state: Mapped[str | None] = mapped_column(String, nullable=True)
    to_state: Mapped[str] = mapped_column(String, nullable=False)
    actor: Mapped[str | None] = mapped_column(String, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now()
    )
