"""
Purpose:
    Legal-specific forbidden-claim templates and “not legal advice” boundaries for handbook mode.

Role in Malone:
    Aligns with `truth_packet_service` forbidden_claims when legal mode is active.

Expected inputs:
    Draft answer text, evidence list.

Expected outputs:
    Pass/fail and reasons for verifier (deterministic checks only in v1).

TODO boundary:
    LLM-based verification remains in existing `render_verifier`; this is rule-based only.
"""

from __future__ import annotations


def legal_handbook_forbidden_claims() -> list[str]:
    return [
        "Do not present handbook excerpts as personal legal advice or as a substitute for counsel.",
        "Do not extrapolate beyond the provided excerpts and citation metadata.",
        "Do not claim the handbook compilation is the official filing if the source metadata says otherwise.",
    ]
