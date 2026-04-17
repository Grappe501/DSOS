from __future__ import annotations


def classify_intent(message: str) -> dict[str, str | None]:
    text = (message or "").strip().lower()

    if not text:
        return {
            "mode": "answer",
            "action": "respond",
            "target": "general",
            "action_key_hint": None,
        }

    if "schedule" in text or "calendar" in text:
        if any(term in text for term in ["analyze", "summary", "summarize", "how many", "count"]):
            return {
                "mode": "analyst",
                "action": "analyze",
                "target": "schedules",
                "action_key_hint": "schedule.analyze",
            }
        return {
            "mode": "answer",
            "action": "respond",
            "target": "schedules",
            "action_key_hint": "schedule.read",
        }

    if any(term in text for term in ["report", "analysis", "analyze", "optimize"]):
        return {
            "mode": "analyst",
            "action": "analyze",
            "target": "operations",
            "action_key_hint": None,
        }

    if any(term in text for term in ["build", "create", "design", "assemble"]):
        return {
            "mode": "builder",
            "action": "propose_build",
            "target": "system",
            "action_key_hint": None,
        }

    if any(term in text for term in ["agent", "investigate", "delegate"]):
        return {
            "mode": "agentic",
            "action": "spawn_agent",
            "target": "operations",
            "action_key_hint": None,
        }

    return {
        "mode": "answer",
        "action": "respond",
        "target": "general",
        "action_key_hint": None,
    }