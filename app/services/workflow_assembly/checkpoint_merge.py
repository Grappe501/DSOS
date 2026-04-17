"""Flatten checkpoint/stop/escalation snippets from per-step extraction for display ordering."""

from __future__ import annotations

from typing import Any


def merge_checkpoint_views(action_steps: list[dict[str, Any]]) -> dict[str, Any]:
    checkpoints: list[str] = []
    stops: list[str] = []
    escalations: list[str] = []
    for s in action_steps:
        ex = s.get("workflow_extraction") or {}
        for c in ex.get("checkpoints") or []:
            t = (c.get("checkpoint_text") or "").strip()
            if t:
                checkpoints.append(t)
        for st in ex.get("stop_conditions") or []:
            t = (st.get("stop_condition_text") or "").strip()
            if t:
                stops.append(t)
        for e in ex.get("escalation_triggers") or []:
            t = (e.get("escalation_trigger_text") or "").strip()
            if t:
                escalations.append(t)
    return {
        "checkpoints_flat": checkpoints[:20],
        "stop_conditions_flat": stops[:20],
        "escalation_triggers_flat": escalations[:20],
    }
