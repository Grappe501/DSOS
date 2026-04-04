"""{generated_note} - Malone proposal normalization service."""
from __future__ import annotations

from typing import Any


def build_proposal_envelope(
    *,
    proposal_type: str,
    requested_action: str,
    candidate_output: dict[str, Any],
    actor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {{
        "proposal_type": proposal_type,
        "requested_action": requested_action,
        "candidate_output": candidate_output,
        "origin_actor": actor,
        "validation_status": "pending",
        "approval_status": "pending",
    }}
