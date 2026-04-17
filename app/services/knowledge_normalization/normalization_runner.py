"""Orchestrate normalization runs and persist ``NormalizedKnowledgeUnit`` rows."""

from __future__ import annotations

import datetime as dt
import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.knowledge_normalization import NormalizationRun, NormalizedKnowledgeUnit
from app.models.models import gen_id
from app.services.knowledge_normalization.legal_normalizer import DraftUnit, build_legal_units
from app.services.knowledge_normalization.normalization_validation import validate_run_payload
from app.services.knowledge_normalization.normalizer_registry import (
    DEFAULT_PROFILE_BY_SOURCE_TYPE,
    PROFILE_LEGAL_HANDBOOK_NORM,
    PROFILE_POLICY_MANUAL_NORM,
)
from app.services.knowledge_normalization.policy_normalizer import PolicyDraftUnit, build_policy_units
from app.services.knowledge_normalization.review_state import REVIEW_SYSTEM_GENERATED
from app.services.knowledge_normalization.source_linking import validate_legal_chunk_link, validate_ingestion_segment_link


def resolve_profile(source_type: str, explicit_profile: str | None) -> str:
    if explicit_profile:
        return explicit_profile
    return DEFAULT_PROFILE_BY_SOURCE_TYPE.get(source_type, PROFILE_POLICY_MANUAL_NORM)


def run_normalization(
    db: Session,
    *,
    source_type: str,
    profile_key: str | None,
    legal_source_version_id: str | None = None,
    ingestion_source_version_id: str | None = None,
    ingestion_source_id: str | None = None,
    legal_document_id: str | None = None,
) -> dict[str, Any]:
    """Execute one normalization run; returns summary dict."""
    profile = resolve_profile(source_type, profile_key)
    started = dt.datetime.utcnow()
    run = NormalizationRun(
        id=gen_id(),
        profile_key=profile,
        source_type=source_type,
        ingestion_source_id=ingestion_source_id,
        ingestion_source_version_id=ingestion_source_version_id,
        legal_document_id=legal_document_id,
        legal_source_version_id=legal_source_version_id,
        validation_status="PENDING",
        unit_count=0,
        failures_json="[]",
        warnings_json="[]",
        meta_json=json.dumps({"started_by": "normalization_runner"}, ensure_ascii=False),
        started_at=started,
        finished_at=None,
    )
    db.add(run)
    db.flush()

    if profile == PROFILE_LEGAL_HANDBOOK_NORM:
        if not legal_source_version_id:
            run.validation_status = "FAIL"
            run.failures_json = json.dumps(["missing_legal_source_version_id"], ensure_ascii=False)
            run.finished_at = dt.datetime.utcnow()
            db.flush()
            return _finalize_run_dict(run, [], orphan_links=0, missing_fields=0, source_ok=False)
        ldid = legal_document_id
        if not ldid:
            from app.models.legal_handbook import LegalSourceVersion

            v = db.get(LegalSourceVersion, legal_source_version_id)
            ldid = v.legal_document_id if v else None
        drafts = build_legal_units(
            db,
            legal_source_version_id=legal_source_version_id,
            legal_document_id=ldid,
            source_type=source_type,
        )
        run.legal_document_id = ldid
        units = _persist_legal_drafts(db, run.id, drafts, legal_source_version_id)
    elif profile == PROFILE_POLICY_MANUAL_NORM:
        if not ingestion_source_version_id or not ingestion_source_id:
            run.validation_status = "FAIL"
            run.failures_json = json.dumps(
                ["missing_ingestion_source_version_id_or_ingestion_source_id"], ensure_ascii=False
            )
            run.finished_at = dt.datetime.utcnow()
            db.flush()
            return _finalize_run_dict(run, [], orphan_links=0, missing_fields=0, source_ok=False)
        pdrafts = build_policy_units(
            db,
            ingestion_source_id=ingestion_source_id,
            ingestion_source_version_id=ingestion_source_version_id,
            source_type=source_type,
        )
        units = _persist_policy_drafts(db, run.id, pdrafts, ingestion_source_version_id)
    else:
        run.validation_status = "FAIL"
        run.failures_json = json.dumps([f"unsupported_profile:{profile}"], ensure_ascii=False)
        run.finished_at = dt.datetime.utcnow()
        db.flush()
        return _finalize_run_dict(run, [], orphan_links=0, missing_fields=0, source_ok=False)

    orphan = _count_orphans(db, units, legal_source_version_id, ingestion_source_version_id)
    missing = _count_missing_optional(units)
    val = validate_run_payload(
        source_resolved=True,
        unit_count=len(units),
        orphan_chunk_links=orphan,
        missing_required_fields=missing,
        profile_key=profile,
    )
    run.validation_status = val.overall
    run.failures_json = json.dumps(val.failures, ensure_ascii=False)
    run.warnings_json = json.dumps(val.warnings, ensure_ascii=False)
    run.unit_count = len(units)
    run.finished_at = dt.datetime.utcnow()
    run.meta_json = json.dumps(
        {**json.loads(run.meta_json or "{}"), "validation_details": val.details},
        ensure_ascii=False,
    )
    db.flush()
    return _finalize_run_dict(run, units, orphan_links=orphan, missing_fields=missing, source_ok=True)


