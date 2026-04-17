"""Governance helpers: intake memory is not authoritative over source evidence."""

from __future__ import annotations


def evidence_precedence_rank(source_kind: str) -> int:
    """
    Higher wins on conflict for *advisory* merging only.
    Legal/source-grounded kinds always dominate conversational intake.
    """
    k = (source_kind or "").strip().lower()
    return {
        "legal_handbook_citation": 100,
        "legal_unit_chunk": 95,
        "ingested_policy_segment": 70,
        "ingested_sop_segment": 70,
        "normalized_unit_approved": 65,
        "intake_session_memory": 15,
        "intake_draft": 10,
    }.get(k, 5)


def intake_is_non_authoritative() -> bool:
    return True
