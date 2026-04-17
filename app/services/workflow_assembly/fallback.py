"""When text extraction is weak relative to workflow claims, flag safe fallback."""

from __future__ import annotations

from typing import Any


def assess_workflow_extraction_fallback(
    action_steps: list[dict[str, Any]],
    *,
    partial_workflow: bool,
) -> dict[str, Any]:
    """Inspectable flags for copilot / formatters; does not block answers."""
    if not action_steps:
        return {"use_minimal_workflow_guidance": True, "reason": "no_steps"}

    lows = 0
    highs = 0
    for s in action_steps:
        ex = s.get("workflow_extraction") or {}
        c = ex.get("extraction_confidence") or "low"
        if c == "low":
            lows += 1
        elif c == "high":
            highs += 1

    use_minimal = partial_workflow and highs == 0 and lows >= len(action_steps)
    return {
        "use_minimal_workflow_guidance": use_minimal,
        "partial_workflow": partial_workflow,
        "high_confidence_step_extractions": highs,
        "low_confidence_step_extractions": lows,
        "reason": "sparse_text_signals" if use_minimal else None,
    }
