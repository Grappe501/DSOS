from __future__ import annotations

import re
from typing import Any


MAX_RESPONSE_LENGTH = 2000


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _extract_allowed_claim_map(truth_packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    claims = truth_packet.get("allowed_claims") or []
    return {
        str(claim.get("id")): claim
        for claim in claims
        if isinstance(claim, dict) and claim.get("id")
    }


def _extract_allowed_numbers(truth_packet: dict[str, Any]) -> set[str]:
    allowed_numbers: set[str] = set()

    for claim in truth_packet.get("allowed_claims") or []:
        claim_value = _stringify((claim or {}).get("value"))
        found = re.findall(r"\d+", claim_value)
        for num in found:
            if num:
                allowed_numbers.add(num)

    return allowed_numbers


def _extract_verified_source_urls(render_payload: dict[str, Any]) -> set[str]:
    urls: set[str] = set()
    for source in render_payload.get("web_sources") or []:
        if not isinstance(source, dict):
            continue
        url = str(source.get("url") or "").strip()
        if url:
            urls.add(url)
    return urls


def build_deterministic_fallback(*, truth_packet: dict[str, Any]) -> str:
    result = truth_packet.get("deterministic_result") or {}
    result_type = result.get("type")

    if truth_packet.get("clarification_preferred"):
        return (
            "I need a little more detail before I can answer that safely. "
            "Please tell me which part of the system or workflow you want me to work with."
        )

    if result_type == "schedule_list":
        count = result.get("count", 0)
        items = result.get("items") or []

        if not items:
            return "I found no schedules in your current scope."

        preview = []
        for item in items[:5]:
            preview.append(
                f"{item.get('title') or 'Untitled'} ({item.get('status') or 'unknown status'})"
            )

        return (
            f"I found {count} schedules in your current scope. "
            f"Here are the first few: " + "; ".join(preview) + "."
        )

    if result_type == "schedule_analysis":
        by_status = result.get("by_status") or {}

        return (
            f"I analyzed {result.get('total', 0)} schedules in your current scope. "
            f"Scheduled: {by_status.get('scheduled', 0)}, "
            f"Draft: {by_status.get('draft', 0)}, "
            f"Submitted: {by_status.get('submitted', 0)}, "
            f"Cancelled: {by_status.get('cancelled', 0)}."
        )

    if truth_packet.get("retrieval_rules", {}).get("allow_web_search"):
        return (
            "I could not produce a verified web-grounded response, so I am returning the safe system fallback instead. "
            "Please refine your request and try again."
        )

    if truth_packet.get("execution_status") == "proposal_only":
        return (
            "I understood the request, but this stage only records the proposal. "
            "No deterministic execution was performed."
        )

    if truth_packet.get("execution_status") == "rejected":
        reasons = (truth_packet.get("validation") or {}).get("reasons") or []
        if reasons:
            return "I could not safely complete that request. " + " ".join(str(r) for r in reasons)
        return "I could not safely complete that request."

    return (
        "I completed the deterministic step, but I could not produce a verified "
        "conversational rendering, so I am returning the safe system summary instead."
    )


def verify_rendered_response(
    *,
    truth_packet: dict[str, Any],
    render_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    render_payload = render_payload or {}
    reasons: list[str] = []

    allowed_claim_map = _extract_allowed_claim_map(truth_packet)
    allowed_numbers = _extract_allowed_numbers(truth_packet)
    verified_source_urls = _extract_verified_source_urls(render_payload)

    grounding_refs = [str(x) for x in render_payload.get("grounding_refs") or []]
    source_refs = [str(x).strip() for x in render_payload.get("source_refs") or [] if str(x).strip()]

    for ref in grounding_refs:
        if ref not in allowed_claim_map:
            reasons.append(f"unknown grounding ref: {ref}")

    for source_ref in source_refs:
        if source_ref not in verified_source_urls:
            reasons.append(f"unknown source ref: {source_ref}")

    clarification_needed = bool(render_payload.get("clarification_needed"))
    clarifying_question = _stringify(render_payload.get("clarifying_question")).strip()
    rendered_answer = _stringify(render_payload.get("rendered_answer")).strip()

    if len(rendered_answer) > MAX_RESPONSE_LENGTH:
        reasons.append("response exceeds maximum allowed length")

    if clarification_needed:
        if not clarifying_question:
            reasons.append("clarification requested without a clarifying question")
    else:
        if not rendered_answer:
            reasons.append("missing rendered answer")

    if truth_packet.get("clarification_preferred") and not clarification_needed:
        reasons.append("clarification required but not requested")

    if verified_source_urls:
        if not clarification_needed and not source_refs:
            reasons.append("web search was used but no verified source refs were returned")
    else:
        rendered_numbers = set(re.findall(r"\d+", rendered_answer))
        unsupported_numbers = sorted(
            number for number in rendered_numbers if number not in allowed_numbers
        )
        if unsupported_numbers:
            reasons.append(f"unsupported numeric claims: {', '.join(unsupported_numbers)}")

    verified = len(reasons) == 0
    fallback_answer = build_deterministic_fallback(truth_packet=truth_packet)

    if clarification_needed and verified:
        delivery_answer = clarifying_question
        delivery_mode = "clarification"
    elif verified and verified_source_urls:
        delivery_answer = rendered_answer
        delivery_mode = "llm_verified_web"
    elif verified:
        delivery_answer = rendered_answer
        delivery_mode = "llm_verified"
    else:
        delivery_answer = fallback_answer
        delivery_mode = "deterministic_fallback"

    return {
        "verified": verified,
        "reasons": reasons,
        "grounding_refs": grounding_refs,
        "source_refs": source_refs,
        "verified_source_urls": sorted(verified_source_urls),
        "fallback_answer": fallback_answer,
        "delivery_answer": delivery_answer,
        "delivery_mode": delivery_mode,
    }