"""Recommended next steps from decision workflow action steps."""

from __future__ import annotations

from typing import Any


def build_next_step_lines(decision_workflow: dict[str, Any] | None) -> list[str]:
    dw = decision_workflow or {}
    steps = dw.get("action_steps") or []
    out: list[str] = []
    for s in steps[:18]:
        summ = (s.get("summary") or "").strip()
        if not summ:
            continue
        order = s.get("order", "?")
        role = (s.get("applies_to_role") or "").strip()
        line = f"{order}. {summ[:800]}"
        if role:
            line += f" (role hint: {role})"
        out.append(line)
    return out


def required_vs_recommended_labels(decision_workflow: dict[str, Any] | None) -> list[str]:
    """Surface requirement_level from merged structure when present on steps (heuristic)."""
    dw = decision_workflow or {}
    # action_steps may not carry requirement_level; placeholder for future enrichment
    lines: list[str] = []
    if dw.get("partial_workflow"):
        lines.append(
            "Requirement vs recommendation: treat ordered items as source-derived guidance, not an exhaustive compliance checklist unless excerpts confirm."
        )
    return lines
