"""When decision/workflow reasoning must downgrade or skip (additive safety)."""

from __future__ import annotations

from typing import Any

from app.services.normalized_retrieval.fallback import confidence_rank, review_rank


def _normalized_retrieval_env_on() -> bool:
    import os

    v = os.environ.get("MALONE_NORMALIZED_RETRIEVAL_ENABLED", "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    v2 = os.environ.get("MALONE_LEGAL_EVIDENCE_ENABLED", "").strip().lower()
    return v2 in ("1", "true", "yes", "on")


def malone_decision_reasoning_enabled() -> bool:
    """Augment answers with structured decision/workflow assembly (follows normalized gate by default)."""
    import os

    v = os.environ.get("MALONE_DECISION_REASONING_ENABLED", "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    return _normalized_retrieval_env_on()


def malone_cross_source_decision_enabled() -> bool:
    """Allow loading multiple evidence bundles for one request (legal + policy + optional SOP)."""
    import os

    v = os.environ.get("MALONE_CROSS_SOURCE_DECISION_ENABLED", "").strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off"):
        return False
    return False


def _policy_evidence_env_on() -> bool:
    import os

    v = os.environ.get("MALONE_POLICY_EVIDENCE_ENABLED", "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    return _normalized_retrieval_env_on()


def malone_sop_evidence_enabled() -> bool:
    """SOP / workflow segment retrieval (segment-based, same pattern as policy)."""
    import os

    v = os.environ.get("MALONE_SOP_EVIDENCE_ENABLED", "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    return _policy_evidence_env_on()


def malone_sop_lookup_enabled() -> bool:
    """Deterministic SOP answer path."""
    import os

    v = os.environ.get("MALONE_SOP_LOOKUP_ENABLED", "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    return malone_sop_evidence_enabled()


def unit_dict_is_low_trust(u: dict[str, Any]) -> bool:
    """Draft or unknown confidence — still show but must not dominate ranking."""
    c = str(u.get("confidence_level") or "").strip().lower()
    r = str(u.get("review_state") or "").strip().lower()
    return c == "unknown" or r == "draft"


def aggregate_trust_tier(units: list[dict[str, Any]]) -> str:
    """Coarse bucket for packet_meta."""
    if not units:
        return "none"
    scores = [review_rank(u.get("review_state")) * 10 + confidence_rank(u.get("confidence_level")) for u in units]
    if max(scores) >= 40:
        return "high"
    if max(scores) >= 25:
        return "medium"
    return "low"


def should_emit_structured_sections(decision_block: dict[str, Any] | None) -> bool:
    if not decision_block or not decision_block.get("enabled"):
        return False
    if decision_block.get("fallback_reason"):
        return False
    return True
