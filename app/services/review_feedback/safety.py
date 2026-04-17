"""Safety checks: human feedback must not mutate source evidence text."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.knowledge_normalization import NormalizedKnowledgeUnit
from app.models.scenario_memory import MaloneDecisionTrace


def assert_no_source_text_mutation_fields(meta_patch: dict[str, object] | None) -> None:
    if not meta_patch:
        return
    forbidden = {"source_text", "body_text", "plain_language_summary_override", "rewrite"}
    bad = forbidden & {k.lower() for k in meta_patch}
    if bad:
        raise ValueError(f"meta_json may not silently override source fields: {bad}")


def verify_normalized_unit_exists(db: Session, unit_id: str) -> NormalizedKnowledgeUnit:
    row = db.query(NormalizedKnowledgeUnit).filter(NormalizedKnowledgeUnit.id == unit_id).one_or_none()
    if row is None:
        raise ValueError("normalized_unit not found")
    return row


def verify_decision_trace_exists(db: Session, trace_id: str) -> MaloneDecisionTrace:
    row = db.query(MaloneDecisionTrace).filter(MaloneDecisionTrace.id == trace_id).one_or_none()
    if row is None:
        raise ValueError("decision_trace not found")
    return row
