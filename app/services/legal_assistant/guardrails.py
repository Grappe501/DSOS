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
