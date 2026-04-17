"""Build auditable action plan + source map from merged units."""

from __future__ import annotations

from typing import Any

from app.services.decision_reasoning.escalation_resolver import group_escalations
from app.services.decision_reasoning.exception_resolver import group_exceptions
from app.services.decision_reasoning.role_mapper import collect_roles
from app.services.decision_reasoning.serialization import parse_json_field, source_anchor_for_unit
from app.services.decision_reasoning.workflow_assembler import assemble_ordered_steps
from app.services.decision_reasoning.condition_evaluator import group_conditions


def build_action_plan(
    merged: list[tuple[dict[str, Any], str, dict[str, Any] | None]],
) -> dict[str, Any]:
    units = [m[0] for m in merged]
    roles = collect_roles(units)
    conditions = group_conditions(units)
    exceptions = group_exceptions(units)
    escalations = group_escalations(units)
    steps, partial, partial_reason = assemble_ordered_steps(units)

    source_evidence_map: dict[str, Any] = {}
    for u, lane, ev in merged:
        uid = str(u.get("id") or "")
        if not uid:
            continue
        source_evidence_map[uid] = source_anchor_for_unit(u, lane=lane, evidence_item=ev)
        ck = parse_json_field(u.get("citation_keys_json") if isinstance(u.get("citation_keys_json"), str) else None, [])
        if ck:
            source_evidence_map[uid]["citation_keys"] = ck

    return {
        "roles": roles,
        "conditions": conditions,
        "exceptions": exceptions,
        "escalations": escalations,
        "action_steps": steps,
        "partial_workflow": partial,
        "partial_workflow_reason": partial_reason,
        "source_evidence_map": source_evidence_map,
    }
