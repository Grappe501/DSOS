"""Persist scenario memory + decision trace rows (linked, inspectable)."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.scenario_memory import MaloneDecisionTrace, MaloneScenarioMemory
from app.models.models import gen_id
from app.services.scenario_memory.evidence_linking import (
    normalized_unit_refs_from_decision_workflow,
    source_types_present,
    source_version_snapshot,
)
from app.services.scenario_memory.fallback import should_persist_trace_for_delivery
from app.services.scenario_memory.scenario_classifier import classify_scenario
from app.services.scenario_memory.trace_serialization import dumps_limited, loads_safe


def is_eligible_for_scenario_memory(
    intent: dict[str, Any],
    *,
    legal_bundle: dict[str, Any] | None,
    policy_bundle: dict[str, Any] | None,
    sop_bundle: dict[str, Any] | None,
) -> bool:
    t = intent.get("target")
    if t in ("legal_handbook", "policy_manual", "sop_workflow"):
        return True
    for b in (legal_bundle, policy_bundle, sop_bundle):
        if b and b.get("enabled") and len(b.get("items") or []) > 0:
            return True
    return False


def persist_scenario_memory_and_trace(
    db: Session,
    *,
    proposal_id: str,
    actor_user_id: str | None,
    message: str,
    intent: dict[str, Any],
    truth_packet: dict[str, Any],
    decision_workflow: dict[str, Any] | None,
    legal_bundle: dict[str, Any] | None,
    policy_bundle: dict[str, Any] | None,
    sop_bundle: dict[str, Any] | None,
    operating_copilot: dict[str, Any] | None,
    verification: dict[str, Any] | None,
    delivery_status: str | None,
    delivery_mode: str | None,
) -> dict[str, str] | None:
    from app.services.scenario_memory.fallback import malone_scenario_memory_enabled

    if not malone_scenario_memory_enabled():
        return None
    if not is_eligible_for_scenario_memory(
        intent,
        legal_bundle=legal_bundle,
        policy_bundle=policy_bundle,
        sop_bundle=sop_bundle,
    ):
        return None
    if not should_persist_trace_for_delivery(delivery_status=delivery_status):
        return None

    cls = classify_scenario(message, intent=intent, decision_workflow=decision_workflow)
    stypes = source_types_present(
        legal_bundle=legal_bundle,
        policy_bundle=policy_bundle,
        sop_bundle=sop_bundle,
    )
    versions = source_version_snapshot(
        legal_bundle=legal_bundle,
        policy_bundle=policy_bundle,
        sop_bundle=sop_bundle,
    )
    from app.services.scenario_memory.retrieval import prompt_fingerprint

    fp = prompt_fingerprint(message)
    pm = truth_packet.get("packet_meta") or {}
    answer_pattern = truth_packet.get("answer_pattern") or {}
    det_mode = str(delivery_mode or "")
    if det_mode == "legal_grounded_deterministic":
        legal_mode_flag = "legal_deterministic"
    elif det_mode in ("policy_grounded_deterministic", "sop_grounded_deterministic"):
        legal_mode_flag = "non_legal_deterministic"
    else:
        legal_mode_flag = "non_deterministic"

    dw = decision_workflow or {}
    sem = dw.get("source_evidence_map") if isinstance(dw, dict) else {}
    fb = {
        "decision_workflow_fallback": dw.get("fallback_reason"),
        "operating_copilot_fallback": (operating_copilot or {}).get("fallback_reason"),
        "truth_packet_pattern_meta": {
            "answer_pattern_rendered": pm.get("answer_pattern_rendered"),
            "answer_pattern_selected": pm.get("answer_pattern_selected"),
        },
    }

    scenario = MaloneScenarioMemory(
        id=gen_id(),
        proposal_id=str(proposal_id),
        actor_user_id=actor_user_id,
        prompt_text=(message or "")[:8000],
        prompt_fingerprint=fp,
        scenario_type=cls["scenario_type"],
        intent_target=cls.get("intent_target"),
        source_types_json=json.dumps(stypes, ensure_ascii=False),
        source_version_snapshot_json=json.dumps(versions, ensure_ascii=False, default=str),
        memory_status="active",
        review_audit_status="pending",
        delivery_mode=delivery_mode,
        delivery_status=delivery_status,
        meta_json=dumps_limited(
            {
                "primary_route": cls.get("primary_route"),
                "scenario_route": cls.get("scenario_route"),
                "cross_source": len(stypes) > 1,
            },
            max_chars=120_000,
        ),
    )
    db.add(scenario)
    db.flush()

    trace = MaloneDecisionTrace(
        id=gen_id(),
        scenario_memory_id=scenario.id,
        answer_pattern_json=dumps_limited(answer_pattern, max_chars=80_000),
        deterministic_legal_mode=legal_mode_flag,
        decision_workflow_json=dumps_limited(dw, max_chars=400_000),
        source_evidence_map_json=dumps_limited(sem if isinstance(sem, dict) else {}, max_chars=400_000),
        normalized_unit_refs_json=dumps_limited(normalized_unit_refs_from_decision_workflow(dw), max_chars=120_000),
        fallback_flags_json=dumps_limited(fb, max_chars=80_000),
        packet_meta_snapshot_json=dumps_limited(pm, max_chars=120_000),
        operating_copilot_snapshot_json=dumps_limited(operating_copilot or {}, max_chars=120_000)
        if operating_copilot
        else None,
        verification_snapshot_json=dumps_limited(verification or {}, max_chars=120_000),
        meta_json="{}",
    )
    db.add(trace)
    db.flush()
    return {"scenario_memory_id": scenario.id, "decision_trace_id": trace.id}


def load_trace_bundle(db: Session, scenario_memory_id: str) -> dict[str, Any] | None:
    row = db.query(MaloneDecisionTrace).filter(MaloneDecisionTrace.scenario_memory_id == scenario_memory_id).one_or_none()
    if not row:
        return None
    return {
        "answer_pattern": loads_safe(row.answer_pattern_json, {}),
        "decision_workflow": loads_safe(row.decision_workflow_json, {}),
        "source_evidence_map": loads_safe(row.source_evidence_map_json, {}),
    }
