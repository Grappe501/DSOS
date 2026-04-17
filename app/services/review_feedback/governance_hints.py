"""Lightweight governance summary for Malone responses (non-authoritative)."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.services.review_feedback.review_queries import get_head, summarize_normalized_unit_stub
from app.services.review_feedback.artifact_registry import ARTIFACT_NORMALIZED_UNIT


def _collect_unit_ids_from_packet(truth_packet: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for lane in ("legal_evidence", "policy_evidence", "sop_evidence"):
        b = truth_packet.get(lane) if isinstance(truth_packet.get(lane), dict) else {}
        norm = b.get("normalized") if isinstance(b.get("normalized"), dict) else {}
        umap = norm.get("units_by_chunk_id") or norm.get("units_by_segment_id") or {}
        if not isinstance(umap, dict):
            continue
        for _k, rows in umap.items():
            if not isinstance(rows, list):
                continue
            for row in rows:
                if isinstance(row, dict) and row.get("id"):
                    ids.append(str(row["id"]))
    return list(dict.fromkeys(ids))[:40]


def build_governance_hints_for_turn(db: Session, truth_packet: dict[str, Any]) -> dict[str, Any]:
    """Summarize review heads for normalized units referenced in the truth packet."""
    unit_ids = _collect_unit_ids_from_packet(truth_packet)
    units_out: list[dict[str, Any]] = []
    for uid in unit_ids:
        stub = summarize_normalized_unit_stub(db, uid)
        head = get_head(db, artifact_type=ARTIFACT_NORMALIZED_UNIT, artifact_id=uid)
        units_out.append(
            {
                "normalized_unit_id": uid,
                "unit": stub,
                "review_head": head,
            }
        )
    return {
        "read_only": True,
        "precedence_note": "Governance hints do not override source-grounded citations.",
        "normalized_units": units_out,
    }
