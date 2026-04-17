"""Scenario memory + decision trace persistence, comparison, precedence (in-memory DB)."""

from __future__ import annotations

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


def test_persist_scenario_memory_and_trace_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MALONE_SCENARIO_MEMORY_ENABLED", "1")
    from app.models.models import MaloneProposal, gen_id
    from app.models.scenario_memory import MaloneDecisionTrace, MaloneScenarioMemory

    from app.services.scenario_memory.scenario_store import persist_scenario_memory_and_trace

    db = _memory_db()
    pid = gen_id()
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

    lb = {
        "enabled": True,
        "legal_source_version_id": "lsv-1",
        "items": [{"legal_unit_chunk_id": "c1"}],
        "normalized": {"enabled": False},
    }
    dw = {
        "enabled": True,
        "fallback_reason": None,
        "source_evidence_map": {"u1": {"lane": "legal_handbook"}},
        "action_steps": [],
    }
    tp = {
        "answer_pattern": {"pattern_id": "workflow", "rendered_pattern": "workflow"},
        "packet_meta": {"answer_pattern_rendered": "workflow"},
        "decision_workflow": dw,
    }
    out = persist_scenario_memory_and_trace(
        db,
        proposal_id=pid,
        actor_user_id=None,
        message="what should we do next about pharmacy workflow",
        intent={"target": "legal_handbook"},
        truth_packet=tp,
        decision_workflow=dw,
        legal_bundle=lb,
        policy_bundle=None,
        sop_bundle=None,
        operating_copilot=None,
        verification={"delivery_mode": "legal_grounded_deterministic"},
        delivery_status="legal_grounded_deterministic",
        delivery_mode="legal_grounded_deterministic",
    )
    assert out is not None
    sm = db.query(MaloneScenarioMemory).filter(MaloneScenarioMemory.id == out["scenario_memory_id"]).one()
    assert "legal_handbook" in sm.source_types_json
    tr = db.query(MaloneDecisionTrace).filter(MaloneDecisionTrace.scenario_memory_id == sm.id).one()
    assert json.loads(tr.decision_workflow_json).get("enabled") is True
    assert "workflow" in tr.answer_pattern_json


