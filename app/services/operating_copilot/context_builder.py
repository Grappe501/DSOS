"""Operational context metadata for copilot (counts, merge hints)."""

from __future__ import annotations

from typing import Any

from app.services.decision_reasoning.context_builder import merge_units, source_types_present


def build_copilot_context(
    *,
    legal_bundle: dict[str, Any] | None,
    policy_bundle: dict[str, Any] | None,
    sop_bundle: dict[str, Any] | None,
    decision_workflow: dict[str, Any] | None,
) -> dict[str, Any]:
    merged = merge_units(
        legal_bundle=legal_bundle,
        policy_bundle=policy_bundle,
        sop_bundle=sop_bundle,
    )
    st = source_types_present(merged)
    dw = decision_workflow or {}
    return {
        "merged_normalized_unit_tuples": len(merged),
        "source_types_present": st,
        "decision_workflow_enabled": bool(dw.get("enabled")),
        "decision_fallback_reason": dw.get("fallback_reason"),
    }
