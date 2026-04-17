"""Presentation-only adjustments for demo; citations and verification payloads stay authoritative."""

from __future__ import annotations

import re
from typing import Any

from app.services.demo_mode.config import demo_mode_active, demo_safe_responses


def _collapse_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text or "").strip()


def _trim_answer_cosmetic(answer: str | None) -> str | None:
    if answer is None:
        return None
    out = _collapse_blank_lines(answer)
    if len(out) > 14_000:
        return out[:14_000] + "\n…"
    return out


def _first_body_excerpt(items: list[Any], limit: int = 420) -> str:
    for it in items[:3]:
        if not isinstance(it, dict):
            continue
        t = (it.get("body_text") or it.get("text") or it.get("plain_text") or "").strip()
        if t:
            return (t[:limit] + "…") if len(t) > limit else t
    return ""


def build_presentation_layer(response: dict[str, Any]) -> dict[str, Any]:
    """Read-only slices for UI headers — derived from existing truth_packet fields."""
    tp = response.get("truth_packet") if isinstance(response.get("truth_packet"), dict) else {}
    copilot = tp.get("operating_copilot") if isinstance(tp.get("operating_copilot"), dict) else {}
    guidance = copilot.get("guidance") if isinstance(copilot.get("guidance"), dict) else {}
    dw = tp.get("decision_workflow") if isinstance(tp.get("decision_workflow"), dict) else {}

    what_rules: list[str] = []
    for lane in ("legal_evidence", "policy_evidence", "sop_evidence"):
        b = tp.get(lane) if isinstance(tp.get(lane), dict) else {}
        ex = _first_body_excerpt(list(b.get("items") or []))
        if ex:
            what_rules.append(ex)
            break

    next_steps = [str(x).strip() for x in (guidance.get("recommended_next_steps") or []) if str(x).strip()][:8]
    bullets = [str(x).strip() for x in (guidance.get("operating_summary_bullets") or []) if str(x).strip()][:6]
    who = [str(x).strip() for x in (guidance.get("who_should_act") or []) if str(x).strip()][:5]
    escalate = [str(x).strip() for x in (guidance.get("when_to_escalate") or []) if str(x).strip()][:5]

    why_parts: list[str] = []
    if dw.get("title"):
        why_parts.append(str(dw.get("title")))
    rs = dw.get("reasoning_summary") or dw.get("summary")
    if isinstance(rs, str) and rs.strip():
        why_parts.append(rs.strip()[:500])

    ver = response.get("verification") if isinstance(response.get("verification"), dict) else {}
    if ver.get("delivery_mode") and not why_parts:
        why_parts.append(f"Delivery mode: {ver.get('delivery_mode')}")

    return {
        "headers": {
            "evidence": "What the rules say",
            "guidance": "What to do next",
            "reasoning": "Why this answer",
            "summary": "Operational summary",
        },
        "what_the_rules_say": what_rules[0] if what_rules else "",
        "next_best_actions": next_steps or bullets,
        "who_should_act": who,
        "when_to_escalate": escalate,
        "why_this_answer": " ".join(why_parts)[:1200] if why_parts else "",
        "operating_copilot_enabled": bool(copilot.get("enabled")),
    }


def apply_demo_limited_scope_truth_packet(truth_packet: dict[str, Any]) -> None:
    """Mutates truth_packet: turn off web search for the conversational render branch."""
    from app.services.demo_mode.config import demo_limited_scope

    if not demo_limited_scope():
        return
    rr = truth_packet.setdefault("retrieval_rules", {})
    if isinstance(rr, dict):
        rr["allow_web_search"] = False


def attach_demo_envelope(response: dict[str, Any]) -> dict[str, Any]:
    """Add demo flags + presentation; optional cosmetic trim on delivery.answer."""
    from app.services.demo_mode.config import demo_config_payload, demo_mode_active

    cfg = demo_config_payload()
    active = bool(cfg["malone_demo_mode"])
    response["demo"] = {"active": active, **cfg}

    if active and demo_safe_responses():
        d = response.get("delivery")
        if isinstance(d, dict) and d.get("answer") is not None:
            trimmed = _trim_answer_cosmetic(str(d.get("answer")))
            if trimmed is not None:
                d["answer"] = trimmed

    if active:
        response["presentation"] = build_presentation_layer(response)
    return response
