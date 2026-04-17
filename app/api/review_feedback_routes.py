"""Narrow human review / governance API (owner/admin writes; authenticated reads where noted)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.services.review_feedback.company_knowledge_promotion import (
    archive_company_ingestion_version,
    list_company_knowledge_source_versions,
    list_website_pack_review_heads,
    promote_ingestion_version_to_active_trusted,
)
from app.services.review_feedback.promotion_signals import ingestion_source_version_promotion_signal
from app.services.review_feedback.review_queries import (
    artifact_types_catalog,
    get_head,
    list_events_for_artifact,
    list_heads,
    summarize_normalized_unit_stub,
    summarize_scenario_stub,
)
from app.services.review_feedback.review_store import submit_review_feedback

router = APIRouter(prefix="/api/malone/review", tags=["malone-review"])


class ReviewFeedbackCreate(BaseModel):
    artifact_type: str = Field(..., min_length=3, max_length=80)
    artifact_id: str = Field(..., min_length=1, max_length=200)
    outcome: str = Field(..., min_length=3, max_length=40)
    notes: str | None = Field(default=None, max_length=16000)
    trust_level: str | None = Field(default=None, max_length=20)
    meta_json: dict | None = None


@router.get("/artifact-types")
def review_artifact_types(current=Depends(get_current_user)):
    _actor, _role = current
    return artifact_types_catalog()


@router.get("/queue")
def review_queue(
    artifact_type: str | None = Query(default=None),
    current_state: str | None = Query(default=None),
    limit: int = Query(default=40, ge=1, le=200),
    db: Session = Depends(get_db),
    _admin=Depends(require_roles("owner", "admin")),
):
    return list_heads(db, artifact_type=artifact_type, current_state=current_state, limit=limit)


@router.get("/head/{artifact_type}/{artifact_id}")
def review_get_head(
    artifact_type: str,
    artifact_id: str,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    _actor, _role = current
    row = get_head(db, artifact_type=artifact_type, artifact_id=artifact_id)
    if not row:
        raise HTTPException(status_code=404, detail="review head not found")
    return row


@router.get("/history/{artifact_type}/{artifact_id}")
def review_history(
    artifact_type: str,
    artifact_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
    _admin=Depends(require_roles("owner", "admin")),
):
    return list_events_for_artifact(db, artifact_type=artifact_type, artifact_id=artifact_id, limit=limit)


@router.post("/feedback")
def review_submit_feedback(
    payload: ReviewFeedbackCreate,
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin")),
):
    actor, _role = current
    try:
        out = submit_review_feedback(
            db,
            artifact_type=payload.artifact_type.strip(),
            artifact_id=payload.artifact_id.strip(),
            outcome=payload.outcome.strip(),
            reviewer_user_id=str(actor.id),
            notes=payload.notes,
            trust_level=payload.trust_level,
            meta_json=payload.meta_json,
        )
        db.commit()
        return out
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/artifact-summary/{artifact_type}/{artifact_id}")
def review_artifact_summary(
    artifact_type: str,
    artifact_id: str,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles("owner", "admin")),
):
    from app.services.review_feedback.artifact_registry import (
        ARTIFACT_DECISION_TRACE,
        ARTIFACT_NORMALIZED_UNIT,
        ARTIFACT_SCENARIO_MEMORY,
    )

    if artifact_type == ARTIFACT_NORMALIZED_UNIT:
        stub = summarize_normalized_unit_stub(db, artifact_id)
        if not stub:
            raise HTTPException(status_code=404, detail="artifact not found")
        return {"artifact_type": artifact_type, "summary": stub, "head": get_head(db, artifact_type=artifact_type, artifact_id=artifact_id)}
    if artifact_type == ARTIFACT_SCENARIO_MEMORY:
        stub = summarize_scenario_stub(db, artifact_id)
        if not stub:
            raise HTTPException(status_code=404, detail="artifact not found")
        return {"artifact_type": artifact_type, "summary": stub, "head": get_head(db, artifact_type=artifact_type, artifact_id=artifact_id)}
    if artifact_type == ARTIFACT_DECISION_TRACE:
        from app.models.scenario_memory import MaloneDecisionTrace

        tr = db.query(MaloneDecisionTrace).filter(MaloneDecisionTrace.id == artifact_id).one_or_none()
        if not tr:
            raise HTTPException(status_code=404, detail="artifact not found")
        return {
            "artifact_type": artifact_type,
            "summary": {"id": tr.id, "scenario_memory_id": tr.scenario_memory_id},
            "head": get_head(db, artifact_type=artifact_type, artifact_id=artifact_id),
        }
    raise HTTPException(status_code=400, detail="summary not implemented for this artifact_type; use inspect APIs")


@router.get("/promotion/ingestion-source-version/{version_id}")
def review_promotion_hint(
    version_id: str,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles("owner", "admin")),
):
    return ingestion_source_version_promotion_signal(db, version_id=version_id)


class CompanyKnowledgePromoteBody(BaseModel):
    ingestion_source_version_id: str = Field(..., min_length=1, max_length=200)
    notes: str | None = Field(default=None, max_length=16000)
    require_prior_approval: bool = True


class CompanyKnowledgeArchiveBody(BaseModel):
    ingestion_source_version_id: str = Field(..., min_length=1, max_length=200)
    notes: str | None = Field(default=None, max_length=16000)
    mark_superseded: bool = False


@router.get("/company-knowledge/candidates")
def company_knowledge_candidates(
    limit: int = Query(default=80, ge=1, le=200),
    db: Session = Depends(get_db),
    _admin=Depends(require_roles("owner", "admin")),
):
    return {"candidates": list_company_knowledge_source_versions(db, limit=limit)}


@router.get("/company-knowledge/website-pack-heads")
def company_knowledge_website_pack_heads(
    limit: int = Query(default=60, ge=1, le=200),
    db: Session = Depends(get_db),
    _admin=Depends(require_roles("owner", "admin")),
):
    return {"website_pack_heads": list_website_pack_review_heads(db, limit=limit)}


@router.post("/company-knowledge/promote-version")
def company_knowledge_promote_version(
    payload: CompanyKnowledgePromoteBody,
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin")),
):
    actor, _role = current
    try:
        out = promote_ingestion_version_to_active_trusted(
            db,
            ingestion_source_version_id=payload.ingestion_source_version_id.strip(),
            reviewer_user_id=str(actor.id),
            notes=payload.notes,
            require_prior_approval=payload.require_prior_approval,
        )
        db.commit()
        return out
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/company-knowledge/archive-version")
def company_knowledge_archive_version(
    payload: CompanyKnowledgeArchiveBody,
    db: Session = Depends(get_db),
    current=Depends(require_roles("owner", "admin")),
):
    actor, _role = current
    try:
        out = archive_company_ingestion_version(
            db,
            ingestion_source_version_id=payload.ingestion_source_version_id.strip(),
            reviewer_user_id=str(actor.id),
            notes=payload.notes,
            mark_superseded=payload.mark_superseded,
        )
        db.commit()
        return out
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
