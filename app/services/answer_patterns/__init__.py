"""
Smart answer patterns: deterministic question-type shaping after evidence assembly.

Single Malone path — invoked from ``answer_formatter``; does not replace retrieval.
"""

from __future__ import annotations

from app.services.answer_patterns.integration import render_legal_smart_answer, render_policy_smart_answer
from app.services.answer_patterns.pattern_selector import select_answer_pattern
from app.services.answer_patterns.signals import combined_signal_scores

__all__ = [
    "combined_signal_scores",
    "render_legal_smart_answer",
    "render_policy_smart_answer",
    "select_answer_pattern",
]
