"""Deterministic text extraction helpers (regex / keyword scans)."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedSignals:
    is_definition_like: bool
    is_prohibition: bool
    is_permission: bool
    is_exception_like: bool
    is_reporting_duty: bool
    is_escalation: bool
    requirement_level: str
    matched_rule_count: int


_DEF_HEAD = re.compile(r"(?im)^\s*(?:\(\d+\)|\d+\.|definition|definitions)\b")
_SHALL = re.compile(r"\bshall\b", re.I)
_MUST = re.compile(r"\bmust\b", re.I)
_MUST_NOT = re.compile(r"\bmust\s+not\b|\bshall\s+not\b", re.I)
_MAY_NOT = re.compile(r"\bmay\s+not\b", re.I)
_PROHIBITED = re.compile(r"\bprohibited\b|\bunlawful\b|\bviolation\b", re.I)
_MAY = re.compile(r"\bmay\b", re.I)
_EXCEPT = re.compile(r"\bexcept\b|\bunless\b|\bhowever\b", re.I)
_REPORT = re.compile(r"\breport(?:ing)?\b|\bnotify\b|\bdocument\b", re.I)
_ESCAL = re.compile(r"\bescalat\b|\bcontact\b.*\bcompliance\b|\bsupervisor\b", re.I)


def extract_signals(text: str, title: str | None = None) -> ExtractedSignals:
    blob = f"{title or ''}\n{text}"
    matched = 0
    is_def = bool(_DEF_HEAD.search(blob)) or "definition" in blob.lower()[:400]
    if is_def:
        matched += 1

    is_proh = bool(_MUST_NOT.search(blob) or _MAY_NOT.search(blob) or _PROHIBITED.search(blob))
    if is_proh:
        matched += 1

    is_perm = bool(_MAY.search(blob)) and not is_proh
    if is_perm:
        matched += 1

    is_exc = bool(_EXCEPT.search(blob))
    if is_exc:
        matched += 1

    is_rep = bool(_REPORT.search(blob))
    if is_rep:
        matched += 1

    is_esc = bool(_ESCAL.search(blob))
    if is_esc:
        matched += 1

    req = "unknown"
    if _MUST.search(blob) or _SHALL.search(blob):
        req = "must"
        matched += 1
    elif re.search(r"\bshould\b", blob, re.I):
        req = "should"
        matched += 1
    elif _MAY.search(blob):
        req = "may"

    return ExtractedSignals(
        is_definition_like=is_def,
        is_prohibition=is_proh,
        is_permission=is_perm,
        is_exception_like=is_exc,
        is_reporting_duty=is_rep,
        is_escalation=is_esc,
        requirement_level=req,
        matched_rule_count=matched,
    )


def first_sentence(text: str, max_len: int = 280) -> str:
    t = text.strip().replace("\n", " ")
    if not t:
        return ""
    cut = t[:max_len]
    m = re.search(r"[.!?](?:\s|$)", cut)
    if m:
        return cut[: m.end()].strip()
    return cut.strip()
