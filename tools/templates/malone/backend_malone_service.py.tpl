"""{{generated_note}} - Malone orchestration service for {manifest_version}."""
from __future__ import annotations

from typing import Any

from app.services.intent_service import classify_intent
from app.services.proposal_service import build_proposal_envelope


def handle_malone_request(message: str, actor: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Malone v1 bounded orchestration entry point.

    AI proposes. Deterministic core validates. This service should never commit
    state directly. It normalizes user input into intent + proposal objects.
    """
    intent = classify_intent(message)
    proposal = build_proposal_envelope(
        proposal_type=intent["mode"],
        requested_action=intent["action"],
        candidate_output={{"message": message, "intent": intent}},
        actor=actor,
    )
    return {{
        "mode": intent["mode"],
        "intent": intent,
        "proposal": proposal,
        "status": "proposal_only",
    }}
