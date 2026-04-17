"""Order workflow-ish units; never invent missing steps."""

from __future__ import annotations

import re
from typing import Any

from app.services.decision_reasoning.serialization import parse_json_field

_WORKFLOW_TYPES = frozenset(
    {
        "workflow_step",
        "workflow",
        "procedure_step",
        "step",
        "sop_step",
        "checklist_item",
    }
)
_REQ_TYPES = frozenset({"requirement", "prohibition", "permission", "obligation", "duty"})


def _step_order_from_facets(facets: dict[str, Any]) -> int | None:
    for k in ("step_order", "ordinal", "sequence", "order"):
        v = facets.get(k)
        if isinstance(v, int):
            return v
        if isinstance(v, str) and v.isdigit():
            return int(v)
    return None


def _is_workflowish(unit: dict[str, Any]) -> bool:
    t = (unit.get("normalized_unit_type") or "").strip().lower()
    if t in _WORKFLOW_TYPES:
        return True
    if t in _REQ_TYPES and (unit.get("action_type") or "").strip():
        return True
    st = (unit.get("source_type") or "").strip().lower()
    if st == "sop_workflow":
        return True
    facets = parse_json_field(unit.get("structured_facets_json"), {}) if isinstance(unit.get("structured_facets_json"), str) else (unit.get("structured_facets") or {})
    if isinstance(facets, dict) and facets.get("workflow_step") is True:
        return True
    return False


def assemble_ordered_steps(units: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], bool, str | None]:
    """
    Returns (ordered_step_dicts, partial_workflow, partial_reason).

    partial_workflow True when we could not establish a complete ordered procedure from units alone.
    """
    if not units:
        return [], True, "no_normalized_units"

    wf = [u for u in units if _is_workflowish(u)]
    non_wf = [u for u in units if u not in wf]

    if not wf:
        # Synthesize single-step guidance from top requirement-like units (still partial)
        candidates = [u for u in units if (u.get("plain_language_summary") or u.get("title"))]
        candidates = candidates[:8]
        synth = []
        for i, u in enumerate(candidates, start=1):
            synth.append(
                {
                    "order": i,
                    "kind": "synthesized_from_unit",
                    "summary": (u.get("plain_language_summary") or u.get("title") or "")[:1200],
                    "unit_id": u.get("id"),
                    "normalized_unit_type": u.get("normalized_unit_type"),
                }
            )
        return synth, True, "no_explicit_workflow_steps_in_units"

    decorated: list[tuple[tuple[int, int, str], dict[str, Any]]] = []
    for idx, u in enumerate(wf):
        facets = u.get("structured_facets") or {}
        if isinstance(u.get("structured_facets_json"), str):
            facets = parse_json_field(u.get("structured_facets_json"), facets)
        if not isinstance(facets, dict):
            facets = {}
        ord1 = _step_order_from_facets(facets)
        ord2 = None
        mt = re.search(r"(\d+)", (u.get("title") or ""))
        if mt:
            ord2 = int(mt.group(1))
        key = (ord1 if ord1 is not None else ord2 if ord2 is not None else 999, idx, str(u.get("id") or ""))
        decorated.append((key, u))

    decorated.sort(key=lambda x: x[0])
    ordered = [x[1] for x in decorated]

    out: list[dict[str, Any]] = []
    for i, u in enumerate(ordered, start=1):
        out.append(
            {
                "order": i,
                "kind": "workflow_unit",
                "summary": (u.get("plain_language_summary") or u.get("title") or "")[:1200],
                "unit_id": u.get("id"),
                "normalized_unit_type": u.get("normalized_unit_type"),
                "action_type": u.get("action_type"),
                "applies_to_role": u.get("applies_to_role"),
            }
        )

    partial = bool(non_wf) or len(wf) < 2
    reason = "additional_non_workflow_units_present" if non_wf else ("single_step_only" if len(wf) < 2 else None)
    return out, partial, reason
