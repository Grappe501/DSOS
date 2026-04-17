"""Deterministic signals from user text and normalized unit payloads."""

from __future__ import annotations

import re
from typing import Any

PATTERN_REQUIREMENT = "requirement"
PATTERN_WORKFLOW = "workflow"
PATTERN_EXCEPTION = "exception"
PATTERN_SOURCE_LOCATOR = "source_locator"
PATTERN_STANDARD = "standard"

_ALL = (PATTERN_REQUIREMENT, PATTERN_WORKFLOW, PATTERN_EXCEPTION, PATTERN_SOURCE_LOCATOR, PATTERN_STANDARD)


def _lower(msg: str) -> str:
    return (msg or "").strip().lower()


def score_question_signals(message: str) -> dict[str, int]:
    """Higher score = stronger match (deterministic keyword sets)."""
    t = _lower(message)
    scores = {p: 0 for p in _ALL}
    scores[PATTERN_STANDARD] = 1  # weak prior

    req_phrases = (
        "what is required",
        "what are we required",
        "what do we have to",
        "have to do",
        "mandatory",
        "must we",
        "is it required",
        "is this mandatory",
        "what does this section require",
        "obligation",
        "duty to",
    )
    if any(p in t for p in req_phrases):
        scores[PATTERN_REQUIREMENT] += 12

    wf_phrases = (
        "what do i do next",
        "what should we do next",
        "what is the process",
        "walk me through",
        "how should we handle",
        "step by step",
        "procedure",
        "workflow",
        "checklist",
        "how do we",
    )
    if any(p in t for p in wf_phrases):
        scores[PATTERN_WORKFLOW] += 12

    exc_phrases = (
        "exception",
        "exceptions",
        "what if ",
        "what if,",
        "unless",
        "special case",
        "edge case",
        "does not apply",
        "when does this not",
        "are there cases",
    )
    if any(p in t for p in exc_phrases):
        scores[PATTERN_EXCEPTION] += 12

    loc_phrases = (
        "where does it say",
        "show me the citation",
        "what section",
        "which section",
        "where in the handbook",
        "where in the policy",
        "cite ",
        "citation",
        "page ",
        "what family",
    )
    if any(p in t for p in loc_phrases):
        scores[PATTERN_SOURCE_LOCATOR] += 12

    # Short citation-like query (deterministic)
    if _citation_like_short_query(t):
        scores[PATTERN_SOURCE_LOCATOR] += 6

    return scores


def _citation_like_short_query(t: str) -> bool:
    if len(t) > 100:
        return False
    return bool(
        re.search(
            r"\b(ac\.[a-z]\.\d+|ark\.?\s*code|\d{1,3}-\d{1,3}-\d{1,4}|17-92-|arkansas code)\b",
            t,
            re.I,
        )
    )


def _unit_type_bucket(ut: str | None) -> str | None:
    u = (ut or "").strip().lower()
    if u in ("requirement", "prohibition", "permission", "obligation", "duty"):
        return "requirement"
    if u in ("workflow_step", "workflow", "procedure_step", "step", "sop_step", "checklist_item"):
        return "workflow"
    if u in ("exception", "exemption", "waiver"):
        return "exception"
    return None


def collect_normalized_units_legal(norm: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not norm or not norm.get("enabled"):
        return []
    out: list[dict[str, Any]] = []
    for lst in (norm.get("units_by_chunk_id") or {}).values():
        for u in lst or []:
            if isinstance(u, dict):
                out.append(u)
    return out


def collect_normalized_units_policy(norm: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not norm or not norm.get("enabled"):
        return []
    out: list[dict[str, Any]] = []
    for lst in (norm.get("units_by_segment_id") or {}).values():
        for u in lst or []:
            if isinstance(u, dict):
                out.append(u)
    return out


def score_normalized_signals(units: list[dict[str, Any]]) -> dict[str, int]:
    scores = {p: 0 for p in _ALL}
    if not units:
        return scores
    for u in units:
        b = _unit_type_bucket(u.get("normalized_unit_type"))
        if b == "requirement":
            scores[PATTERN_REQUIREMENT] += 3
        elif b == "workflow":
            scores[PATTERN_WORKFLOW] += 4
        elif b == "exception":
            scores[PATTERN_EXCEPTION] += 4
        et = (u.get("exception_text") or "").strip()
        if et:
            scores[PATTERN_EXCEPTION] += 2
        ct = (u.get("condition_text") or "").strip()
        if ct:
            scores[PATTERN_REQUIREMENT] += 1
        esc = (u.get("escalation_text") or "").strip()
        if esc:
            scores[PATTERN_WORKFLOW] += 1
    return scores


def combined_signal_scores(message: str, units: list[dict[str, Any]]) -> dict[str, int]:
    q = score_question_signals(message)
    n = score_normalized_signals(units)
    return {p: q.get(p, 0) + n.get(p, 0) for p in _ALL}
