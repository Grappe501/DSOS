"""Company-knowledge review queue and guarded promotion on the ingestion control plane."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.ingestion_control import IngestionSource, IngestionSourceVersion
from app.services.ingestion_control.promotion import archive_source_version, promote_source_version
from app.services.review_feedback.artifact_registry import ARTIFACT_INGESTION_SOURCE_VERSION, ARTIFACT_WEBSITE_PACK_ENTRY
from app.services.review_feedback.company_knowledge_states import STATE_ACTIVE, STATE_ARCHIVED, STATE_SUPERSEDED
from app.services.review_feedback.promotion_signals import ingestion_source_version_promotion_signal
from app.services.review_feedback.review_queries import get_head, list_heads
from app.services.review_feedback.review_store import submit_review_feedback
from app.services.review_feedback.review_status import OUTCOME_INFORMATIONAL, OUTCOME_REJECTED

# Internal / company-facing source types (not legal handbook rows).
DEFAULT_COMPANY_SOURCE_TYPES = frozenset(
    {
        "policy_manual",
        "sop_workflow",
        "company_profile",
        "training_module",
        "form_template",
        "general_reference",
        "compliance_notice",
        "meeting_memory",
    }
)


def list_company_knowledge_source_versions(
    db: Session,
    *,
    source_types: frozenset[str] | None = None,
    only_authority_internal: bool = True,
    limit: int = 80,
) -> list[dict[str, Any]]:
    """Rows suitable for human review: ingestion source + version + review head + promotion hint."""
    st = source_types or DEFAULT_COMPANY_SOURCE_TYPES
    q = (
        db.query(IngestionSourceVersion, IngestionSource)
        .join(IngestionSource, IngestionSource.id == IngestionSourceVersion.ingestion_source_id)
        .filter(IngestionSource.source_type.in_(tuple(st)))
    )
    if only_authority_internal:
        q = q.filter(IngestionSource.authority_tier == "internal")
    rows = q.order_by(IngestionSourceVersion.updated_at.desc()).limit(min(max(limit, 1), 200)).all()
    out: list[dict[str, Any]] = []
    for ver, src in rows:
        head = get_head(db, artifact_type=ARTIFACT_INGESTION_SOURCE_VERSION, artifact_id=ver.id)
        sig = ingestion_source_version_promotion_signal(db, version_id=ver.id)
        out.append(
            {
                "ingestion_source_version_id": ver.id,
                "ingestion_source_id": src.id,
                "stable_key": src.stable_key,
                "source_type": src.source_type,
                "business_domain": src.business_domain,
                "version_label": ver.version_label,
                "version_status": ver.status,
                "retrieval_ready": ver.retrieval_ready,
                "source_lifecycle": src.lifecycle_status,
                "review_head": head,
                "promotion_signal": sig,
            }
        )
    return out


def list_website_pack_review_heads(db: Session, *, limit: int = 60) -> list[dict[str, Any]]:
    """Website pack lines are manifest-backed; review state lives in artifact heads + events only."""
    return list_heads(db, artifact_type=ARTIFACT_WEBSITE_PACK_ENTRY, limit=limit)


def promote_ingestion_version_to_active_trusted(
    db: Session,
    *,
    ingestion_source_version_id: str,
    reviewer_user_id: str,
    notes: str | None = None,
    require_prior_approval: bool = True,
) -> dict[str, Any]:
    """
    Apply ingestion promotion (retrieval_ready, promoted_active) after human approval.

    Does not alter segment text or citations; updates governance + operational readiness only.
    """
    head = get_head(db, artifact_type=ARTIFACT_INGESTION_SOURCE_VERSION, artifact_id=ingestion_source_version_id)
    if require_prior_approval:
        st = (head or {}).get("current_review_state") or ""
        if str(st).lower() != "approved":
            raise ValueError("ingestion_source_version must be human-approved before activation promotion")

    prom, ver = promote_source_version(
        db,
        ingestion_source_version_id=ingestion_source_version_id,
        to_status="promoted_active",
        actor=reviewer_user_id,
        reason=notes,
        meta={
            "company_knowledge_lifecycle": STATE_ACTIVE,
            "promotion_channel": "company_knowledge_review",
        },
    )
    return {
        "ingestion_promotion_id": prom.id,
        "ingestion_source_version_id": ver.id,
        "to_status": ver.status,
        "retrieval_ready": ver.retrieval_ready,
    }


def archive_company_ingestion_version(
    db: Session,
    *,
    ingestion_source_version_id: str,
    reviewer_user_id: str,
    notes: str | None = None,
    mark_superseded: bool = False,
) -> dict[str, Any]:
    """Archive version (retrieval off) and record a governance event (audit trail)."""
    prom, ver = archive_source_version(
        db,
        ingestion_source_version_id=ingestion_source_version_id,
        actor=reviewer_user_id,
        reason=notes,
    )
    meta: dict[str, Any] = {"post_archive_ack": True}
    if mark_superseded:
        meta["supersession"] = True
        meta["company_knowledge_lifecycle"] = STATE_SUPERSEDED
    else:
        meta["company_knowledge_lifecycle"] = STATE_ARCHIVED
    submit_review_feedback(
        db,
        artifact_type=ARTIFACT_INGESTION_SOURCE_VERSION,
        artifact_id=ingestion_source_version_id,
        outcome=OUTCOME_INFORMATIONAL,
        reviewer_user_id=reviewer_user_id,
        notes=notes or ("superseded" if mark_superseded else "archived"),
        meta_json=meta,
    )
    return {
        "ingestion_promotion_id": prom.id,
        "ingestion_source_version_id": ver.id,
        "version_status": ver.status,
        "company_knowledge_lifecycle": meta.get("company_knowledge_lifecycle"),
    }
