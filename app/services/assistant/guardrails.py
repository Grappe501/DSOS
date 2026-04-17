"""
Purpose:
    Enforce policy checks before treating evidence as delivery-ready: minimum citations,
    jurisdiction match, coverage, or other deployment rules.

Role in Malone:
    Defense in depth alongside render_verifier; failures should yield safe refusal or
    clarification, not uncited claims.

Expected inputs:
    Evidence list and compliance outcomes (dicts or structured results).

Expected outputs:
    allow flag plus reasons for regulation_answer_traces or logs.

Notes:
    This is a foundation scaffold for the regulation engine.
    Implementation is intentionally deferred to the next build pass.
"""

from __future__ import annotations

from typing import Any


def guardrails_allow(evidence: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    if not evidence:
        return False, ["no_evidence"]
    return True, []


def guardrails_require_legal_citation_keys(evidence: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """Future Malone gate: every evidence row must carry a persisted citation_key before render."""
    reasons: list[str] = []
    for row in evidence:
        if not row.get("citation_key"):
            reasons.append("missing_citation_key")
    return (len(reasons) == 0, reasons)
