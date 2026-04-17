from __future__ import annotations

import os


def _malone_legal_evidence_env_enabled() -> bool:
    v = os.environ.get("MALONE_LEGAL_EVIDENCE_ENABLED", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _policy_manual_triggered(text: str) -> bool:
    """Narrow triggers for internal policy manual grounding (opt-in via env)."""
    t = text.lower()
    needles = (
        "[policy]",
        "policy manual",
        "company policy",
        "internal policy",
        "employee handbook policy",
    )
    return any(n in t for n in needles)


def _legal_handbook_triggered(text: str) -> bool:
    """Narrow triggers for Arkansas / ASBP handbook grounding (not general law chat)."""
    t = text.lower()
    needles = (
        "arkansas state board of pharmacy",
        "asbp",
        "arkansas pharmacy",
        "ark. code ann",
        "arkansas code",
        "ac.a.",
        "ac.b.",
        "ac.c.",
        "ac.d.",
        "ac.e.",
        "ac.f.",
        "ac.g.",
        "ac.h.",
        "17-92-",
        "pharmacy lawbook",
        "lawbook",
        "pdmp",
        "uniform controlled substances",
    )
    return any(n in t for n in needles)


def classify_intent(message: str) -> dict[str, str | None]:
    text = (message or "").strip().lower()

    if not text:
        return {
            "mode": "answer",
            "action": "respond",
            "target": "general",
            "action_key_hint": None,
            "legal_profile": None,
        }

    if _malone_legal_evidence_env_enabled() and _legal_handbook_triggered(text):
        return {
            "mode": "answer",
            "action": "respond",
            "target": "legal_handbook",
            "action_key_hint": None,
            "legal_profile": "arkansas_asbp_handbook",
        }

    v_pol = os.environ.get("MALONE_POLICY_EVIDENCE_ENABLED", "").strip().lower()
    policy_env_on = v_pol in ("1", "true", "yes", "on") or (
        v_pol not in ("0", "false", "no", "off") and _malone_legal_evidence_env_enabled()
    )
    if policy_env_on and _policy_manual_triggered(text):
        return {
            "mode": "answer",
            "action": "respond",
            "target": "policy_manual",
            "action_key_hint": None,
            "legal_profile": None,
        }

    if "schedule" in text or "calendar" in text:
        if any(term in text for term in ["analyze", "summary", "summarize", "how many", "count"]):
            return {
                "mode": "analyst",
                "action": "analyze",
                "target": "schedules",
                "action_key_hint": "schedule.analyze",
                "legal_profile": None,
            }
        return {
            "mode": "answer",
            "action": "respond",
            "target": "schedules",
            "action_key_hint": "schedule.read",
            "legal_profile": None,
        }

    if any(term in text for term in ["report", "analysis", "analyze", "optimize"]):
        return {
            "mode": "analyst",
            "action": "analyze",
            "target": "operations",
            "action_key_hint": None,
            "legal_profile": None,
        }

    if any(term in text for term in ["build", "create", "design", "assemble"]):
        return {
            "mode": "builder",
            "action": "propose_build",
            "target": "system",
            "action_key_hint": None,
            "legal_profile": None,
        }

    if any(term in text for term in ["agent", "investigate", "delegate"]):
        return {
            "mode": "agentic",
            "action": "spawn_agent",
            "target": "operations",
            "action_key_hint": None,
            "legal_profile": None,
        }

    return {
        "mode": "answer",
        "action": "respond",
        "target": "general",
        "action_key_hint": None,
        "legal_profile": None,
    }