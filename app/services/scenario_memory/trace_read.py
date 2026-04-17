"""Read-only access to persisted scenario memory and decision traces (no mutations)."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.scenario_memory import MaloneDecisionTrace, MaloneScenarioMemory
from app.services.scenario_memory.trace_serialization import loads_safe


def actor_may_read_all_traces(role_name: str) -> bool:
    return role_name in {"owner", "admin"}


def can_read_scenario(
    *,
    role_name: str,
    actor_user_id: str | None,
    row: MaloneScenarioMemory,
) -> bool:
    if actor_may_read_all_traces(role_name):
        return True
    if not actor_user_id or not row.actor_user_id:
        return False
    return str(row.actor_user_id) == str(actor_user_id)


def list_recent_scenarios(
    db: Session,
    *,
    actor_user_id: str | None,
    role_name: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    q = db.query(MaloneScenarioMemory).order_by(MaloneScenarioMemory.created_at.desc())
    if not actor_may_read_all_traces(role_name):
        q = q.filter(MaloneScenarioMemory.actor_user_id == actor_user_id)
    rows = q.limit(max(1, min(limit, 100))).all()
    out: list[dict[str, Any]] = []
    for r in rows:
        stypes = loads_safe(r.source_types_json, [])
        out.append(
            {
                "id": r.id,
                "proposal_id": r.proposal_id,
                "actor_user_id": r.actor_user_id,
                "scenario_type": r.scenario_type,
                "intent_target": r.intent_target,
                "memory_status": r.memory_status,
                "delivery_mode": r.delivery_mode,
                "delivery_status": r.delivery_status,
                "source_types": stypes if isinstance(stypes, list) else [],
                "created_at": str(r.created_at),
                "updated_at": str(r.updated_at),
            }
        )
    return out


def _maybe_truncate_json_obj(obj: Any, *, max_chars: int) -> Any:
    raw = json.dumps(obj, ensure_ascii=False, default=str)
    if len(raw) <= max_chars:
        return obj
    return {
        "_truncated": True,
        "_approx_chars": len(raw),
        "preview": raw[: max_chars // 2],
    }


def serialize_readonly_trace_bundle(
    db: Session,
    row: MaloneScenarioMemory,
    *,
    max_json_chars: int = 120_000,
) -> dict[str, Any]:
    tr = (
        db.query(MaloneDecisionTrace)
        .filter(MaloneDecisionTrace.scenario_memory_id == row.id)
        .one_or_none()
    )

    scenario_payload = {
        "id": row.id,
        "proposal_id": row.proposal_id,
        "actor_user_id": row.actor_user_id,
        "prompt_preview": (row.prompt_text or "")[:2000],
        "prompt_fingerprint": row.prompt_fingerprint,
        "scenario_type": row.scenario_type,
        "intent_target": row.intent_target,
        "memory_status": row.memory_status,
        "review_audit_status": row.review_audit_status,
        "delivery_mode": row.delivery_mode,
        "delivery_status": row.delivery_status,
        "source_types": loads_safe(row.source_types_json, []),
        "source_version_snapshot": _maybe_truncate_json_obj(
            loads_safe(row.source_version_snapshot_json, {}),
            max_chars=max_json_chars,
        ),
        "meta_json": _maybe_truncate_json_obj(loads_safe(row.meta_json, {}), max_chars=max_json_chars),
        "created_at": str(row.created_at),
        "updated_at": str(row.updated_at),
    }

    if tr is None:
        return {
            "read_only": True,
            "scenario_memory": scenario_payload,
            "decision_trace": None,
        }

    trace_payload: dict[str, Any] = {
        "id": tr.id,
        "scenario_memory_id": tr.scenario_memory_id,
        "deterministic_legal_mode": tr.deterministic_legal_mode,
        "answer_pattern": _maybe_truncate_json_obj(loads_safe(tr.answer_pattern_json, {}), max_chars=max_json_chars),
        "decision_workflow": _maybe_truncate_json_obj(loads_safe(tr.decision_workflow_json, {}), max_chars=max_json_chars),
        "source_evidence_map": _maybe_truncate_json_obj(loads_safe(tr.source_evidence_map_json, {}), max_chars=max_json_chars),
        "normalized_unit_refs": loads_safe(tr.normalized_unit_refs_json, []),
        "fallback_flags": _maybe_truncate_json_obj(loads_safe(tr.fallback_flags_json, {}), max_chars=max_json_chars),
        "packet_meta_snapshot": _maybe_truncate_json_obj(loads_safe(tr.packet_meta_snapshot_json, {}), max_chars=max_json_chars),
        "operating_copilot_snapshot": _maybe_truncate_json_obj(
            loads_safe(tr.operating_copilot_snapshot_json, {}) if tr.operating_copilot_snapshot_json else {},
            max_chars=max_json_chars,
        ),
        "verification_snapshot": _maybe_truncate_json_obj(loads_safe(tr.verification_snapshot_json, {}), max_chars=max_json_chars),
        "meta_json": _maybe_truncate_json_obj(loads_safe(tr.meta_json, {}), max_chars=max_json_chars),
        "created_at": str(tr.created_at),
    }

    return {
        "read_only": True,
        "scenario_memory": scenario_payload,
        "decision_trace": trace_payload,
    }