def test_decision_trace_includes_source_evidence_map(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MALONE_SCENARIO_MEMORY_ENABLED", "1")
    from app.models.models import MaloneProposal, gen_id
    from app.models.scenario_memory import MaloneDecisionTrace

    from app.services.scenario_memory.scenario_store import persist_scenario_memory_and_trace

    db = _memory_db()
    pid = gen_id()
    db.add(
        MaloneProposal(
            id=pid,
            proposal_type="answer",
            requested_action="respond",
            source_message="x",
            validation_status="approved",
            approval_status="approved",
            execution_status="proposal_only",
        )
    )
    db.commit()
    dw = {"enabled": True, "source_evidence_map": {"uid": {"lane": "policy_manual"}}}
    oid = persist_scenario_memory_and_trace(
        db,
        proposal_id=pid,
        actor_user_id=None,
        message="policy question",
        intent={"target": "policy_manual"},
        truth_packet={"answer_pattern": {}, "packet_meta": {}, "decision_workflow": dw},
        decision_workflow=dw,
        legal_bundle=None,
        policy_bundle={"enabled": True, "ingestion_source_version_id": "pv1", "items": [{}]},
        sop_bundle=None,
        operating_copilot=None,
        verification={},
        delivery_status="x",
        delivery_mode="policy_grounded_deterministic",
    )
    assert oid
    tr = db.query(MaloneDecisionTrace).filter(MaloneDecisionTrace.scenario_memory_id == oid["scenario_memory_id"]).one()
    sem = json.loads(tr.source_evidence_map_json)
    assert "uid" in sem


def test_compare_to_prior_row_structure() -> None:
    from app.services.scenario_memory.scenario_comparator import compare_to_prior_row
    from app.services.scenario_memory.precedence import current_evidence_outranks_memory

    assert current_evidence_outranks_memory() is True
    cur = {
        "source_types": ["legal_handbook", "policy_manual"],
        "answer_pattern": {"pattern_id": "requirement"},
        "answer_pattern_rendered": "requirement",
        "scenario_classification": {"primary_route": "next_steps"},
        "decision_workflow": {"enabled": True},
        "prompt_normalized": "what should we do next for compliance",
    }
    pri = {
        "source_types": ["legal_handbook"],
        "primary_route": "next_steps",
        "prompt_normalized": "what should we do next for licensing",
    }
    diff = compare_to_prior_row(
        current=cur,
        prior_scenario_meta=pri,
        prior_trace_answer_pattern={"pattern_id": "workflow"},
        prior_trace_decision={"enabled": True},
    )
    assert diff["source_types_overlap"] == ["legal_handbook"]
    assert diff.get("weak_match_warning") is not None


def test_precedence_conflict_suppresses_prior_hint() -> None:
    from app.services.scenario_memory.precedence import should_suppress_prior_due_to_conflict

    cur = {"legal_handbook": {"legal_source_version_id": "a"}}
    pri = {"legal_handbook": {"legal_source_version_id": "b"}}
    assert should_suppress_prior_due_to_conflict(current_source_versions=cur, prior_source_versions=pri) is True


def test_find_prior_respects_min_similarity(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MALONE_SCENARIO_MEMORY_ENABLED", "1")
    from app.models.models import MaloneProposal, gen_id
    from app.models.scenario_memory import MaloneScenarioMemory

    from app.services.scenario_memory.retrieval import find_prior_scenario_analogs

    db = _memory_db()
    pid = gen_id()
    db.add(
        MaloneProposal(
            id=pid,
            proposal_type="answer",
            requested_action="respond",
            source_message="z",
            validation_status="approved",
            approval_status="approved",
            execution_status="proposal_only",
        )
    )
    db.commit()
    sm = MaloneScenarioMemory(
        id=gen_id(),
        proposal_id=pid,
        prompt_text="unrelated xyz abc",
        prompt_fingerprint="deadbeef",
        scenario_type="t",
        intent_target="legal_handbook",
        source_types_json="[]",
        source_version_snapshot_json="{}",
    )
    db.add(sm)
    db.commit()

    out = find_prior_scenario_analogs(
        db,
        message="completely different topic about zebras in space",
        intent={"target": "legal_handbook"},
        current_version_snapshot={},
        min_similarity=0.95,
    )
    assert out == []


def test_mixed_source_types_persisted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MALONE_SCENARIO_MEMORY_ENABLED", "1")
    from app.models.models import MaloneProposal, gen_id
    from app.models.scenario_memory import MaloneScenarioMemory

    from app.services.scenario_memory.scenario_store import persist_scenario_memory_and_trace

    db = _memory_db()
    pid = gen_id()
    db.add(
        MaloneProposal(
            id=pid,
            proposal_type="answer",
            requested_action="respond",
            source_message="m",
            validation_status="approved",
            approval_status="approved",
            execution_status="proposal_only",
        )
    )
    db.commit()
    oid = persist_scenario_memory_and_trace(
        db,
        proposal_id=pid,
        actor_user_id=None,
        message="cross",
        intent={"target": "general"},
        truth_packet={"answer_pattern": {}, "packet_meta": {}, "decision_workflow": {"enabled": True}},
        decision_workflow={"enabled": True},
        legal_bundle={"enabled": True, "items": [1], "legal_source_version_id": "L"},
        policy_bundle={"enabled": True, "items": [1], "ingestion_source_version_id": "P"},
        sop_bundle={"enabled": True, "items": [1], "ingestion_source_version_id": "S"},
        operating_copilot=None,
        verification={},
        delivery_status="x",
        delivery_mode="x",
    )
    assert oid
    sm = db.query(MaloneScenarioMemory).filter(MaloneScenarioMemory.id == oid["scenario_memory_id"]).one()
    st = json.loads(sm.source_types_json)
    assert set(st) == {"legal_handbook", "policy_manual", "sop_workflow"}


def test_legal_formatter_still_has_citations(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MALONE_SMART_ANSWER_PATTERNS_ENABLED", "0")
    from app.services.legal_assistant.answer_formatter import format_legal_lookup_answer

    items = [
        {
            "citation_key": "X-1",
            "legal_unit_chunk_id": "c1",
            "snippet": "text",
            "page_start": 1,
            "page_end": 1,
        }
    ]
    tp = {
        "scenario_memory_context": {
            "priors": [{"scenario_memory_id": "old", "similarity": 0.2, "review_only": True}],
            "precedence": "current wins",
            "emit_in_answer": False,
        }
    }
    text = format_legal_lookup_answer(items, message="", truth_packet=tp)
    assert "Citation:" in text
    assert "X-1" in text
