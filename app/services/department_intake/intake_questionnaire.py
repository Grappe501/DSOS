"""Structured baseline prompts (deterministic; not LLM-generated)."""

from __future__ import annotations

from typing import Any

# question_key -> prompt text
BASE_QUESTIONS: list[dict[str, Any]] = [
    {"key": "mission", "prompt": "What is this department's primary purpose or mission?", "priority": 1},
    {"key": "responsibilities", "prompt": "What are the main responsibilities owned by this department?", "priority": 2},
    {"key": "roles", "prompt": "What roles or job titles exist in this department, and who owns what?", "priority": 3},
    {"key": "workflows", "prompt": "What are the major workflows or recurring processes?", "priority": 3},
    {"key": "systems", "prompt": "What systems or tools does the department use day to day?", "priority": 4},
    {"key": "inputs_outputs", "prompt": "What are the key inputs to your work and what do you deliver as outputs?", "priority": 4},
    {"key": "dependencies", "prompt": "Who do you depend on, and who depends on you?", "priority": 5},
    {"key": "handoffs", "prompt": "Where are handoffs to other teams or departments?", "priority": 5},
    {"key": "escalation", "prompt": "When and how do you escalate issues?", "priority": 6},
    {"key": "blockers", "prompt": "What blockers, pain points, or exceptions come up often?", "priority": 6},
    {"key": "sop_refs", "prompt": "What written SOPs, policies, or forms apply (by name if known)?", "priority": 7},
    {"key": "metrics", "prompt": "How do you measure success for this department?", "priority": 8},
]


def initial_prompts() -> list[dict[str, Any]]:
    return list(BASE_QUESTIONS)
