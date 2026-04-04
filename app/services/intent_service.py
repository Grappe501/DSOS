from __future__ import annotations


def classify_intent(message: str) -> dict[str, str]:
    text = (message or "").strip().lower()

    if not text:
        return {
            "mode": "answer",
            "action": "respond",
            "target": "general",
        }

    if "schedule" in text or "calendar" in text:
        if any(term in text for term in ["analyze", "summary", "summarize", "how many", "count"]):
            return {
                "mode": "analyst",
                "action": "analyze",
                "target": "schedules",
            }
        return {
            "mode": "answer",
            "action": "respond",
            "target": "schedules",
        }

    if any(term in text for term in ["report", "analysis", "analyze", "optimize"]):
        return {
            "mode": "analyst",
            "action": "analyze",
            "target": "operations",
        }

    if any(term in text for term in ["build", "create", "design", "assemble"]):
        return {
            "mode": "builder",
            "action": "propose_build",
            "target": "system",
        }

    if any(term in text for term in ["agent", "investigate", "delegate"]):
        return {
            "mode": "agentic",
            "action": "spawn_agent",
            "target": "operations",
        }

    return {
        "mode": "answer",
        "action": "respond",
        "target": "general",
    }