def _persist_legal_drafts(
    db: Session, run_id: str, drafts: list[DraftUnit], legal_source_version_id: str
) -> list[NormalizedKnowledgeUnit]:
    out: list[NormalizedKnowledgeUnit] = []
    for d in drafts:
        ok, _ = validate_legal_chunk_link(
            db, legal_unit_chunk_id=d.legal_unit_chunk_id, legal_source_version_id=legal_source_version_id
        )
        if not ok:
            continue
        row = NormalizedKnowledgeUnit(
            id=gen_id(),
            normalization_run_id=run_id,
            ordinal=d.ordinal,
            normalized_unit_type=d.normalized_unit_type,
            source_type="legal_handbook",
            ingestion_source_id=None,
            ingestion_source_version_id=None,
            ingestion_segment_id=None,
            legal_document_id=d.legal_document_id,
            legal_source_version_id=d.legal_source_version_id,
            legal_unit_id=d.legal_unit_id,
            legal_unit_chunk_id=d.legal_unit_chunk_id,
            title=d.title,
            source_text=d.source_text,
            plain_language_summary=d.plain_language_summary,
            applies_to_role=d.applies_to_role,
            action_type=d.action_type,
            requirement_level=d.requirement_level,
            condition_text=d.condition_text,
            exception_text=d.exception_text,
            escalation_text=d.escalation_text,
            output_outcome_text=d.output_outcome_text,
            citation_keys_json=d.citation_keys_json,
            anchor_json=d.anchor_json,
            structured_facets_json=d.structured_facets_json,
            confidence_level=d.confidence_level,
            review_state=REVIEW_SYSTEM_GENERATED,
            superseded=False,
            superseded_by_unit_id=None,
            retrieval_headline=d.retrieval_headline,
            retrieval_blob=d.retrieval_blob,
            meta_json=d.meta_json,
        )
        db.add(row)
        out.append(row)
    db.flush()
    return out


def _persist_policy_drafts(
    db: Session, run_id: str, drafts: list[PolicyDraftUnit], ingestion_source_version_id: str
) -> list[NormalizedKnowledgeUnit]:
    out: list[NormalizedKnowledgeUnit] = []
    for d in drafts:
        ok, _ = validate_ingestion_segment_link(
            db,
            ingestion_segment_id=d.ingestion_segment_id,
            ingestion_source_version_id=ingestion_source_version_id,
        )
        if not ok:
            continue
        row = NormalizedKnowledgeUnit(
            id=gen_id(),
            normalization_run_id=run_id,
            ordinal=d.ordinal,
            normalized_unit_type=d.normalized_unit_type,
            source_type="policy_manual",
            ingestion_source_id=d.ingestion_source_id,
            ingestion_source_version_id=d.ingestion_source_version_id,
            ingestion_segment_id=d.ingestion_segment_id,
            legal_document_id=None,
            legal_source_version_id=None,
            legal_unit_id=None,
            legal_unit_chunk_id=None,
            title=d.title,
            source_text=d.source_text,
            plain_language_summary=d.plain_language_summary,
            applies_to_role=d.applies_to_role,
            action_type=d.action_type,
            requirement_level=d.requirement_level,
            condition_text=None,
            exception_text=None,
            escalation_text=None,
            output_outcome_text=None,
            citation_keys_json=d.citation_keys_json,
            anchor_json=d.anchor_json,
            structured_facets_json=d.structured_facets_json,
            confidence_level=d.confidence_level,
            review_state=REVIEW_SYSTEM_GENERATED,
            superseded=False,
            superseded_by_unit_id=None,
            retrieval_headline=d.retrieval_headline,
            retrieval_blob=d.retrieval_blob,
            meta_json=d.meta_json,
        )
        db.add(row)
        out.append(row)
    db.flush()
    return out


def _count_orphans(
    db: Session,
    units: list[NormalizedKnowledgeUnit],
    legal_ver: str | None,
    ing_ver: str | None,
) -> int:
    n = 0
    for u in units:
        if u.legal_unit_chunk_id and legal_ver:
            ok, _ = validate_legal_chunk_link(
                db, legal_unit_chunk_id=u.legal_unit_chunk_id, legal_source_version_id=legal_ver
            )
            if not ok:
                n += 1
        if u.ingestion_segment_id and ing_ver:
            ok, _ = validate_ingestion_segment_link(
                db, ingestion_segment_id=u.ingestion_segment_id, ingestion_source_version_id=ing_ver
            )
            if not ok:
                n += 1
    return n


def _count_missing_optional(units: list[NormalizedKnowledgeUnit]) -> int:
    return sum(1 for u in units if not u.plain_language_summary)


def _finalize_run_dict(
    run: NormalizationRun,
    units: list[NormalizedKnowledgeUnit],
    *,
    orphan_links: int,
    missing_fields: int,
    source_ok: bool,
) -> dict[str, Any]:
    return {
        "normalization_run_id": run.id,
        "validation_status": run.validation_status,
        "unit_count": run.unit_count,
        "failures": json.loads(run.failures_json or "[]"),
        "warnings": json.loads(run.warnings_json or "[]"),
        "profile_key": run.profile_key,
        "source_type": run.source_type,
        "orphan_links": orphan_links,
        "missing_summary_fields": missing_fields,
        "source_resolved": source_ok,
    }
