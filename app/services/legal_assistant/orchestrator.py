"""
Purpose:
    Single import surface for handbook evidence + formatting (no duplicate agent).

Role in Malone:
    Callers use ``build_legal_evidence_bundle`` and ``format_legal_lookup_answer``;
    routing remains in ``malone_service``.
"""

from __future__ import annotations

from app.services.legal_assistant.answer_formatter import format_legal_lookup_answer
from app.services.legal_evidence_service import (
    build_legal_evidence_bundle,
    enrich_truth_packet_with_legal,
)

__all__ = [
    "build_legal_evidence_bundle",
    "enrich_truth_packet_with_legal",
    "format_legal_lookup_answer",
]
