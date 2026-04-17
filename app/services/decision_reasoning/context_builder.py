"""Merge normalized units from one or more evidence bundles into a decision context."""

from __future__ import annotations

from typing import Any

from app.services.ingestion_control.source_types import LEGAL_HANDBOOK, POLICY_MANUAL, SOP_WORKFLOW


def _units_from_legal(bundle: dict[str, Any] | None) -> list[tuple[dict[str, Any], str, dict[str, Any] | None]]:
    """(unit, lane, evidence_item)"""
    if not bundle or not bundle.get("enabled"):
        return []
    norm = bundle.get("normalized") or {}
    if not norm.get("enabled"):
        return []
    by_c = norm.get("units_by_chunk_id") or {}
    items = bundle.get("items") or []
    chunk_to_item: dict[str, dict[str, Any]] = {}
    for it in items:
        cid = str(it.get("legal_unit_chunk_id") or "")
        if cid:
            chunk_to_item[cid] = it
    out: list[tuple[dict[str, Any], str, dict[str, Any] | None]] = []
    for cid, lst in by_c.items():
        for u in lst:
            if isinstance(u, dict):
                u2 = dict(u)
                u2.setdefault("source_type", LEGAL_HANDBOOK)
                out.append((u2, "legal_handbook", chunk_to_item.get(cid)))
    return out


def _units_from_segment_bundle(
    bundle: dict[str, Any] | None,
    lane: str,
    default_source_type: str,
) -> list[tuple[dict[str, Any], str, dict[str, Any] | None]]:
    if not bundle or not bundle.get("enabled"):
        return []
    norm = bundle.get("normalized") or {}
    if not norm.get("enabled"):
        return []
    by_s = norm.get("units_by_segment_id") or {}
    items = bundle.get("items") or []
    seg_to_item: dict[str, dict[str, Any]] = {}
    for it in items:
        sid = str(it.get("ingestion_segment_id") or "")
        if sid:
            seg_to_item[sid] = it
    out: list[tuple[dict[str, Any], str, dict[str, Any] | None]] = []
    for sid, lst in by_s.items():
        for u in lst:
            if isinstance(u, dict):
                u2 = dict(u)
                st = (u2.get("source_type") or default_source_type).strip().lower()
                if lane == "sop_workflow" or st == SOP_WORKFLOW:
                    u2["source_type"] = SOP_WORKFLOW
                else:
                    u2["source_type"] = POLICY_MANUAL
                out.append((u2, lane, seg_to_item.get(sid)))
    return out


def merge_units(
    *,
    legal_bundle: dict[str, Any] | None,
    policy_bundle: dict[str, Any] | None,
    sop_bundle: dict[str, Any] | None,
) -> list[tuple[dict[str, Any], str, dict[str, Any] | None]]:
    merged: list[tuple[dict[str, Any], str, dict[str, Any] | None]] = []
    merged.extend(_units_from_legal(legal_bundle))
    merged.extend(_units_from_segment_bundle(policy_bundle, "policy_manual", POLICY_MANUAL))
    merged.extend(_units_from_segment_bundle(sop_bundle, "sop_workflow", SOP_WORKFLOW))
    return merged


def source_types_present(merged: list[tuple[dict[str, Any], str, Any]]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for u, lane, _ in merged:
        st = (u.get("source_type") or lane).strip().lower()
        if st not in seen:
            seen.add(st)
            out.append(st)
    return out
