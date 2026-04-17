"""
Deterministic SOP/workflow text extraction (regex/heuristic, inspectable).

Does not replace normalized units or citations; enriches assembly when text supports it.
"""

from __future__ import annotations

from typing import Any

from app.services.workflow_extraction.branch_extractor import extract_branches
from app.services.workflow_extraction.checkpoint_extractor import extract_checkpoints
from app.services.workflow_extraction.escalation_trigger_extractor import extract_escalation_triggers
from app.services.workflow_extraction.prerequisite_extractor import extract_prerequisites
from app.services.workflow_extraction.role_owner_extractor import extract_role_owners
from app.services.workflow_extraction.sop_parser import combined_unit_text
from app.services.workflow_extraction.step_extractor import extract_bullet_steps, extract_numbered_steps
from app.services.workflow_extraction.stop_condition_extractor import extract_stop_conditions
from app.services.workflow_extraction.serialization import dumps_extraction


def extract_workflow_fields_from_text(text: str) -> dict[str, Any]:
    """Run all extractors on one text blob; null-safe lists."""
    t = text or ""
    numbered = extract_numbered_steps(t)
    bullets = extract_bullet_steps(t)
    prereq = extract_prerequisites(t)
    ck = extract_checkpoints(t)
    stops = extract_stop_conditions(t)
    esc = extract_escalation_triggers(t)
    roles = extract_role_owners(t)
    branches = extract_branches(t)

    import re as _re

    expected_outputs: list[dict[str, Any]] = []
    for m in _re.finditer(r"(?is)\b(record|document|submit|file|send)\b[^.]{10,400}\.", t):
        expected_outputs.append({"expected_output_text": m.group(0).strip()[:900], "source": "regex_output_verb"})

    conf = _confidence(numbered, bullets, ck, stops, esc)
    return dumps_extraction(
        {
            "numbered_steps": numbered,
            "bullet_steps": bullets,
            "prerequisites": prereq,
            "checkpoints": ck,
            "stop_conditions": stops,
            "escalation_triggers": esc,
            "role_hints": roles,
            "branch_conditions": branches,
            "expected_outputs": expected_outputs[:8],
            "extraction_confidence": conf,
        }
    )


def _confidence(
    numbered: list,
    bullets: list,
    ck: list,
    stops: list,
    esc: list,
) -> str:
    score = 0
    if len(numbered) >= 2:
        score += 3
    elif len(numbered) == 1:
        score += 1
    if bullets:
        score += 1
    if ck or stops or esc:
        score += 1
    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


__all__ = [
    "combined_unit_text",
    "extract_workflow_fields_from_text",
    "extract_numbered_steps",
    "extract_bullet_steps",
]
