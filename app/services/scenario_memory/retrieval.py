"""Retrieve prior scenarios for controlled comparison (secondary to current evidence)."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from sqlalchemy.orm import Session

from app.models.scenario_memory import MaloneDecisionTrace, MaloneScenarioMemory
from app.services.scenario_memory.precedence import should_suppress_prior_due_to_conflict
from app.services.scenario_memory.trace_serialization import loads_safe


def normalize_prompt_for_fingerprint(message: str) -> str:
    t = (message or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t[:8000]


def prompt_fingerprint(message: str) -> str:
    n = normalize_prompt_for_fingerprint(message)
    return hashlib.sha256(n.encode("utf-8")).hexdigest()[:32]


def find_prior_scenario_analogs(
    db: Session,
    *,
    message: str,
    intent: dict[str, Any],
    current_version_snapshot: dict[str, Any],
    limit: int = 5,
    min_similarity: float = 0.08,
) -> list[dict[str, Any]]:
    """
    Heuristic prior matches: same fingerprint first, then token overlap on recent rows.
    Never authoritative; caller must apply precedence rules.
    """
    fp = prompt_fingerprint(message)
    target = str(intent.get("target") or "")
    q = (
        db.query(MaloneScenarioMemory)
        .filter(MaloneScenarioMemory.memory_status == "active")
        .order_by(MaloneScenarioMemory.created_at.desc())
    )
    rows = [r for r in q.limit(400).all()]
    scored: list[tuple[float, Any]] = []
    norm = normalize_prompt_for_fingerprint(message)
    cur_tokens = {x for x in norm.split() if len(x) > 2}

    for row in rows:
        pri_st = loads_safe(row.source_types_json, [])
        sim = 1.0 if row.prompt_fingerprint == fp else _token_sim(cur_tokens, row.prompt_text or "")
        if target and row.intent_target and row.intent_target != target:
            sim *= 0.65
        if sim >= min_similarity:
            conflict = should_suppress_prior_due_to_conflict(
                current_source_versions=current_version_snapshot,
                prior_source_versions=loads_safe(row.source_version_snapshot_json, {}),
            )
            if not conflict and (row.review_audit_status or "").strip().lower() == "approved":
                sim *= 1.08
            scored.append((sim, (row, pri_st, conflict)))

    scored.sort(key=lambda x: -x[0])
    out: list[dict[str, Any]] = []
    for sim, (row, pri_st, conflict) in scored[:limit]:
        tr = db.query(MaloneDecisionTrace).filter(MaloneDecisionTrace.scenario_memory_id == row.id).one_or_none()
        ap = loads_safe(tr.answer_pattern_json, {}) if tr else {}
        out.append(
            {
                "scenario_memory_id": row.id,
                "similarity": round(sim, 4),
                "intent_target_then": row.intent_target,
                "scenario_type_then": row.scenario_type,
                "source_types_then": pri_st,
                "answer_pattern_then": ap.get("pattern_id") or ap.get("rendered_pattern"),
                "created_at": str(row.created_at),
                "source_version_drift_warning": conflict,
                "review_audit_status_then": row.review_audit_status,
                "review_only": True,
            }
        )
    return out


def _token_sim(cur_tokens: set[str], prior_text: str) -> float:
    pt = {x for x in normalize_prompt_for_fingerprint(prior_text).split() if len(x) > 2}
    if not cur_tokens or not pt:
        return 0.0
    return len(cur_tokens & pt) / len(cur_tokens | pt)


def attach_prior_scenario_context(
    packet: dict[str, Any],
    *,
    priors: list[dict[str, Any]],
    precedence_note: str,
) -> dict[str, Any]:
    import os

    emit = os.environ.get("MALONE_SCENARIO_MEMORY_APPEND", "").strip().lower() in ("1", "true", "yes", "on")
    packet["scenario_memory_context"] = {
        "priors": priors,
        "precedence": precedence_note,
        "emit_in_answer": emit,
    }
    pm = packet.get("packet_meta") or {}
    pm["scenario_memory_prior_count"] = len(priors)
    packet["packet_meta"] = pm
    if priors:
        from app.services.legal_assistant.guardrails import scenario_memory_prior_forbidden_claims

        forb = list(packet.get("forbidden_claims") or [])
        forb.extend(scenario_memory_prior_forbidden_claims())
        packet["forbidden_claims"] = forb[:80]
    return packet
