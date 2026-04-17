"""Workflow extraction + assembly (deterministic, no DB)."""

from __future__ import annotations

from app.services.legal_assistant.answer_formatter import format_legal_lookup_answer
from app.services.workflow_assembly.action_plan import enrich_action_steps_with_extraction, augment_decision_plan_with_assembly
from app.services.workflow_extraction import extract_workflow_fields_from_text


def test_numbered_steps_extracted_in_order():
    text = """Prerequisites: Cart stocked.\n\n1. Verify order.\n2. Check label.\n3. Deliver to floor."""
    ex = extract_workflow_fields_from_text(text)
    nums = ex.get("numbered_steps") or []
    assert len(nums) >= 3
    assert nums[0]["step_order"] == 1
    assert nums[1]["step_order"] == 2


def test_role_owner_when_language_present():
    ex = extract_workflow_fields_from_text("The pharmacist must verify. Pharmacy technician may assist.")
    roles = ex.get("role_hints") or []
    keys = {r.get("role_key") for r in roles}
    assert "pharmacist" in keys or "pharmacy_technician" in keys


def test_checkpoint_and_stop_extraction():
    ex = extract_workflow_fields_from_text(
        "Verify the order matches the MAR. Stop if the medication is not listed. Notify the supervisor if unsure."
    )
    assert ex.get("checkpoints") or ex.get("stop_conditions")


def test_escalation_trigger():
    ex = extract_workflow_fields_from_text("Escalate to compliance if the audit fails.")
    assert ex.get("escalation_triggers")


def test_branch_condition():
    ex = extract_workflow_fields_from_text("If the patient is allergic, discontinue and notify the physician.")
    assert ex.get("branch_conditions")


def test_assembly_produces_ordered_plan_fields():
    units = [
        {
            "id": "u1",
            "normalized_unit_type": "workflow_step",
            "plain_language_summary": "1. Wash hands.\n2. Don PPE.",
            "title": "SOP",
            "source_type": "sop_workflow",
        }
    ]
    steps = [
        {
            "order": 1,
            "kind": "workflow_unit",
            "summary": "Wash hands.",
            "unit_id": "u1",
            "normalized_unit_type": "workflow_step",
        }
    ]
    enriched = enrich_action_steps_with_extraction(steps, units)
    assert enriched[0].get("workflow_extraction")


def test_augment_plan_has_merged_views():
    plan = {
        "roles": [],
        "conditions": [],
        "exceptions": [],
        "escalations": [{"kind": "note", "text": "Call PIC"}],
        "action_steps": [
            {
                "order": 1,
                "summary": "x",
                "unit_id": "u1",
                "workflow_extraction": extract_workflow_fields_from_text(
                    "Escalate to compliance if inventory mismatch."
                ),
            }
        ],
        "partial_workflow": True,
        "partial_workflow_reason": "test",
        "source_evidence_map": {},
    }
    out = augment_decision_plan_with_assembly(plan)
    assert "workflow_extraction_assessment" in out
    assert "workflow_escalation_lines_merged" in out


def test_sparse_extraction_fallback_flag():
    from app.services.workflow_assembly.fallback import assess_workflow_extraction_fallback

    steps = [
        {
            "workflow_extraction": {"extraction_confidence": "low"},
        }
    ]
    a = assess_workflow_extraction_fallback(steps, partial_workflow=True)
    assert a.get("use_minimal_workflow_guidance") is True


def test_legal_formatter_preserves_citations():
    items = [
        {
            "citation_key": "L-1",
            "legal_unit_chunk_id": "c1",
            "snippet": "Statute text",
            "page_start": 1,
            "page_end": 1,
        }
    ]
    text = format_legal_lookup_answer(items, message="")
    assert "Citation:" in text
    assert "L-1" in text
