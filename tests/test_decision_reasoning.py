"""Tests for decision/workflow reasoning assembly (no DB)."""

from __future__ import annotations

from app.services.decision_reasoning import build_decision_workflow_block
from app.services.decision_reasoning.decision_router import classify_operational_intent
from app.services.decision_reasoning.fallback import should_emit_structured_sections
from app.services.legal_assistant.answer_formatter import format_legal_lookup_answer


def test_classify_operational_intent_escalation():
    assert classify_operational_intent("When do we escalate to the supervisor?") == "escalation_focus"


def test_classify_operational_intent_steps():
    assert classify_operational_intent("What should we do step by step?") == "step_by_step"


def test_should_emit_requires_no_fallback():
    assert should_emit_structured_sections({"enabled": True, "fallback_reason": "x"}) is False
    assert should_emit_structured_sections({"enabled": True, "roles": []}) is True


def test_build_decision_workflow_merges_legal_and_policy_units():
    legal_bundle = {
        "enabled": True,
        "normalized": {
            "enabled": True,
            "units_by_chunk_id": {
                "c1": [
                    {
                        "id": "u1",
                        "normalized_unit_type": "requirement",
                        "source_type": "legal_handbook",
                        "plain_language_summary": "Keep records.",
                        "applies_to_role": "PIC",
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
        "normalized": {
            "enabled": True,
            "units_by_segment_id": {
                "s1": [
                    {
                        "id": "u2",
                        "normalized_unit_type": "workflow_step",
                        "source_type": "policy_manual",
                        "plain_language_summary": "Notify compliance.",
                        "review_state": "system_generated",
                        "confidence_level": "medium",
                        "ingestion_segment_id": "s1",
                    }
                ]
            },
        },
    }
    block = build_decision_workflow_block(
        message="what should we do",
        legal_bundle=legal_bundle,
        policy_bundle=policy_bundle,
        sop_bundle=None,
        enabled=True,
    )
    assert block.get("enabled") is True
    assert "legal_handbook" in (block.get("sources_present") or [])
    assert "policy_manual" in (block.get("sources_present") or [])
    assert len(block.get("action_steps") or []) >= 1


def test_format_legal_appends_decision_when_emit():
    items = [
        {
            "citation_key": "K1",
            "legal_unit_chunk_id": "c1",
            "snippet": "body",
            "page_start": 1,
            "page_end": 1,
        }
    ]
    dw = {
        "enabled": True,
        "operational_intent": "lookup",
        "roles": [{"role": "PIC", "unit_ids": ["u1"]}],
        "action_steps": [{"order": 1, "summary": "Verify license.", "kind": "workflow_unit"}],
        "conditions": [],
        "exceptions": [],
        "escalations": [],
        "partial_workflow": False,
        "partial_workflow_reason": None,
        "source_evidence_map": {},
    }
    text = format_legal_lookup_answer(items, normalized_bundle=None, decision_workflow=dw)
    assert "Operational guidance" in text
    assert "PIC" in text


def test_build_decision_disabled():
    block = build_decision_workflow_block(
        message="x",
        legal_bundle=None,
        policy_bundle=None,
        sop_bundle=None,
        enabled=False,
    )
    assert block.get("enabled") is False
