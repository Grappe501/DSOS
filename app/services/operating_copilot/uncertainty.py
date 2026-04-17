"""Assess uncertainty from merged units, decision workflow, and evidence scope."""

from __future__ import annotations

from typing import Any

from app.services.decision_reasoning.fallback import unit_dict_is_low_trust


def assess_uncertainty(
    *,
    merged_unit_count: int,
    decision_workflow: dict[str, Any] | None,
    source_types: list[str],
    low_trust_unit_count: int,
) -> dict[str, Any]:
    reasons: list[str] = []
    level = "medium"

    if merged_unit_count == 0:
        reasons.append("no_normalized_units_merged")
        level = "high"

    dw = decision_workflow or {}
    if dw.get("partial_workflow"):
        reasons.append("partial_workflow")
        level = "high" if level != "high" else "high"

    if dw.get("caution_low_trust_dominant") or (merged_unit_count and low_trust_unit_count >= merged_unit_count):
        reasons.append("low_trust_or_draft_normalized_fields")
        level = "high"

    if len(source_types) < 2:
        reasons.append("single_source_type_only")

    if not reasons:
        level = "low"
        reasons.append("evidence_present_for_guidance")

    return {
        "level": level,
        "reasons": reasons,
        "source_type_count": len(source_types),
    }


def uncertainty_note_text(u: dict[str, Any]) -> str:
    lvl = u.get("level") or "medium"
    parts = [f"Uncertainty: {lvl}."]
    for r in (u.get("reasons") or [])[:6]:
        parts.append(f"({r})")
    return " ".join(parts)
