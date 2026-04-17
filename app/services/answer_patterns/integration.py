"""Wire selector + pattern renderers into one entrypoint for answer_formatter."""

from __future__ import annotations

from typing import Any

from app.services.answer_patterns import (
    exception_pattern,
    requirement_pattern,
    source_locator_pattern,
    workflow_pattern,
)
from app.services.answer_patterns.fallback import (
    malone_smart_answer_patterns_enabled,
    should_fallback_to_standard_pattern,
)
from app.services.answer_patterns.pattern_selector import select_answer_pattern
from app.services.answer_patterns.serialization import pattern_trace_to_dict
from app.services.answer_patterns.signals import (
    PATTERN_STANDARD,
    collect_normalized_units_legal,
    collect_normalized_units_policy,
)


def _append_decision(lines: list[str], decision_workflow: dict[str, Any] | None) -> None:
    from app.services.legal_assistant.answer_formatter import append_decision_workflow_lines

    append_decision_workflow_lines(lines, decision_workflow)


def _append_copilot(lines: list[str], truth_packet: dict[str, Any] | None) -> None:
    from app.services.legal_assistant.answer_formatter import append_operating_copilot_lines

    if truth_packet:
        append_operating_copilot_lines(lines, truth_packet.get("operating_copilot"))


def render_legal_smart_answer(
    *,
    message: str,
    items: list[dict[str, Any]],
    normalized_bundle: dict[str, Any] | None,
    decision_workflow: dict[str, Any] | None,
    max_items: int,
    truth_packet: dict[str, Any] | None,
) -> str:
    from app.services.legal_assistant.answer_formatter import format_legal_lookup_answer_standard

    units = collect_normalized_units_legal(normalized_bundle)
    sel = select_answer_pattern(message=message, source_type="legal_handbook", normalized_units=units)
    pid = str(sel.get("pattern_id") or PATTERN_STANDARD)
    conf = str(sel.get("confidence") or "low")
    use_standard = (
        not malone_smart_answer_patterns_enabled()
        or should_fallback_to_standard_pattern(
            pattern_id=pid,
            confidence=conf,
            items=items,
            normalized_units=units,
        )
        or pid == PATTERN_STANDARD
    )
    trace: dict[str, Any] = {**sel, "smart_patterns_enabled": malone_smart_answer_patterns_enabled()}

    if use_standard:
        text = format_legal_lookup_answer_standard(
            items,
            max_items=max_items,
            normalized_bundle=normalized_bundle,
        )
        trace["rendered_pattern"] = "standard"
        trace["fallback_to_standard"] = True
    else:
        if pid == "workflow":
            text = workflow_pattern.render_legal(
                message=message,
                items=items,
                normalized_bundle=normalized_bundle,
                decision_workflow=decision_workflow,
                max_items=max_items,
            )
        elif pid == "requirement":
            text = requirement_pattern.render_legal(
                message=message,
                items=items,
                normalized_bundle=normalized_bundle,
                max_items=max_items,
            )
        elif pid == "exception":
            text = exception_pattern.render_legal(
                message=message,
                items=items,
                normalized_bundle=normalized_bundle,
                max_items=max_items,
            )
        elif pid == "source_locator":
            text = source_locator_pattern.render_legal(
                message=message,
                items=items,
                normalized_bundle=normalized_bundle,
                max_items=max_items,
            )
        else:
            text = format_legal_lookup_answer_standard(
                items,
                max_items=max_items,
                normalized_bundle=normalized_bundle,
            )
            trace["rendered_pattern"] = "standard"
            trace["fallback_to_standard"] = True
        if pid in ("workflow", "requirement", "exception", "source_locator"):
            trace["rendered_pattern"] = pid
            trace["fallback_to_standard"] = False

    lines = text.split("\n")
    _append_decision(lines, decision_workflow)
    _append_copilot(lines, truth_packet)
    out = "\n".join(lines)
    if truth_packet is not None:
        truth_packet["answer_pattern"] = pattern_trace_to_dict(trace)
        pm = truth_packet.setdefault("packet_meta", {})
        pm["answer_pattern_rendered"] = trace.get("rendered_pattern")
        pm["answer_pattern_selected"] = trace.get("pattern_id")
        pm["answer_pattern_confidence"] = trace.get("confidence")
        rp = trace.get("rendered_pattern")
        if rp and rp != "standard":
            from app.services.legal_assistant.guardrails import smart_answer_pattern_forbidden_claims

            forb = list(truth_packet.get("forbidden_claims") or [])
            forb.extend(smart_answer_pattern_forbidden_claims())
            truth_packet["forbidden_claims"] = forb[:80]
    return out


