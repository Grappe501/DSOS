"""
Purpose:
    Map compliance failures to safe user-visible outcomes (clarify, refuse, escalate)
    without performing state mutation in this module.

Role in Malone:
    Orchestrator or malone_service may translate these dicts into delivery modes that
    align with clarification and workflow blocked semantics.

Expected inputs:
    Failure codes or reasons from authority, effective_dates, conflicts modules.

Expected outputs:
    Structured dicts suitable for logging and response shaping.

Notes:
    This is a foundation scaffold for the regulation engine.
    Implementation is intentionally deferred to the next build pass.
"""

from __future__ import annotations

from typing import Any


def escalation_for_no_evidence(*, reason: str) -> dict[str, Any]:
    return {
        "action": "refuse_or_clarify",
        "reason": reason,
        "safe_for_user": True,
    }
