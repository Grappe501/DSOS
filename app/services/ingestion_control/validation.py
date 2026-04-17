"""
Structured validation for business ingest jobs.

Reuses Arkansas PASS / PASS_WITH_WARNINGS / FAIL semantics from
``ingest_validate_status.decide_overall_status``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ingestion_control import IngestionValidation
from app.models.legal_handbook import LegalCitation, LegalDocumentFamily, LegalUnit, LegalUnitChunk
from app.models.models import gen_id
from app.services.legal_ingestion.ingest_validate_status import decide_overall_status


@dataclass
class ValidationPayload:
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    precheck: dict[str, Any] = field(default_factory=dict)
    structure: dict[str, Any] = field(default_factory=dict)
    db_counts: dict[str, Any] = field(default_factory=dict)
    retrieval: dict[str, Any] = field(default_factory=dict)

    def overall(self) -> str:
        return decide_overall_status(self.failures, self.warnings)


def persist_validation(
    db: Session,
    *,
    ingestion_job_id: str,
    payload: ValidationPayload,
) -> IngestionValidation:
    row = (
        db.query(IngestionValidation).filter(IngestionValidation.ingestion_job_id == ingestion_job_id).one_or_none()
    )
    overall = payload.overall()
    body = {
        "overall_status": overall,
        "failures_json": json.dumps(payload.failures, ensure_ascii=False),
        "warnings_json": json.dumps(payload.warnings, ensure_ascii=False),
        "precheck_json": json.dumps(payload.precheck, ensure_ascii=False) if payload.precheck else None,
        "structure_json": json.dumps(payload.structure, ensure_ascii=False) if payload.structure else None,
        "db_counts_json": json.dumps(payload.db_counts, ensure_ascii=False) if payload.db_counts else None,
        "retrieval_json": json.dumps(payload.retrieval, ensure_ascii=False) if payload.retrieval else None,
    }
    if row is None:
        row = IngestionValidation(
            id=gen_id(),
            ingestion_job_id=ingestion_job_id,
            overall_status=overall,
            **{k: v for k, v in body.items() if k != "overall_status"},
        )
        db.add(row)
    else:
        row.overall_status = overall
        row.failures_json = body["failures_json"]
        row.warnings_json = body["warnings_json"]
        row.precheck_json = body["precheck_json"]
        row.structure_json = body["structure_json"]
        row.db_counts_json = body["db_counts_json"]
        row.retrieval_json = body["retrieval_json"]
    db.flush()
    return row


def legal_version_counts(
    db: Session,
    *,
    legal_source_version_id: str,
) -> dict[str, int]:
    family_count = int(
        db.execute(
            select(func.count(func.distinct(LegalDocumentFamily.id)))
            .select_from(LegalUnitChunk)
            .join(LegalUnit, LegalUnitChunk.legal_unit_id == LegalUnit.id)
            .join(LegalDocumentFamily, LegalUnit.legal_document_family_id == LegalDocumentFamily.id)
            .where(LegalUnitChunk.legal_source_version_id == legal_source_version_id)
        ).scalar_one()
    )

    unit_count = int(
        db.execute(
            select(func.count(func.distinct(LegalUnit.id)))
            .select_from(LegalUnitChunk)
            .join(LegalUnit, LegalUnitChunk.legal_unit_id == LegalUnit.id)
            .where(LegalUnitChunk.legal_source_version_id == legal_source_version_id)
        ).scalar_one()
    )
    chunk_count = int(
        db.query(LegalUnitChunk).filter(LegalUnitChunk.legal_source_version_id == legal_source_version_id).count()
    )
    citation_count = int(
        db.query(LegalCitation)
        .join(LegalUnitChunk, LegalCitation.legal_unit_chunk_id == LegalUnitChunk.id)
        .filter(LegalUnitChunk.legal_source_version_id == legal_source_version_id)
        .count()
    )
    return {
        "family_count": family_count,
        "legal_unit_count": unit_count,
        "chunk_count": chunk_count,
        "citation_count": citation_count,
    }


def validate_legal_handbook_ingest(
    db: Session,
    *,
    legal_source_version_id: str | None,
    ingest_succeeded: bool,
    precheck_ok: bool,
) -> ValidationPayload:
    p = ValidationPayload()
    p.precheck = {"precheck_ok": precheck_ok}
    if not precheck_ok:
        p.failures.append("precheck_failed")
    if not ingest_succeeded:
        p.failures.append("ingest_did_not_complete")
        return p
    if not legal_source_version_id:
        p.failures.append("missing_legal_source_version_id")
        return p
    counts = legal_version_counts(db, legal_source_version_id=legal_source_version_id)
    p.db_counts = counts
    p.structure = {"profile": "legal_handbook"}
    if counts["chunk_count"] <= 0:
        p.failures.append("no_chunks_for_version")
    if counts["citation_count"] <= 0:
        p.warnings.append("no_citations_for_version")
    if counts["family_count"] <= 0:
        p.failures.append("no_families_for_version")
    return p


def validate_policy_manual_segments(
    *,
    segment_count: int,
    checksum_present: bool,
) -> ValidationPayload:
    p = ValidationPayload()
    p.precheck = {"checksum_present": checksum_present}
    if not checksum_present:
        p.failures.append("missing_content_checksum")
    p.structure = {"segment_count": segment_count, "profile": "policy_manual"}
    if segment_count <= 0:
        p.failures.append("no_segments_parsed")
    elif segment_count == 1:
        p.warnings.append("single_segment_only_consider_heading_structure")
    return p


def merge_payloads(base: ValidationPayload, *others: ValidationPayload) -> ValidationPayload:
    out = ValidationPayload(
        failures=list(base.failures),
        warnings=list(base.warnings),
        precheck=dict(base.precheck),
        structure=dict(base.structure),
        db_counts=dict(base.db_counts),
        retrieval=dict(base.retrieval),
    )
    for o in others:
        out.failures.extend(o.failures)
        out.warnings.extend(o.warnings)
        out.precheck.update(o.precheck)
        out.structure.update(o.structure)
        out.db_counts.update(o.db_counts)
        out.retrieval.update(o.retrieval)
    return out
