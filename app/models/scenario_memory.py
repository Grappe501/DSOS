"""
Scenario memory and decision trace persistence for Malone (one path).

Stores inspectable, source-grounded snapshots of operational scenarios and
decision/workflow reasoning. Does not replace current evidence.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.models import TimestampMixin, gen_id


class MaloneScenarioMemory(Base, TimestampMixin):
    """User/business situation row linked to a Malone proposal."""

    __tablename__ = "malone_scenario_memories"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    proposal_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("malone_proposals.id"),
        nullable=False,
        index=True,
    )
    actor_user_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    prompt_fingerprint: Mapped[str] = mapped_column(String, nullable=False, index=True)
    scenario_type: Mapped[str] = mapped_column(String, nullable=False, default="unknown", index=True)
    intent_target: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    source_types_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    source_version_snapshot_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    memory_status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="active",
        index=True,
    )
    review_audit_status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="pending",
        index=True,
    )
    delivery_mode: Mapped[str | None] = mapped_column(String, nullable=True)
    delivery_status: Mapped[str | None] = mapped_column(String, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class MaloneDecisionTrace(Base):
    """Serialized reasoning trace for a scenario (1:1 with scenario memory)."""

    __tablename__ = "malone_decision_traces"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    scenario_memory_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("malone_scenario_memories.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    answer_pattern_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    deterministic_legal_mode: Mapped[str] = mapped_column(String, nullable=False, default="unknown")
    decision_workflow_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    source_evidence_map_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    normalized_unit_refs_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    fallback_flags_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    packet_meta_snapshot_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    operating_copilot_snapshot_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_snapshot_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=dt.datetime.utcnow,
        server_default=func.now(),
        index=True,
    )
