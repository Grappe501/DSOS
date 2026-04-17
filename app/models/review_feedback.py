"""
Human review loop: append-only feedback events + materialized artifact heads.

Does not store or replace source text; governs trust/review state and audit only.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.models import gen_id


class MaloneReviewFeedbackEvent(Base):
    """Append-only human review / feedback record."""

    __tablename__ = "malone_review_feedback_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    artifact_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    artifact_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    reviewer_user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)

    outcome: Mapped[str] = mapped_column(String, nullable=False, index=True)
    review_state_before: Mapped[str | None] = mapped_column(String, nullable=True)
    review_state_after: Mapped[str | None] = mapped_column(String, nullable=True)

    trust_level: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    risk_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        server_default=func.now(),
        index=True,
    )


class MaloneReviewArtifactHead(Base):
    """Latest review/trust snapshot per artifact (for queues and fast reads)."""

    __tablename__ = "malone_review_artifact_heads"
    __table_args__ = (UniqueConstraint("artifact_type", "artifact_id", name="uq_malone_review_artifact"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    artifact_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    artifact_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    current_review_state: Mapped[str] = mapped_column(String, nullable=False, default="system_generated", index=True)
    current_trust_level: Mapped[str | None] = mapped_column(String, nullable=True)
    last_outcome: Mapped[str | None] = mapped_column(String, nullable=True)
    last_reviewer_user_id: Mapped[str | None] = mapped_column(String, ForeignKey("users.id"), nullable=True)
    last_event_id: Mapped[str | None] = mapped_column(String, nullable=True)

    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
        server_default=func.now(),
    )
