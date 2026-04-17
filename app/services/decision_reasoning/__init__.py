"""
Decision / workflow reasoning: assemble normalized units into auditable operational guidance.

Single Malone path — augments the same evidence bundles and formatters; does not replace raw excerpts.
"""

from __future__ import annotations

from typing import Any

from app.services.decision_reasoning.action_plan_builder import build_action_plan
from app.services.decision_reasoning.context_builder import merge_units, source_types_present
from app.services.decision_reasoning.decision_router import classify_operational_intent
from app.services.decision_reasoning.fallback import aggregate_trust_tier, malone_decision_reasoning_enabled, unit_dict_is_low_trust
from app.services.decision_reasoning.serialization import serialize_decision_workflow_block
from app.services.normalized_retrieval.fallback import confidence_rank, review_rank


def build_decision_workflow_block(
    *,
    message: str,
    legal_bundle: dict[str, Any] | None,
    policy_bundle: dict[str, Any] | None,
    sop_bundle: dict[str, Any] | None,
    enabled: bool,
) -> dict[str, Any]:
    """
    Build inspectable decision/workflow structure for truth packet + answer formatting.

    When ``enabled`` is False or no normalized units are merged, returns a small disabled / fallback dict.
    """
    if not enabled:
        return {"enabled": False, "reason": "decision_reasoning_disabled"}

    merged = merge_units(
        legal_bundle=legal_bundle,
        policy_bundle=policy_bundle,
        sop_bundle=sop_bundle,
    )
    intent = classify_operational_intent(message)

    if not merged:
        return {
            "enabled": True,
            "fallback_reason": "no_normalized_units_for_decision_layer",
            "operational_intent": intent,
            "sources_present": [],
        }

    units_for_plan = sorted(
        [m[0] for m in merged],
        key=lambda u: (
            -review_rank(u.get("review_state")),
            -confidence_rank(u.get("confidence_level")),
            str(u.get("id") or ""),
        ),
    )
    # Re-merge tuples in sorted unit order for build_action_plan (evidence map needs all links)
    by_id = {str(m[0].get("id")): m for m in merged if m[0].get("id")}
    merged_sorted: list[tuple[dict[str, Any], str, dict[str, Any] | None]] = []
    for u in units_for_plan:
        uid = str(u.get("id") or "")
        if uid in by_id:
            merged_sorted.append(by_id[uid])

    plan = build_action_plan(merged_sorted if merged_sorted else list(merged))
    sources = source_types_present(merged)
    low_trust = sum(1 for u, _, _ in merged if unit_dict_is_low_trust(u))

    block: dict[str, Any] = {
        "enabled": True,
        "fallback_reason": None,
        "operational_intent": intent,
        "sources_present": sources,
        "trust_tier": aggregate_trust_tier([m[0] for m in merged]),
        "low_trust_unit_count": low_trust,
        "caution_low_trust_dominant": low_trust >= len(merged) and len(merged) > 0,
    }
    block.update(plan)
    return serialize_decision_workflow_block(block)


__all__ = [
    "build_decision_workflow_block",
    "build_action_plan",
    "classify_operational_intent",
    "merge_units",
    "malone_decision_reasoning_enabled",
    "serialize_decision_workflow_block",
]
