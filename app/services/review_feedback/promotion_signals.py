"""Promotion readiness from review state (advisory; does not replace validation gates)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.ingestion_control import IngestionSourceVersion
from app.services.review_feedback.review_queries import get_head

from app.services.review_feedback.artifact_registry import ARTIFACT_INGESTION_SOURCE_VERSION


def ingestion_source_version_promotion_signal(db: Session, *, version_id: str) -> dict[str, object]:
    v = db.query(IngestionSourceVersion).filter(IngestionSourceVersion.id == version_id).one_or_none()
    head = get_head(db, artifact_type=ARTIFACT_INGESTION_SOURCE_VERSION, artifact_id=version_id)
    st = (head.get("current_review_state") or "").strip().lower() if head else ""
    # "validated" corresponds to ready_for_promotion / staging without activation.
    approved_like = st in ("approved", "validated")
    ready = bool(head and st == "approved")
    return {
        "ingestion_source_version_id": version_id,
        "retrieval_ready_db": bool(v.retrieval_ready) if v else False,
        "review_head_approved": ready,
        "review_head_staging": approved_like and st == "validated",
        "promotion_hint": "approved_for_promotion" if ready else ("staging" if approved_like else "needs_review_or_validation"),
    }
