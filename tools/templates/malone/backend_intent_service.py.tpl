"""{generated_note} - Malone intent parser."""
from __future__ import annotations


def classify_intent(message: str) -> dict[str, str]:
    text = (message or "").lower()

    if any(term in text for term in ["report", "summary", "analyze", "analysis"]):
        return {{"mode": "analyst", "action": "analyze"}}
    if any(term in text for term in ["build", "create", "design", "assemble"]):
        return {{"mode": "builder", "action": "propose_build"}}
    if any(term in text for term in ["agent", "investigate", "optimize"]):
        return {{"mode": "agentic", "action": "spawn_agent"}}

    return {{"mode": "answer", "action": "respond"}}
