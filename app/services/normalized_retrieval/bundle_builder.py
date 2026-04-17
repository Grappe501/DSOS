"""Combine raw evidence bundles with normalized knowledge units."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.services.normalized_retrieval.fallback import unit_needs_caveat
from app.services.normalized_retrieval.legal_selector import (
    fetch_normalized_units_for_legal_chunks,
    group_units_by_chunk_id,
)
from app.services.normalized_retrieval.policy_selector import (
    fetch_normalized_units_for_policy_segments,
    group_units_by_segment_id,
    search_policy_segments,
)
from app.services.ingestion_control.source_types import POLICY_MANUAL, SOP_WORKFLOW
from app.services.normalized_retrieval.serialization import normalized_unit_to_dict


def attach_normalized_to_legal_bundle(
    db: Session,
    bundle: dict[str, Any],
    *,
    enabled: bool,
) -> dict[str, Any]:
    """
    Mutates and returns ``bundle`` with a ``normalized`` key when units exist.

    Raw ``items`` are unchanged; normalized data is additive metadata keyed by chunk id.
    """
    if not enabled or not bundle.get("enabled"):
        bundle["normalized"] = {"enabled": False, "reason": "normalized_retrieval_disabled"}
        return bundle

    vid = bundle.get("legal_source_version_id")
    items = bundle.get("items") or []
    chunk_ids = [str(it.get("legal_unit_chunk_id")) for it in items if it.get("legal_unit_chunk_id")]
    if not vid or not chunk_ids:
        bundle["normalized"] = {
            "enabled": True,
            "units_by_chunk_id": {},
            "warnings": ["no_chunks_or_version_for_normalized_attachment"],
            "fallback_reason": "missing_scope",
        }
        return bundle

    units = fetch_normalized_units_for_legal_chunks(db, legal_source_version_id=str(vid), chunk_ids=chunk_ids)
    grouped = group_units_by_chunk_id(units)
    ser: dict[str, list[dict[str, Any]]] = {}
    warnings: list[str] = []
    for cid, lst in grouped.items():
        ser[cid] = []
        for u in lst:
            d = normalized_unit_to_dict(u)
            if unit_needs_caveat(u):
                d["caveat"] = "low_confidence_or_draft_review"
                warnings.append(f"caveat:{cid}")
            ser[cid].append(d)

    bundle["normalized"] = {
        "enabled": True,
        "source_type": "legal_handbook",
        "units_by_chunk_id": ser,
        "warnings": warnings,
        "fallback_reason": None if ser else "no_matching_normalized_units",
    }
    return bundle


def _build_segment_evidence_bundle_with_normalized(
    db: Session,
    message: str,
    *,
    ingestion_source_version_id: str | None,
    segment_kind: str,
    no_version_warning: str,
    no_hits_warning: str,
    limit: int = 8,
    normalized_enabled: bool,
) -> dict[str, Any]:
    """Shared path for policy_manual and sop_workflow segment stores."""
    vid = ingestion_source_version_id
    warnings: list[str] = []
    if not vid:
        warnings.append(no_version_warning)
        return {
            "enabled": True,
            "segment_kind": segment_kind,
            "ingestion_source_version_id": None,
            "items": [],
            "warnings": warnings,
            "normalized": {"enabled": False, "reason": "no_version"},
        }

    items = search_policy_segments(db, message, ingestion_source_version_id=str(vid), limit=limit)
    if not items:
        warnings.append(no_hits_warning)

    seg_ids = [str(it["ingestion_segment_id"]) for it in items if it.get("ingestion_segment_id")]
    norm_block: dict[str, Any] = {"enabled": False}
    if normalized_enabled and seg_ids:
        units = fetch_normalized_units_for_policy_segments(
            db, ingestion_source_version_id=str(vid), segment_ids=seg_ids
        )
        grouped = group_units_by_segment_id(units)
        ser: dict[str, list[dict[str, Any]]] = {}
        nw: list[str] = []
        for sid, lst in grouped.items():
            ser[sid] = []
            for u in lst:
                d = normalized_unit_to_dict(u)
                if unit_needs_caveat(u):
                    d["caveat"] = "low_confidence_or_draft_review"
                    nw.append(f"caveat:{sid}")
                ser[sid].append(d)
        norm_block = {
            "enabled": True,
            "source_type": segment_kind,
            "units_by_segment_id": ser,
            "warnings": nw,
            "fallback_reason": None if ser else "no_matching_normalized_units",
        }
    elif normalized_enabled:
        norm_block = {
            "enabled": True,
            "source_type": segment_kind,
            "units_by_segment_id": {},
            "warnings": [],
            "fallback_reason": "no_segments",
        }

    return {
        "enabled": True,
        "segment_kind": segment_kind,
        "ingestion_source_version_id": str(vid),
        "items": items,
        "warnings": warnings,
        "normalized": norm_block,
    }


def build_policy_evidence_bundle_with_normalized(
    db: Session,
    message: str,
    *,
    ingestion_source_version_id: str | None,
    limit: int = 8,
    normalized_enabled: bool,
) -> dict[str, Any]:
    """Segment search + optional normalized units (policy_manual)."""
    return _build_segment_evidence_bundle_with_normalized(
        db,
        message,
        ingestion_source_version_id=ingestion_source_version_id,
        segment_kind=POLICY_MANUAL,
        no_version_warning="no_policy_source_version",
        no_hits_warning="no_policy_segment_hits",
        limit=limit,
        normalized_enabled=normalized_enabled,
    )


def build_sop_evidence_bundle_with_normalized(
    db: Session,
    message: str,
    *,
    ingestion_source_version_id: str | None,
    limit: int = 8,
    normalized_enabled: bool,
) -> dict[str, Any]:
    """Segment search + optional normalized units (sop_workflow)."""
    return _build_segment_evidence_bundle_with_normalized(
        db,
        message,
        ingestion_source_version_id=ingestion_source_version_id,
        segment_kind=SOP_WORKFLOW,
        no_version_warning="no_sop_source_version",
        no_hits_warning="no_sop_segment_hits",
        limit=limit,
        normalized_enabled=normalized_enabled,
    )


def merge_normalized_into_item(
    items: list[dict[str, Any]],
    units_by_chunk_id: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Attach ``normalized_units`` copy onto each evidence item (non-destructive)."""
    out = []
    for it in items:
        cid = str(it.get("legal_unit_chunk_id") or "")
        row = dict(it)
        if cid and cid in units_by_chunk_id:
            row["normalized_units"] = list(units_by_chunk_id[cid])
        out.append(row)
    return out
