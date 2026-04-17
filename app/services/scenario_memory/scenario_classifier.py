"""Deterministic scenario labeling from intent + operating-copilot style routing."""

from __future__ import annotations

from typing import Any

from app.services.operating_copilot.scenario_router import route_scenario


def classify_scenario(
    message: str,
    *,
    intent: dict[str, Any],
    decision_workflow: dict[str, Any] | None,
) -> dict[str, Any]:
    """Returns scenario_type label, primary route, and inspectable route payload."""
    target = str(intent.get("target") or "unknown")
    routed = route_scenario(message or "", decision_workflow=decision_workflow)
    primary = str(routed.get("primary_scenario") or "none")
    label = f"{target}|{primary}"
    return {
        "scenario_type": label,
        "intent_target": target,
        "primary_route": primary,
        "primary_scenario": primary,
        "scenario_route": routed,
    }
