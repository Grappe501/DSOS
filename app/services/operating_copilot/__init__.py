"""
Business operating copilot: scenario-style operational guidance on one Malone path.

Sits after retrieval, normalization, decision/workflow assembly, and smart patterns.
Does not replace citations or raw excerpts.
"""

from __future__ import annotations

from typing import Any

from app.services.decision_reasoning.context_builder import merge_units
from app.services.decision_reasoning.fallback import unit_dict_is_low_trust
from app.services.operating_copilot.action_guidance import build_next_step_lines, required_vs_recommended_labels
from app.services.operating_copilot.context_builder import build_copilot_context
from app.services.operating_copilot.cross_source_merge import evidence_scope_summary
from app.services.operating_copilot.escalation_guidance import (
    build_condition_lines,
    build_escalation_lines,
    build_exception_lines,
)
from app.services.operating_copilot.fallback import malone_operating_copilot_enabled
from app.services.operating_copilot.role_guidance import build_role_lines
from app.services.operating_copilot.scenario_router import (
    SCENARIO_NONE,
    SCENARIO_SUMMARY,
    is_operational_copilot_query,
    route_scenario,
)
from app.services.operating_copilot.serialization import serialize_copilot_block
from app.services.operating_copilot.summary_guidance import build_operating_summary_bullets
from app.services.operating_copilot.uncertainty import assess_uncertainty, uncertainty_note_text


def build_operating_copilot_block(
    *,
    message: str,
    legal_bundle: dict[str, Any] | None,
    policy_bundle: dict[str, Any] | None,
    sop_bundle: dict[str, Any] | None,
    decision_workflow: dict[str, Any] | None,
    enabled: bool,
) -> dict[str, Any]:
    """
    Structured operational guidance for truth packet + optional answer appendix.

    Safe when evidence is thin: returns enabled False or minimal uncertainty with fallback_reason.
    """
    if not enabled:
        return {"enabled": False, "reason": "operating_copilot_disabled"}

    scope = evidence_scope_summary(
        legal_bundle=legal_bundle,
        policy_bundle=policy_bundle,
        sop_bundle=sop_bundle,
    )
    total_items = sum((scope.get("item_counts") or {}).values())
    if total_items == 0:
        return {"enabled": False, "reason": "no_evidence_items_for_copilot"}

    if not is_operational_copilot_query(message):
        return {"enabled": False, "reason": "not_operational_query"}

    merged = merge_units(
        legal_bundle=legal_bundle,
        policy_bundle=policy_bundle,
        sop_bundle=sop_bundle,
    )
    low_trust = sum(1 for u, _, _ in merged if unit_dict_is_low_trust(u))
    ctx = build_copilot_context(
        legal_bundle=legal_bundle,
        policy_bundle=policy_bundle,
        sop_bundle=sop_bundle,
        decision_workflow=decision_workflow,
    )

    routed = route_scenario(message, decision_workflow=decision_workflow)
    primary = str(routed.get("primary_scenario") or SCENARIO_NONE)
    route_reasons: list[str] = list(routed.get("reasons") or [])
    if primary == SCENARIO_NONE:
        primary = SCENARIO_SUMMARY
        route_reasons.append("defaulted_to_operating_summary_when_operational")

    dw = decision_workflow or {}
    unc = assess_uncertainty(
        merged_unit_count=len(merged),
        decision_workflow=dw,
        source_types=list(ctx.get("source_types_present") or []),
        low_trust_unit_count=low_trust,
    )

    next_steps = build_next_step_lines(dw)
    roles = build_role_lines(dw)
    esc = build_escalation_lines(dw)
    excs = build_exception_lines(dw)
    conds = build_condition_lines(dw)
    req_lbl = required_vs_recommended_labels(dw)
    bullets = build_operating_summary_bullets(
        message=message, decision_workflow=dw, primary_scenario=primary
    )

    has_structured = bool(next_steps or roles or esc or excs or conds)
    if not has_structured and len(merged) == 0 and unc["level"] == "high":
        block: dict[str, Any] = {
            "enabled": True,
            "fallback_reason": "insufficient_structured_guidance",
            "emit_minimal_only": True,
            "primary_scenario": primary,
            "scenario_route": routed,
            "uncertainty": unc,
            "evidence_scope": scope,
            "context": ctx,
            "guidance": {
                "situation_summary": (message or "").strip()[:500],
                "uncertainty_note": uncertainty_note_text(unc),
            },
            "route_reasons": route_reasons,
        }
        return serialize_copilot_block(block)

    req_preview = [f"Step preview: {s}" for s in next_steps[:3]] if next_steps else []
    guidance: dict[str, Any] = {
        "situation_summary": (message or "").strip()[:500],
        "what_appears_required": list(req_lbl) + req_preview,
        "recommended_next_steps": next_steps,
        "who_should_act": roles,
        "conditions_and_blockers": conds,
        "exceptions": excs,
        "when_to_escalate": esc,
        "operating_summary_bullets": bullets if primary == SCENARIO_SUMMARY else bullets[:4],
        "distinction": {
            "required": "Items tied to requirement/prohibition normalized types or statutory excerpts (verify in Sources).",
            "recommended": "Ordered steps and role hints are assembly aids from normalized fields — confirm against excerpts.",
            "uncertain": uncertainty_note_text(unc),
            "escalate": "When escalation strings exist or uncertainty is high, stop for human/compliance review.",
        },
        "supporting_sources": {
            "source_types": list(ctx.get("source_types_present") or []),
            "cross_source": bool(scope.get("cross_source")),
            "item_counts": scope.get("item_counts") or {},
        },
    }

    block = {
        "enabled": True,
        "fallback_reason": None,
        "emit_minimal_only": False,
        "primary_scenario": primary,
        "scenario_route": routed,
        "uncertainty": unc,
        "evidence_scope": scope,
        "context": ctx,
        "guidance": guidance,
        "route_reasons": route_reasons,
    }
    return serialize_copilot_block(block)


__all__ = [
    "build_operating_copilot_block",
    "is_operational_copilot_query",
    "malone_operating_copilot_enabled",
    "route_scenario",
]
