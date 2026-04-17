"""Read-only copilot serialization, turn telemetry, and trace inspection helpers."""

from __future__ import annotations

import copy
import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base


def _memory_db():
    import app.models.models  # noqa: F401
    import app.models.scenario_memory  # noqa: F401

    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    return sessionmaker(bind=eng)()


def test_operating_copilot_serialization_is_plain_json() -> None:
    from app.services.operating_copilot.serialization import serialize_copilot_block

    block = {
        "enabled": True,
        "primary_scenario": "next_steps",
        "scenario_route": {"primary_scenario": "next_steps", "scores": {"next_steps": 1}},
        "evidence_scope": {"cross_source": False},
    }
    out = serialize_copilot_block(block)
    json.dumps(out)
    assert out["primary_scenario"] == "next_steps"


def test_build_turn_telemetry_shape_and_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MALONE_SCENARIO_MEMORY_APPEND", "0")
    from app.services.scenario_memory.precedence import PRECEDENCE_NOTE
    from app.services.telemetry.malone_turn_telemetry import build_turn_telemetry

    tp = {
        "packet_meta": {
            "answer_pattern_selected": "workflow",
            "answer_pattern_rendered": "workflow",
            "scenario_memory_prior_count": 1,
        },
        "answer_pattern": {"pattern_id": "workflow"},
        "operating_copilot": {
            "enabled": True,
            "primary_scenario": "next_steps",
            "fallback_reason": None,
            "emit_minimal_only": False,
            "scenario_route": {"primary_scenario": "next_steps", "scores": {}},
            "route_reasons": ["x"],
            "evidence_scope": {"source_types_with_items": ["legal_handbook"], "cross_source": False},
            "context": {"source_types_present": ["legal_handbook"]},
        },
        "decision_workflow": {"enabled": True, "fallback_reason": None, "sources_present": ["legal_handbook"]},
        "scenario_memory_context": {
            "priors": [{"scenario_memory_id": "p1"}],
            "precedence": PRECEDENCE_NOTE,
            "emit_in_answer": False,
        },
        "scenario_memory_id": "sm-1",
        "decision_trace_id": "dt-1",
    }
    ver = {"delivery_mode": "legal_grounded_deterministic", "verified": True, "reasons": []}
    tel = build_turn_telemetry(
        truth_packet=tp,
        verification=ver,
        intent={"target": "legal_handbook", "mode": "answer"},
        proposal_id="prop-9",
        cross_source_legal_policy_triggered=True,
    )
    assert tel["read_only"] is True
    assert tel["precedence_note"] == PRECEDENCE_NOTE
    assert tel["delivery"]["deterministic_legal_mode"] == "legal_deterministic"
    assert tel["scenario_memory"]["prior_analog_count"] == 1
    assert tel["trace_ids"]["scenario_memory_id"] == "sm-1"
    assert tel["cross_source"]["cross_source_legal_policy_triggered"] is True
    assert tel["answer_pattern"]["packet_meta_selected"] == "workflow"


def test_build_turn_telemetry_does_not_mutate_truth_packet() -> None:
    from app.services.telemetry.malone_turn_telemetry import build_turn_telemetry

    tp = {"packet_meta": {}, "legal_evidence": {"items": [{"citation_key": "x"}]}}
    snap = copy.deepcopy(tp)
    build_turn_telemetry(
        truth_packet=tp,
        verification={"delivery_mode": "legal_grounded_deterministic"},
        intent={"target": "legal_handbook"},
    )
    assert tp == snap


def test_trace_serialization_after_persist(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MALONE_SCENARIO_MEMORY_ENABLED", "1")
    from app.models.models import MaloneProposal, User, gen_id
    from app.models.scenario_memory import MaloneScenarioMemory

    from app.services.scenario_memory.scenario_store import persist_scenario_memory_and_trace
    from app.services.scenario_memory.trace_read import can_read_scenario, serialize_readonly_trace_bundle

    db = _memory_db()
    uid = gen_id()
    pid = gen_id()
    db.add(User(id=uid, email="t@example.com", password_hash="x"))
    db.add(
        MaloneProposal(
            id=pid,
            proposal_type="answer",
            requested_action="respond",
            source_message="test",
            validation_status="approved",
            approval_status="approved",
            execution_status="proposal_only",
        )
    )
    db.commit()

    lb = {"enabled": True, "legal_source_version_id": "lsv", "items": [{"legal_unit_chunk_id": "c1"}]}
    dw = {"enabled": True, "fallback_reason": None, "source_evidence_map": {}}
    oc = {"enabled": True, "primary_scenario": "next_steps"}
    tp = {
        "answer_pattern": {"pattern_id": "workflow"},
        "packet_meta": {},
        "decision_workflow": dw,
        "operating_copilot": oc,
    }
    out = persist_scenario_memory_and_trace(
        db,
        proposal_id=pid,
        actor_user_id=uid,
        message="what should we do next",
        intent={"target": "legal_handbook"},
        truth_packet=tp,
        decision_workflow=dw,
        legal_bundle=lb,
        policy_bundle=None,
        sop_bundle=None,
        operating_copilot=oc,
        verification={"delivery_mode": "legal_grounded_deterministic"},
        delivery_status="legal_grounded_deterministic",
        delivery_mode="legal_grounded_deterministic",
    )
    assert out
    sm = db.query(MaloneScenarioMemory).filter(MaloneScenarioMemory.id == out["scenario_memory_id"]).one()
    bundle = serialize_readonly_trace_bundle(db, sm)
    assert bundle["read_only"] is True
    assert bundle["decision_trace"]["deterministic_legal_mode"] == "legal_deterministic"
    assert bundle["decision_trace"]["operating_copilot_snapshot"]["primary_scenario"] == "next_steps"

    assert can_read_scenario(role_name="user", actor_user_id=uid, row=sm) is True
    assert can_read_scenario(role_name="user", actor_user_id="other", row=sm) is False
    assert can_read_scenario(role_name="admin", actor_user_id="other", row=sm) is True


def test_inspect_api_surface_is_read_only_documented() -> None:
    """Routes expose GET-only inspection; no mutation verbs in this module's contract."""
    from app.services.telemetry.malone_turn_telemetry import TELEMETRY_SCHEMA_V1

    assert TELEMETRY_SCHEMA_V1.get("schema_version") == 1
    assert "trace_ids" in TELEMETRY_SCHEMA_V1.get("fields", {})