def render_policy_smart_answer(
    *,
    message: str,
    items: list[dict[str, Any]],
    normalized_bundle: dict[str, Any] | None,
    decision_workflow: dict[str, Any] | None,
    max_items: int,
    truth_packet: dict[str, Any] | None,
    answer_title: str | None = None,
) -> str:
    from app.services.legal_assistant.answer_formatter import format_policy_lookup_answer_standard

    units = collect_normalized_units_policy(normalized_bundle)
    sel = select_answer_pattern(message=message, source_type="policy_manual", normalized_units=units)
    pid = str(sel.get("pattern_id") or PATTERN_STANDARD)
    conf = str(sel.get("confidence") or "low")
    use_standard = (
        not malone_smart_answer_patterns_enabled()
        or should_fallback_to_standard_pattern(
            pattern_id=pid,
            confidence=conf,
            items=items,
            normalized_units=units,
        )
        or pid == PATTERN_STANDARD
    )
    trace: dict[str, Any] = {**sel, "smart_patterns_enabled": malone_smart_answer_patterns_enabled()}

    if use_standard:
        text = format_policy_lookup_answer_standard(
            items,
            max_items=max_items,
            normalized_bundle=normalized_bundle,
            answer_title=answer_title,
        )
        trace["rendered_pattern"] = "standard"
        trace["fallback_to_standard"] = True
    else:
        dispatch = {
            "requirement": requirement_pattern.render_policy,
            "workflow": workflow_pattern.render_policy,
            "exception": exception_pattern.render_policy,
            "source_locator": source_locator_pattern.render_policy,
        }
        fn = dispatch.get(pid)
        if fn is None:
            text = format_policy_lookup_answer_standard(
                items,
                max_items=max_items,
                normalized_bundle=normalized_bundle,
                answer_title=answer_title,
            )
            trace["rendered_pattern"] = "standard"
            trace["fallback_to_standard"] = True
        else:
            if pid == "workflow":
                text = fn(
                    message=message,
                    items=items,
                    normalized_bundle=normalized_bundle,
                    decision_workflow=decision_workflow,
                    max_items=max_items,
                    answer_title=answer_title,
                )
            else:
                text = fn(
                    message=message,
                    items=items,
                    normalized_bundle=normalized_bundle,
                    max_items=max_items,
                    answer_title=answer_title,
                )
            trace["rendered_pattern"] = pid
            trace["fallback_to_standard"] = False

    lines = text.split("\n")
    _append_decision(lines, decision_workflow)
    _append_copilot(lines, truth_packet)
    out = "\n".join(lines)
    if truth_packet is not None:
        truth_packet["answer_pattern"] = pattern_trace_to_dict(trace)
        pm = truth_packet.setdefault("packet_meta", {})
        pm["answer_pattern_rendered"] = trace.get("rendered_pattern")
        pm["answer_pattern_selected"] = trace.get("pattern_id")
        pm["answer_pattern_confidence"] = trace.get("confidence")
        rp = trace.get("rendered_pattern")
        if rp and rp != "standard":
            from app.services.legal_assistant.guardrails import smart_answer_pattern_forbidden_claims

            forb = list(truth_packet.get("forbidden_claims") or [])
            forb.extend(smart_answer_pattern_forbidden_claims())
            truth_packet["forbidden_claims"] = forb[:80]
    return out
