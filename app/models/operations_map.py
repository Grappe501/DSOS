"""
Department intake sessions and structured operations map (org memory, not legal authority).

Intake answers are provisional until reviewed; they do not override source-grounded evidence.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.models import TimestampMixin, gen_id


class OperationsDepartment(Base, TimestampMixin):
    """A department node in the operations map."""

    __tablename__ = "operations_departments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    stable_key: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class DepartmentIntakeSession(Base, TimestampMixin):
    """One interactive intake run; links to proposal/scenario for audit."""

    __tablename__ = "department_intake_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    operations_department_id: Mapped[str] = mapped_column(
        String, ForeignKey("operations_departments.id"), nullable=False, index=True
    )
    actor_user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="open", index=True)
    proposal_id: Mapped[str | None] = mapped_column(String, ForeignKey("malone_proposals.id"), nullable=True, index=True)
    scenario_memory_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("malone_scenario_memories.id"), nullable=True, index=True
    )
    state_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class DepartmentIntakeAnswer(Base):
    """Append-only answer row with optional transcript linkage."""

    __tablename__ = "department_intake_answers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    intake_session_id: Mapped[str] = mapped_column(
        String, ForeignKey("department_intake_sessions.id"), nullable=False, index=True
    )
    question_key: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    prompt_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    entry_mode: Mapped[str] = mapped_column(String, nullable=False, default="text", index=True)
    transcript_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    parser_output_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=dt.datetime.utcnow, server_default=func.now(), index=True
    )


class OperationsRole(Base, TimestampMixin):
    __tablename__ = "operations_roles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    operations_department_id: Mapped[str] = mapped_column(
        String, ForeignKey("operations_departments.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class OperationsWorkflow(Base, TimestampMixin):
    __tablename__ = "operations_workflows"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    operations_department_id: Mapped[str] = mapped_column(
        String, ForeignKey("operations_departments.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_role_id: Mapped[str | None] = mapped_column(String, ForeignKey("operations_roles.id"), nullable=True, index=True)
    inputs_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    outputs_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class OperationsSystemTool(Base, TimestampMixin):
    __tablename__ = "operations_system_tools"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    operations_department_id: Mapped[str] = mapped_column(
        String, ForeignKey("operations_departments.id"), nullable=False, index=True
    )
    operations_workflow_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("operations_workflows.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class OperationsDependency(Base, TimestampMixin):
    __tablename__ = "operations_dependencies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    operations_department_id: Mapped[str] = mapped_column(
        String, ForeignKey("operations_departments.id"), nullable=False, index=True
    )
    from_ref: Mapped[str] = mapped_column(String, nullable=False)
    to_ref: Mapped[str] = mapped_column(String, nullable=False)
    dependency_type: Mapped[str] = mapped_column(String, nullable=False, default="related", index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class OperationsHandoff(Base, TimestampMixin):
    __tablename__ = "operations_handoffs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    operations_department_id: Mapped[str] = mapped_column(
        String, ForeignKey("operations_departments.id"), nullable=False, index=True
    )
    operations_workflow_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("operations_workflows.id"), nullable=True, index=True
    )
    to_counterparty: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class OperationsEscalation(Base, TimestampMixin):
    __tablename__ = "operations_escalations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    operations_department_id: Mapped[str] = mapped_column(
        String, ForeignKey("operations_departments.id"), nullable=False, index=True
    )
    operations_workflow_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("operations_workflows.id"), nullable=True, index=True
    )
    trigger_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    path_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class OperationsBlocker(Base, TimestampMixin):
    __tablename__ = "operations_blockers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    operations_department_id: Mapped[str] = mapped_column(
        String, ForeignKey("operations_departments.id"), nullable=False, index=True
    )
    operations_workflow_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("operations_workflows.id"), nullable=True, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class OperationsArtifactRef(Base, TimestampMixin):
    """SOP / policy / form references mentioned during intake (not file bodies)."""

    __tablename__ = "operations_artifact_refs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    operations_department_id: Mapped[str] = mapped_column(
        String, ForeignKey("operations_departments.id"), nullable=False, index=True
    )
    label: Mapped[str] = mapped_column(String, nullable=False)
    ref_kind: Mapped[str] = mapped_column(String, nullable=False, default="mentioned", index=True)
    meta_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
