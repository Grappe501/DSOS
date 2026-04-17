"""JSON-safe decision/workflow structures for truth packet and formatting."""

from __future__ import annotations

import json
from typing import Any


def parse_json_field(raw: str | None, default: Any) -> Any:
    if not raw or not str(raw).strip():
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return default


def source_anchor_for_unit(
    unit: dict[str, Any],
    *,
    lane: str,
    evidence_item: dict[str, Any] | None,
) -> dict[str, Any]:
    """Stable anchor for audit: ties a normalized unit back to raw evidence."""
    anchor: dict[str, Any] = {"lane": lane, "normalized_unit_id": unit.get("id")}
    if lane == "legal_handbook":
        anchor["legal_unit_chunk_id"] = unit.get("legal_unit_chunk_id") or (evidence_item or {}).get(
            "legal_unit_chunk_id"
        )
        anchor["citation_key"] = (evidence_item or {}).get("citation_key") or (evidence_item or {}).get(
            "primary_citation"
        )
    elif lane in ("policy_manual", "sop_workflow"):
        anchor["ingestion_segment_id"] = unit.get("ingestion_segment_id") or (evidence_item or {}).get(
            "ingestion_segment_id"
        )
        anchor["heading"] = (evidence_item or {}).get("heading")
    anchor["source_type"] = unit.get("source_type")
    return {k: v for k, v in anchor.items() if v is not None}


def serialize_decision_workflow_block(block: dict[str, Any]) -> dict[str, Any]:
    """Ensure only JSON-serializable content (caller builds block)."""
    return json.loads(json.dumps(block, default=str))
