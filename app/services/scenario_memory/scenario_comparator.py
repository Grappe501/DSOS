"""Compare current snapshot dicts to a prior persisted scenario (inspectable, non-authoritative)."""

from __future__ import annotations

from typing import Any

from app.services.scenario_memory.trace_serialization import loads_safe


def compare_to_prior_row(
    *,
    current: dict[str, Any],
    prior_scenario_meta: dict[str, Any],
    prior_trace_answer_pattern: dict[str, Any] | None,
    prior_trace_decision: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Structured diff for audit / UX. Does not assert “same scenario”.
    """
    cur_types = list(current.get("source_types") or [])
    pri_types = list(prior_scenario_meta.get("source_types") or [])
    cur_pattern = (current.get("answer_pattern") or {}).get("pattern_id") or current.get("answer_pattern_rendered")
    pri_pattern = None
    if prior_trace_answer_pattern:
        pri_pattern = prior_trace_answer_pattern.get("pattern_id") or prior_trace_answer_pattern.get(
            "rendered_pattern"
        )

    cur_route = (current.get("scenario_classification") or {}).get("primary_route")
    pri_route = prior_scenario_meta.get("primary_route")

    similarity_hint = _jaccard_tokens(
        current.get("prompt_normalized", ""),
        prior_scenario_meta.get("prompt_normalized", ""),
    )

    return {
        "similarity_token_score": round(similarity_hint, 4),
        "source_types_then": pri_types,
        "source_types_now": cur_types,
        "source_types_overlap": sorted(set(pri_types) & set(cur_types)),
        "answer_pattern_then": pri_pattern,
        "answer_pattern_now": cur_pattern,
        "scenario_route_then": pri_route,
        "scenario_route_now": cur_route,
        "decision_workflow_enabled_then": (prior_trace_decision or {}).get("enabled"),
        "decision_workflow_enabled_now": (current.get("decision_workflow") or {}).get("enabled"),
        "weak_match_warning": similarity_hint < 0.12,
        "disclaimer": "Comparison is heuristic; verify all obligations against current sources.",
    }


def _jaccard_tokens(a: str, b: str) -> float:
    sa = {x for x in (a or "").lower().split() if len(x) > 2}
    sb = {x for x in (b or "").lower().split() if len(x) > 2}
    if not sa and not sb:
        return 0.0
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0


def scenario_row_to_meta(row: Any, *, prompt_normalized: str) -> dict[str, Any]:
    st = loads_safe(getattr(row, "source_types_json", "[]"), [])
    meta = loads_safe(getattr(row, "meta_json", "{}"), {})
    return {
        "scenario_id": getattr(row, "id", None),
        "prompt_normalized": prompt_normalized,
        "source_types": st,
        "scenario_type": getattr(row, "scenario_type", None),
        "primary_route": meta.get("primary_route"),
        "intent_target": getattr(row, "intent_target", None),
        "created_at": str(getattr(row, "created_at", "")),
    }
