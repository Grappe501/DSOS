"""Enrich decision/workflow action steps with text-based workflow extraction."""

from __future__ import annotations

from typing import Any

from app.services.workflow_extraction import combined_unit_text, extract_workflow_fields_from_text
from app.services.workflow_assembly.branch_resolution import collect_branch_hints
from app.services.workflow_assembly.checkpoint_merge import merge_checkpoint_views
from app.services.workflow_assembly.escalation_merge import merge_escalation_views
from app.services.workflow_assembly.fallback import assess_workflow_extraction_fallback
from app.services.workflow_assembly.ownership_assignment import merge_step_ownership
from app.services.workflow_assembly.step_ordering import attach_embedded_substep_count


def enrich_action_steps_with_extraction(
    action_steps: list[dict[str, Any]],
    units: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_id = {str(u.get("id")): u for u in units if u.get("id")}
    out: list[dict[str, Any]] = []
    for step in action_steps:
        s = dict(step)
        uid = str(s.get("unit_id") or "")
        u = by_id.get(uid)
        if not u:
            s["workflow_extraction"] = {
                "extraction_confidence": "none",
                "reason": "unit_not_found_for_step",
            }
            merge_step_ownership(s)
            out.append(s)
            continue
        txt = combined_unit_text(u)
        s["workflow_extraction"] = extract_workflow_fields_from_text(txt)
        merge_step_ownership(s)
        out.append(s)
    attach_embedded_substep_count(out)
    return out


def augment_decision_plan_with_assembly(plan: dict[str, Any]) -> dict[str, Any]:
    """Add merged views + fallback assessment (mutates copy)."""
    p = dict(plan)
    steps = list(p.get("action_steps") or [])
    ck = merge_checkpoint_views(steps)
    p["workflow_checkpoint_view"] = ck
    p["workflow_branch_hints"] = collect_branch_hints(steps)
    p["workflow_escalation_lines_merged"] = merge_escalation_views(p.get("escalations") or [], steps)
    p["workflow_extraction_assessment"] = assess_workflow_extraction_fallback(
        steps,
        partial_workflow=bool(p.get("partial_workflow")),
    )
    return p
