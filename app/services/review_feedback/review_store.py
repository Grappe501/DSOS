"""Create review events, update artifact heads, sync governed columns (no source rewrites)."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.ingestion_control import IngestionSourceVersion
from app.models.knowledge_normalization import NormalizedKnowledgeUnit
from app.models.models import gen_id
from app.models.review_feedback import MaloneReviewArtifactHead, MaloneReviewFeedbackEvent
from app.models.scenario_memory import MaloneDecisionTrace, MaloneScenarioMemory
from app.services.review_feedback.artifact_registry import (
    ARTIFACT_DECISION_TRACE,
    ARTIFACT_INGESTION_SOURCE_VERSION,
    ARTIFACT_NORMALIZED_UNIT,
    ARTIFACT_OPERATING_COPILOT,
    ARTIFACT_SCENARIO_MEMORY,
    ARTIFACT_WEBSITE_PACK_ENTRY,
    assert_known_artifact,
)
from app.services.review_feedback.company_knowledge_states import lifecycle_from_review_outcome
from app.services.review_feedback.review_status import (
    OUTCOME_APPROVED,
    OUTCOME_HOLD_FOR_REVIEW,
    OUTCOME_INFORMATIONAL,
    OUTCOME_NEEDS_REVISION,
    OUTCOME_READY_FOR_PROMOTION,
    OUTCOME_REJECTED,
    OUTCOME_RISK_FLAG,
    OUTCOMES,
    head_state_from_normalized,
    head_state_from_scenario_audit,
    map_outcome_to_normalized_review_state,
    map_outcome_to_scenario_audit_status,
    merge_human_review_meta,
)
from app.services.review_feedback.safety import (
    assert_no_source_text_mutation_fields,
    verify_decision_trace_exists,
    verify_normalized_unit_exists,
)


def _get_or_create_head(
    db: Session,
    *,
    artifact_type: str,
    artifact_id: str,
) -> MaloneReviewArtifactHead:
    row = (
        db.query(MaloneReviewArtifactHead)
        .filter(
            MaloneReviewArtifactHead.artifact_type == artifact_type,
            MaloneReviewArtifactHead.artifact_id == artifact_id,
        )
        .one_or_none()
    )
    if row:
        return row
    row = MaloneReviewArtifactHead(
        id=gen_id(),
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        current_review_state="system_generated",
    )
    db.add(row)
    db.flush()
    return row


def _resolve_initial_head_state(db: Session, *, artifact_type: str, artifact_id: str) -> str:
    if artifact_type == ARTIFACT_NORMALIZED_UNIT:
        u = verify_normalized_unit_exists(db, artifact_id)
        return head_state_from_normalized(u.review_state)
    if artifact_type in (ARTIFACT_SCENARIO_MEMORY, ARTIFACT_OPERATING_COPILOT):
        sm = db.query(MaloneScenarioMemory).filter(MaloneScenarioMemory.id == artifact_id).one_or_none()
        if sm is None:
            raise ValueError("scenario_memory not found")
        return head_state_from_scenario_audit(sm.review_audit_status)
    if artifact_type == ARTIFACT_DECISION_TRACE:
        tr = verify_decision_trace_exists(db, artifact_id)
        meta = json.loads(tr.meta_json) if tr.meta_json else {}
        hr = meta.get("human_review") if isinstance(meta.get("human_review"), dict) else {}
        return str(hr.get("review_state") or "system_generated")
    if artifact_type == ARTIFACT_INGESTION_SOURCE_VERSION:
        v = db.query(IngestionSourceVersion).filter(IngestionSourceVersion.id == artifact_id).one_or_none()
        if v is None:
            raise ValueError("ingestion_source_version not found")
        meta = json.loads(v.meta_json) if v.meta_json else {}
        hr = meta.get("human_review") if isinstance(meta.get("human_review"), dict) else {}
        return str(hr.get("review_state") or str(v.status or "draft"))
    if artifact_type == ARTIFACT_WEBSITE_PACK_ENTRY:
        return "system_generated"
    raise ValueError(f"unsupported artifact_type: {artifact_type}")


def _build_review_patch(
    *,
    outcome: str,
    event_id: str,
    reviewer_id: str,
    trust_level: str | None,
    notes: str | None,
    meta_patch: dict[str, Any] | None,
) -> dict[str, Any]:
    patch: dict[str, Any] = {
        "last_outcome": outcome,
        "last_event_id": event_id,
        "reviewer_user_id": reviewer_id,
    }
    if trust_level:
        patch["trust_level"] = trust_level
    if notes:
        patch["notes"] = notes[:8000]
    if meta_patch:
        patch["extra"] = meta_patch
    return patch


def _sync_domain_object(
    db: Session,
    *,
    artifact_type: str,
    artifact_id: str,
    outcome: str,
    head_state_value: str,
    trust_level: str | None,
    meta_patch: dict[str, Any] | None,
    notes: str | None,
    reviewer_id: str,
    event_id: str,
) -> None:
    assert_no_source_text_mutation_fields(meta_patch)
    patch = _build_review_patch(
        outcome=outcome,
        event_id=event_id,
        reviewer_id=reviewer_id,
        trust_level=trust_level,
        notes=notes,
        meta_patch=meta_patch,
    )

    if artifact_type == ARTIFACT_NORMALIZED_UNIT:
        u = verify_normalized_unit_exists(db, artifact_id)
        mapped = map_outcome_to_normalized_review_state(outcome, prior=u.review_state)
        if mapped:
            u.review_state = mapped
        if trust_level in ("high", "medium", "low"):
            u.confidence_level = trust_level
        return

    if artifact_type == ARTIFACT_SCENARIO_MEMORY:
        sm = db.query(MaloneScenarioMemory).filter(MaloneScenarioMemory.id == artifact_id).one_or_none()
        if sm is None:
            raise ValueError("scenario_memory not found")
        audit = map_outcome_to_scenario_audit_status(outcome, prior=sm.review_audit_status)
        if audit:
            sm.review_audit_status = audit
        patch["review_state"] = head_state_value
        sm.meta_json = merge_human_review_meta(sm.meta_json, patch)
        return

    if artifact_type == ARTIFACT_OPERATING_COPILOT:
        sm = db.query(MaloneScenarioMemory).filter(MaloneScenarioMemory.id == artifact_id).one_or_none()
        if sm is None:
            raise ValueError("scenario_memory not found")
        audit = map_outcome_to_scenario_audit_status(outcome, prior=sm.review_audit_status)
        if audit:
            sm.review_audit_status = audit
        patch["review_state"] = head_state_value
        patch["operating_copilot_review"] = True
        sm.meta_json = merge_human_review_meta(sm.meta_json, patch)
        return

    if artifact_type == ARTIFACT_DECISION_TRACE:
        tr = verify_decision_trace_exists(db, artifact_id)
        patch["review_state"] = head_state_value
        tr.meta_json = merge_human_review_meta(tr.meta_json, patch)
        return

    if artifact_type == ARTIFACT_INGESTION_SOURCE_VERSION:
        v = db.query(IngestionSourceVersion).filter(IngestionSourceVersion.id == artifact_id).one_or_none()
        if v is None:
            raise ValueError("ingestion_source_version not found")
        patch["review_state"] = head_state_value
        patch["promotion_ready"] = outcome in (OUTCOME_APPROVED, OUTCOME_READY_FOR_PROMOTION)
        patch["company_knowledge_lifecycle"] = lifecycle_from_review_outcome(outcome)
        v.meta_json = merge_human_review_meta(v.meta_json, patch)
        return

    if artifact_type == ARTIFACT_WEBSITE_PACK_ENTRY:
        # Events + heads only; manifest stays external.
        return


def submit_review_feedback(
    db: Session,
    *,
    artifact_type: str,
    artifact_id: str,
    outcome: str,
    reviewer_user_id: str,
    notes: str | None = None,
    trust_level: str | None = None,
    meta_json: dict[str, Any] | None = None,
) -> dict[str, Any]:
    assert_known_artifact(artifact_type)
    o = (outcome or "").strip().lower()
    if o not in OUTCOMES:
        raise ValueError(f"invalid outcome: {outcome}")

    state_before = _resolve_initial_head_state(db, artifact_type=artifact_type, artifact_id=artifact_id)

    head_state_value = state_before
    if artifact_type == ARTIFACT_NORMALIZED_UNIT:
        u = verify_normalized_unit_exists(db, artifact_id)
        mapped = map_outcome_to_normalized_review_state(o, prior=u.review_state)
        if mapped:
            head_state_value = mapped
    elif artifact_type in (ARTIFACT_SCENARIO_MEMORY, ARTIFACT_OPERATING_COPILOT):
        sm = db.query(MaloneScenarioMemory).filter(MaloneScenarioMemory.id == artifact_id).one_or_none()
        if sm is None:
            raise ValueError("scenario_memory not found")
        audit = map_outcome_to_scenario_audit_status(o, prior=sm.review_audit_status)
        if audit:
            head_state_value = audit
    elif artifact_type == ARTIFACT_DECISION_TRACE:
        head_state_value = {
            OUTCOME_INFORMATIONAL: "reviewed",
            OUTCOME_APPROVED: "approved",
            OUTCOME_REJECTED: "rejected",
            OUTCOME_NEEDS_REVISION: "needs_revision",
            OUTCOME_RISK_FLAG: "under_review",
            OUTCOME_READY_FOR_PROMOTION: "validated",
            OUTCOME_HOLD_FOR_REVIEW: "under_review",
        }.get(o, "reviewed")
    elif artifact_type == ARTIFACT_INGESTION_SOURCE_VERSION:
        v = db.query(IngestionSourceVersion).filter(IngestionSourceVersion.id == artifact_id).one_or_none()
        if v is None:
            raise ValueError("ingestion_source_version not found")
        if o == OUTCOME_APPROVED:
            head_state_value = "approved"
        elif o == OUTCOME_REJECTED:
            head_state_value = "rejected"
        elif o == OUTCOME_NEEDS_REVISION:
            head_state_value = "needs_revision"
        elif o == OUTCOME_READY_FOR_PROMOTION:
            head_state_value = "validated"
        elif o == OUTCOME_HOLD_FOR_REVIEW:
            head_state_value = "under_review"
        elif o == OUTCOME_INFORMATIONAL:
            head_state_value = "reviewed"
        elif o == OUTCOME_RISK_FLAG:
            head_state_value = "under_review"
        else:
            head_state_value = v.status or "draft"
    elif artifact_type == ARTIFACT_WEBSITE_PACK_ENTRY:
        head_state_value = {
            OUTCOME_APPROVED: "approved",
            OUTCOME_REJECTED: "rejected",
            OUTCOME_NEEDS_REVISION: "needs_revision",
            OUTCOME_INFORMATIONAL: "reviewed",
            OUTCOME_RISK_FLAG: "under_review",
            OUTCOME_READY_FOR_PROMOTION: "ready_for_promotion",
            OUTCOME_HOLD_FOR_REVIEW: "under_review",
        }.get(o, state_before)

    event = MaloneReviewFeedbackEvent(
        id=gen_id(),
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        reviewer_user_id=reviewer_user_id,
        outcome=o,
        review_state_before=state_before,
        review_state_after=head_state_value,
        trust_level=trust_level,
        risk_flag=o == OUTCOME_RISK_FLAG,
        notes=notes,
        meta_json=json.dumps(meta_json or {}, ensure_ascii=False, default=str),
    )
    db.add(event)
    db.flush()

    _sync_domain_object(
        db,
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        outcome=o,
        head_state_value=head_state_value,
        trust_level=trust_level,
        meta_patch=meta_json,
        notes=notes,
        reviewer_id=reviewer_user_id,
        event_id=event.id,
    )

    head = _get_or_create_head(db, artifact_type=artifact_type, artifact_id=artifact_id)
    head.current_review_state = head_state_value
    head.current_trust_level = trust_level
    head.last_outcome = o
    head.last_reviewer_user_id = reviewer_user_id
    head.last_event_id = event.id

    db.flush()
    return {"event_id": event.id, "artifact_type": artifact_type, "artifact_id": artifact_id}
