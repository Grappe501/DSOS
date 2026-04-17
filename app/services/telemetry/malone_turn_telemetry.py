"""Per-turn Malone telemetry: routing, patterns, fallbacks, evidence scope (observational only)."""

from __future__ import annotations

from typing import Any

from app.services.scenario_memory.precedence import PRECEDENCE_NOTE

TELEMETRY_SCHEMA_V1: dict[str, Any] = {
    "schema_version": 1,
    "description": "Observational summary of routing, patterns, and trace pointers; does not drive answers.",
    "fields": {
        "read_only": "Always true for API/UI consumption.",
        "precedence_note": "Human-readable precedence reminder (non-authoritative).",
        "scenario_route": "Operating-copilot primary scenario + router payload.",
        "operating_copilot": "Enabled flag, fallbacks, evidence_scope summary.",
        "decision_workflow": "Workflow block summary (fallbacks, sources_present).",
        "answer_pattern": "Pattern id + packet_meta pattern labels.",
        "fallbacks": "Copilot/workflow/verification fallback signals.",
        "evidence_scope": "Source types and cross_source from copilot evidence scope.",
        "cross_source": "Evidence-scope cross-source vs legal cross-source policy gate.",
        "delivery": "delivery_mode, deterministic_legal_mode bucket, verified.",
        "scenario_memory": "Prior analog counts (secondary context only).",
        "trace_ids": "scenario_memory_id and decision_trace_id when persisted.",
        "inspect_routes": "Relative URLs for read-only trace listing/detail.",
    },
}


def _deterministic_legal_mode_label(delivery_mode: str | None) -> str:
    dm = str(delivery_mode or "")
    if dm == "legal_grounded_deterministic":
        return "legal_deterministic"
    if dm in ("policy_grounded_deterministic", "sop_grounded_deterministic"):
        return "non_legal_deterministic"
    return "non_deterministic"


def build_turn_telemetry(
    *,
    truth_packet: dict[str, Any],
    verification: dict[str, Any] | None,
    intent: dict[str, Any],
    proposal_id: str | None = None,
    cross_source_legal_policy_triggered: bool = False,
) -> dict[str, Any]:
    """
    Summarize inspectable routing/metadata for the current turn.

    Pure function: does not read the database or mutate inputs.
    """
    tp = truth_packet if isinstance(truth_packet, dict) else {}
    ver = verification if isinstance(verification, dict) else {}
    pm = tp.get("packet_meta") if isinstance(tp.get("packet_meta"), dict) else {}
    oc = tp.get("operating_copilot") if isinstance(tp.get("operating_copilot"), dict) else {}
    dw = tp.get("decision_workflow") if isinstance(tp.get("decision_workflow"), dict) else {}
    ap = tp.get("answer_pattern") if isinstance(tp.get("answer_pattern"), dict) else {}
    smc = tp.get("scenario_memory_context") if isinstance(tp.get("scenario_memory_context"), dict) else {}
    priors = smc.get("priors") if isinstance(smc.get("priors"), list) else []

    ev_scope = oc.get("evidence_scope") if isinstance(oc.get("evidence_scope"), dict) else {}
    ctx = oc.get("context") if isinstance(oc.get("context"), dict) else {}
    stypes_ctx = ctx.get("source_types_present") if isinstance(ctx.get("source_types_present"), list) else []
    cross_from_scope = bool(ev_scope.get("cross_source"))
    cross_from_guidance = False
    g = oc.get("guidance") if isinstance(oc.get("guidance"), dict) else {}
    sup = g.get("supporting_sources") if isinstance(g.get("supporting_sources"), dict) else {}
    if sup.get("cross_source") is True:
        cross_from_guidance = True

    scenario_route = oc.get("scenario_route") if isinstance(oc.get("scenario_route"), dict) else {}

    delivery_mode = ver.get("delivery_mode")

    return {
        "schema_version": 1,
        "read_only": True,
        "precedence_note": PRECEDENCE_NOTE,
        "intent": {
            "target": intent.get("target"),
            "mode": intent.get("mode"),
        },
        "proposal_id": proposal_id,
        "scenario_route": {
            "primary_scenario": oc.get("primary_scenario"),
            "router_payload": scenario_route,
            "route_reasons": list(oc.get("route_reasons") or [])[:40],
        },
        "operating_copilot": {
            "enabled": bool(oc.get("enabled")),
            "primary_scenario": oc.get("primary_scenario"),
            "fallback_reason": oc.get("fallback_reason"),
            "emit_minimal_only": bool(oc.get("emit_minimal_only")),
            "evidence_scope": ev_scope,
            "source_types_present": stypes_ctx,
        },
        "decision_workflow": {
            "enabled": bool(dw.get("enabled")),
            "fallback_reason": dw.get("fallback_reason"),
            "sources_present": list(dw.get("sources_present") or [])[:40],
            "partial_workflow": dw.get("partial_workflow"),
        },
        "answer_pattern": {
            "pattern_id": ap.get("pattern_id"),
            "packet_meta_selected": pm.get("answer_pattern_selected"),
            "packet_meta_rendered": pm.get("answer_pattern_rendered"),
        },
        "fallbacks": {
            "operating_copilot": oc.get("fallback_reason"),
            "decision_workflow": dw.get("fallback_reason"),
            "verification_reasons": list(ver.get("reasons") or [])[:20],
        },
        "evidence_scope": {
            "source_types_with_items": list(ev_scope.get("source_types_with_items") or [])[:20],
            "item_counts": ev_scope.get("item_counts") if isinstance(ev_scope.get("item_counts"), dict) else {},
            "cross_source": cross_from_scope or cross_from_guidance,
        },
        "cross_source": {
            "from_evidence_scope": cross_from_scope or cross_from_guidance,
            "cross_source_legal_policy_triggered": bool(cross_source_legal_policy_triggered),
        },
        "delivery": {
            "delivery_mode": delivery_mode,
            "deterministic_legal_mode": _deterministic_legal_mode_label(
                str(delivery_mode) if delivery_mode is not None else None
            ),
            "verified": bool(ver.get("verified")),
        },
        "scenario_memory": {
            "prior_analog_count": len(priors),
            "prior_emit_in_answer": bool(smc.get("emit_in_answer")),
            "packet_meta_prior_count": pm.get("scenario_memory_prior_count"),
        },
        "trace_ids": {
            "scenario_memory_id": tp.get("scenario_memory_id") or pm.get("scenario_memory_id"),
            "decision_trace_id": tp.get("decision_trace_id") or pm.get("decision_trace_id"),
        },
        "inspect_routes": {
            "recent_traces": "/api/malone/inspect/traces",
            "trace_detail": "/api/malone/inspect/traces/{scenario_memory_id}",
        },
    }
