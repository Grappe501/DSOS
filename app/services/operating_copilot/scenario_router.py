"""Deterministic scenario routing for business operating copilot (inspectable)."""

from __future__ import annotations

import re
from typing import Any

SCENARIO_NEXT_STEPS = "next_steps"
SCENARIO_ROLE = "role"
SCENARIO_EXCEPTION = "exception"
SCENARIO_ESCALATION = "escalation"
SCENARIO_SUMMARY = "operating_summary"
SCENARIO_NONE = "none"

_ALL = (
    SCENARIO_NEXT_STEPS,
    SCENARIO_ROLE,
    SCENARIO_EXCEPTION,
    SCENARIO_ESCALATION,
    SCENARIO_SUMMARY,
)

# Tie-break: first listed wins when scores tie at max.
_SCENARIO_TIE_ORDER = (
    SCENARIO_ESCALATION,
    SCENARIO_EXCEPTION,
    SCENARIO_ROLE,
    SCENARIO_NEXT_STEPS,
    SCENARIO_SUMMARY,
)


def _lower(msg: str) -> str:
    return (msg or "").strip().lower()


def score_scenario_signals(message: str) -> dict[str, int]:
    t = _lower(message)
    s = {k: 0 for k in _ALL}
    if any(
        x in t
        for x in (
            "what should we do",
            "what should i do",
            "next step",
            "what is the next step",
            "how should we handle",
            "what do we do here",
            "what to do first",
        )
    ):
        s[SCENARIO_NEXT_STEPS] += 14
    if any(
        x in t
        for x in (
            "pharmacist",
            "technician",
            "who should",
            "who owns",
            "what does the ",
            "role of",
            "responsible for",
        )
    ):
        s[SCENARIO_ROLE] += 14
    if any(
        x in t
        for x in (
            "exception",
            "what if",
            "unless",
            "blocker",
            "denied",
            "does not apply",
            "special case",
        )
    ):
        s[SCENARIO_EXCEPTION] += 14
    if any(
        x in t
        for x in (
            "escalat",
            "compliance",
            "when should this go",
            "stop the workflow",
            "who to notify",
        )
    ):
        s[SCENARIO_ESCALATION] += 14
    if any(
        x in t
        for x in (
            "summarize",
            "short operational",
            "top things",
            "what matters",
            "give me the short",
        )
    ):
        s[SCENARIO_SUMMARY] += 14
    return s


def route_scenario(
    message: str,
    *,
    decision_workflow: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Returns primary_scenario, scores, reasons.

    Uses decision_workflow hints when present (weak boost only).
    """
    scores = score_scenario_signals(message)
    dw = decision_workflow or {}
    reasons: list[str] = [f"scenario_scores={scores}"]

    if dw.get("operational_intent") == "escalation_focus":
        scores[SCENARIO_ESCALATION] += 4
        reasons.append("decision_workflow_escalation_focus")
    if dw.get("operational_intent") == "step_by_step":
        scores[SCENARIO_NEXT_STEPS] += 4
        reasons.append("decision_workflow_step_by_step")
    if (dw.get("escalations") or []):
        scores[SCENARIO_ESCALATION] += 2
    if (dw.get("exceptions") or []) and isinstance(dw.get("exceptions"), list):
        scores[SCENARIO_EXCEPTION] += 1

    max_score = max(scores.get(k, 0) for k in _ALL)
    if max_score == 0:
        return {
            "primary_scenario": SCENARIO_NONE,
            "scores": scores,
            "reasons": reasons + ["no_scenario_signal"],
        }

    candidates = [k for k in _SCENARIO_TIE_ORDER if scores.get(k, 0) == max_score]
    winner = candidates[0]
    reasons.append(f"primary_scenario={winner}")
    return {"primary_scenario": winner, "scores": scores, "reasons": reasons}


def is_operational_copilot_query(message: str) -> bool:
    """Broad gate: scenario-style or role/ops language."""
    t = _lower(message)
    if max(score_scenario_signals(message).values()) > 0:
        return True
    return bool(
        re.search(
            r"\b(operational|workflow|procedure|policy|compliance|escalat|pharmacy technician|pic)\b",
            t,
        )
    )
