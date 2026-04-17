"""Business operating copilot: scenario routing, cross-source, fallback, formatter (no DB)."""

from __future__ import annotations

import pytest

from app.services.decision_reasoning import build_decision_workflow_block
from app.services.legal_assistant.answer_formatter import format_legal_lookup_answer
from app.services.operating_copilot import (
    build_operating_copilot_block,
    is_operational_copilot_query,
    route_scenario,
)
from app.services.operating_copilot.fallback import should_emit_operating_copilot_section
from app.services.operating_copilot.scenario_router import (
    SCENARIO_ESCALATION,
    SCENARIO_EXCEPTION,
    SCENARIO_NEXT_STEPS,
    SCENARIO_ROLE,
)


@pytest.fixture(autouse=True)
def _enable_copilot_layers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MALONE_DECISION_REASONING_ENABLED", "1")
    monkeypatch.setenv("MALONE_OPERATING_COPILOT_ENABLED", "1")


def _legal_policy_bundles() -> tuple[dict, dict]:
    legal_bundle = {
        "enabled": True,
        "items": [{"legal_unit_chunk_id": "c1", "citation_key": "K1"}],
        "normalized": {
            "enabled": True,
            "units_by_chunk_id": {
                "c1": [
                    {
                        "id": "u1",
                        "normalized_unit_type": "requirement",
                        "source_type": "legal_handbook",
                        "plain_language_summary": "Maintain required records.",
                        "review_state": "system_generated",
                        "confidence_level": "medium",
                        "legal_unit_chunk_id": "c1",
                    }
                ]
            },
        },
    }
    policy_bundle = {
        "enabled": True,
        "items": [{"ingestion_segment_id": "s1"}],
        "normalized": {
            "enabled": True,
            "units_by_segment_id": {
                "s1": [
                    {
                        "id": "u2",
                        "normalized_unit_type": "workflow_step",
                        "source_type": "policy_manual",
                        "plain_language_summary": "Notify compliance within 24 hours.",
                        "review_state": "system_generated",
                        "confidence_level": "medium",
                        "ingestion_segment_id": "s1",
                    }
                ]
            },
        },
    }
    return legal_bundle, policy_bundle


def test_next_step_question_routes_to_next_steps_scenario() -> None:
    r = route_scenario("What is the next step we should take here?", decision_workflow=None)
    assert r["primary_scenario"] == SCENARIO_NEXT_STEPS


def test_role_question_routes_to_role_scenario() -> None:
    r = route_scenario("What does the pharmacist need to do first?", decision_workflow=None)
    assert r["primary_scenario"] == SCENARIO_ROLE


def test_exception_question_routes_to_exception_scenario() -> None:
    r = route_scenario("What if this claim is denied — any exceptions?", decision_workflow=None)
    assert r["primary_scenario"] == SCENARIO_EXCEPTION


def test_escalation_question_routes_to_escalation_scenario() -> None:
    r = route_scenario("When should this go to compliance and who to notify?", decision_workflow=None)
    assert r["primary_scenario"] == SCENARIO_ESCALATION


def test_mixed_legal_policy_preserves_cross_source() -> None:
    lb, pb = _legal_policy_bundles()
    dw = build_decision_workflow_block(
        message="what should we do next",
        legal_bundle=lb,
        policy_bundle=pb,
        sop_bundle=None,
        enabled=True,
    )
    block = build_operating_copilot_block(
        message="what should we do next for operational compliance",
        legal_bundle=lb,
        policy_bundle=pb,
        sop_bundle=None,
        decision_workflow=dw,
        enabled=True,
    )
    assert block.get("enabled") is True
    scope = block.get("evidence_scope") or {}
    assert scope.get("cross_source") is True
    g = block.get("guidance") or {}
    src = g.get("supporting_sources") or {}
    st = src.get("source_types") or []
    assert "legal_handbook" in st and "policy_manual" in st


def test_weak_workflow_support_minimal_fallback_emits_section() -> None:
    """Items present for scope, but no normalized units → thin copilot, safe minimal."""
    thin_legal = {
        "enabled": True,
        "items": [{"legal_unit_chunk_id": "c1"}],
        "normalized": {"enabled": False},
    }
    dw = build_decision_workflow_block(
        message="what should we do next",
        legal_bundle=thin_legal,
        policy_bundle=None,
        sop_bundle=None,
        enabled=True,
    )
    block = build_operating_copilot_block(
        message="what should we do next for operational workflow compliance",
        legal_bundle=thin_legal,
        policy_bundle=None,
        sop_bundle=None,
        decision_workflow=dw,
        enabled=True,
    )
    assert block.get("emit_minimal_only") is True
    assert should_emit_operating_copilot_section(block) is True


def test_legal_smart_answer_preserves_citations_with_copilot_append(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MALONE_SMART_ANSWER_PATTERNS_ENABLED", "0")
    items = [
        {
            "citation_key": "TEST-1",
            "legal_unit_chunk_id": "c1",
            "snippet": "Dangerous drugs shall be stored securely.",
            "page_start": 1,
            "page_end": 1,
        }
    ]
    lb, _ = _legal_policy_bundles()
    dw = build_decision_workflow_block(
        message="what should we do next",
        legal_bundle=lb,
        policy_bundle=None,
        sop_bundle=None,
        enabled=True,
    )
    block = build_operating_copilot_block(
        message="what should we do next",
        legal_bundle=lb,
        policy_bundle=None,
        sop_bundle=None,
        decision_workflow=dw,
        enabled=True,
    )
    truth_packet: dict = {"operating_copilot": block}
    text = format_legal_lookup_answer(
        items,
        normalized_bundle=lb.get("normalized"),
        decision_workflow=dw,
        message="what should we do next",
        truth_packet=truth_packet,
    )
    assert "Citation:" in text
    assert "TEST-1" in text
    assert "Business operating copilot" in text


def test_policy_bundle_surfaces_steps_when_decision_has_action_steps() -> None:
    lb, pb = _legal_policy_bundles()
    dw = build_decision_workflow_block(
        message="who should do this step by step",
        legal_bundle=lb,
        policy_bundle=pb,
        sop_bundle=None,
        enabled=True,
    )
    block = build_operating_copilot_block(
        message="who should do this step by step",
        legal_bundle=lb,
        policy_bundle=pb,
        sop_bundle=None,
        decision_workflow=dw,
        enabled=True,
    )
    assert block.get("enabled") is True
    g = block.get("guidance") or {}
    assert g.get("recommended_next_steps") or g.get("who_should_act") is not None


def test_operational_gate_skips_non_ops_queries_when_no_broad_signals() -> None:
    assert is_operational_copilot_query("Arkansas pharmacy law definition of dangerous drug") is False


def test_disabled_env_returns_disabled_block(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MALONE_OPERATING_COPILOT_ENABLED", "0")
    lb, _ = _legal_policy_bundles()
    dw = build_decision_workflow_block(
        message="what should we do",
        legal_bundle=lb,
        policy_bundle=None,
        sop_bundle=None,
        enabled=True,
    )
    from app.services.operating_copilot.fallback import malone_operating_copilot_enabled

    assert malone_operating_copilot_enabled() is False
    block = build_operating_copilot_block(
        message="what should we do",
        legal_bundle=lb,
        policy_bundle=None,
        sop_bundle=None,
        decision_workflow=dw,
        enabled=malone_operating_copilot_enabled(),
    )
    assert block.get("enabled") is False
