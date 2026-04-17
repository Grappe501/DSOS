"""Deterministic pattern selection with explainable reasons."""

from __future__ import annotations

from typing import Any

from app.services.answer_patterns.signals import (
    PATTERN_EXCEPTION,
    PATTERN_REQUIREMENT,
    PATTERN_SOURCE_LOCATOR,
    PATTERN_STANDARD,
    PATTERN_WORKFLOW,
    combined_signal_scores,
)

# Tie-break when scores equal: earlier in tuple wins (deterministic).
_TIE_PRIORITY = (
    PATTERN_SOURCE_LOCATOR,
    PATTERN_REQUIREMENT,
    PATTERN_WORKFLOW,
    PATTERN_EXCEPTION,
)


def select_answer_pattern(
    *,
    message: str,
    source_type: str,
    normalized_units: list[dict[str, Any]],
) -> dict[str, Any]:
    scores = combined_signal_scores(message, normalized_units)
    reasons: list[str] = [f"signal_scores={scores}"]

    max_score = max(scores.get(p, 0) for p in _TIE_PRIORITY)
    if max_score == 0:
        winner = PATTERN_STANDARD
        top_score = 0
    else:
        winner = next(p for p in _TIE_PRIORITY if scores.get(p, 0) == max_score)
        top_score = max_score

    if top_score == 0:
        confidence = "low"
        reasons.append("all_pattern_scores_zero_use_standard")
    elif top_score >= 12:
        confidence = "high"
        reasons.append(f"winner={winner}_score={top_score}")
    elif top_score >= 6:
        confidence = "medium"
        reasons.append(f"winner={winner}_score={top_score}")
    else:
        confidence = "medium"
        reasons.append(f"winner={winner}_score={top_score}_weak_signal")

    # Legal: avoid obligation/workflow/exception shapes without strong text cue when no normalized rows
    if source_type == "legal_handbook" and not normalized_units:
        if winner in (PATTERN_REQUIREMENT, PATTERN_WORKFLOW, PATTERN_EXCEPTION) and top_score < 12:
            winner = PATTERN_SOURCE_LOCATOR if scores.get(PATTERN_SOURCE_LOCATOR, 0) > 0 else PATTERN_STANDARD
            reasons.append("legal_downgrade_without_norm_units_and_weak_text")
            confidence = "medium"

    return {
        "pattern_id": winner,
        "confidence": confidence,
        "reasons": reasons,
        "signal_scores": dict(scores),
        "source_type": source_type,
    }
