from __future__ import annotations

import time
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import MaloneProposal
from app.services.audit_service import log_malone_action
from app.services.deterministic_actions_schedule import register_schedule_actions
from app.services.deterministic_registry import list_actions
from app.services.intent_service import classify_intent, cross_source_legal_policy_triggered
from app.services.openai_service import (
    OpenAIServiceError,
    is_openai_enabled,
    is_web_search_enabled,
    render_conversational_response,
)
from app.services.proposal_service import (
    build_proposal_envelope,
    create_proposal_record,
    serialize_proposal_record,
    update_proposal_record,
    validate_proposal_envelope,
)
from app.services.render_verifier import (
    build_deterministic_fallback,
    verify_rendered_response,
)
from app.services.legal_assistant.answer_formatter import format_legal_lookup_answer, format_policy_lookup_answer
from app.services.decision_reasoning import build_decision_workflow_block
from app.services.operating_copilot import build_operating_copilot_block, malone_operating_copilot_enabled
from app.services.scenario_memory.evidence_linking import source_version_snapshot
from app.services.scenario_memory.fallback import malone_scenario_memory_priors_enabled
from app.services.scenario_memory.precedence import PRECEDENCE_NOTE
from app.services.scenario_memory.retrieval import attach_prior_scenario_context, find_prior_scenario_analogs
from app.services.scenario_memory.scenario_store import persist_scenario_memory_and_trace
from app.services.legal_evidence_service import (
    build_legal_evidence_bundle,
    build_policy_evidence_bundle,
    build_sop_evidence_bundle,
    enrich_truth_packet_with_decision_workflow,
    enrich_truth_packet_with_operating_copilot,
    enrich_truth_packet_with_legal,
    enrich_truth_packet_with_policy,
    enrich_truth_packet_with_sop,
    malone_cross_source_decision_enabled,
    malone_decision_reasoning_enabled,
    malone_legal_evidence_enabled,
    malone_legal_lookup_enabled,
    malone_policy_evidence_enabled,
    malone_policy_lookup_enabled,
    malone_sop_evidence_enabled,
    malone_sop_lookup_enabled,
    persist_legal_answer_trace,
)
from app.services.review_feedback.governance_hints import build_governance_hints_for_turn
from app.services.telemetry import build_turn_telemetry
from app.services.truth_packet_service import build_truth_packet
from app.services.workflow_service import (
    DEFAULT_WORKFLOW_NAME,
    get_workflow_instance,
    serialize_workflow_instance,
    start_workflow_instance,
)

# -----------------------------------------------------------------------------
# Bootstrap deterministic registry
# -----------------------------------------------------------------------------
def _bootstrap_registry() -> None:
    register_schedule_actions()


_bootstrap_registry()


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _actor_payload(actor: Any, role_name: str) -> dict[str, Any]:
    return {
        "id": getattr(actor, "id", None),
        "email": getattr(actor, "email", None),
        "role": role_name,
        "department": getattr(actor, "department", None),
    }


def _resolve_action_key(intent: dict[str, Any]) -> str | None:
    action_key_hint = intent.get("action_key_hint")
    if isinstance(action_key_hint, str) and action_key_hint.strip():
        return action_key_hint.strip()

    target = intent.get("target")
    action = intent.get("action")

    if target == "schedules" and action == "respond":
        return "schedule.read"
    if target == "schedules" and action == "analyze":
        return "schedule.analyze"

    return None


def _build_render_fallback(
    *,
    fallback_answer: str,
    reason: str,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    verification = {
        "verified": False,
        "reasons": [reason],
        "grounding_refs": [],
        "source_refs": [],
        "verified_source_urls": [],
        "fallback_answer": fallback_answer,
        "delivery_answer": fallback_answer,
        "delivery_mode": "deterministic_fallback",
    }
    return {}, verification, "deterministic_only"


def _deliver_legal_handbook_deterministic(
    *,
    db: Session,
    proposal_record: Any,
    actor_payload: dict[str, Any],
    truth_packet: dict[str, Any],
    message: str,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    bundle = truth_packet.get("legal_evidence") or {}
    items = bundle.get("items") or []
    text = format_legal_lookup_answer(
        items,
        normalized_bundle=bundle.get("normalized"),
        decision_workflow=truth_packet.get("decision_workflow"),
        message=message,
        truth_packet=truth_packet,
    )
    verification = {
        "verified": True,
        "reasons": [],
        "grounding_refs": [],
        "source_refs": [],
        "verified_source_urls": [],
        "fallback_answer": text,
        "delivery_answer": text,
        "delivery_mode": "legal_grounded_deterministic",
    }
    log_malone_action(
        db,
        action="malone.delivery.legal_handbook",
        proposal_id=proposal_record.id,
        actor=actor_payload,
        meta_json={
            "item_count": len(items),
            "legal_source_version_id": bundle.get("legal_source_version_id"),
            "warnings": bundle.get("warnings"),
            "normalized_fallback": (bundle.get("normalized") or {}).get("fallback_reason"),
            "answer_pattern": truth_packet.get("answer_pattern"),
            "operating_copilot": truth_packet.get("operating_copilot"),
        },
    )
    return {}, verification, "legal_grounded_deterministic"


def _deliver_policy_manual_deterministic(
    *,
    db: Session,
    proposal_record: Any,
    actor_payload: dict[str, Any],
    truth_packet: dict[str, Any],
    message: str,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    bundle = truth_packet.get("policy_evidence") or {}
    items = bundle.get("items") or []
    text = format_policy_lookup_answer(
        items,
        normalized_bundle=bundle.get("normalized"),
        decision_workflow=truth_packet.get("decision_workflow"),
        message=message,
        truth_packet=truth_packet,
    )
    verification = {
        "verified": True,
        "reasons": [],
        "grounding_refs": [],
        "source_refs": [],
        "verified_source_urls": [],
        "fallback_answer": text,
        "delivery_answer": text,
        "delivery_mode": "policy_grounded_deterministic",
    }
    log_malone_action(
        db,
        action="malone.delivery.policy_manual",
        proposal_id=proposal_record.id,
        actor=actor_payload,
        meta_json={
            "item_count": len(items),
            "ingestion_source_version_id": bundle.get("ingestion_source_version_id"),
            "warnings": bundle.get("warnings"),
            "normalized_fallback": (bundle.get("normalized") or {}).get("fallback_reason"),
            "answer_pattern": truth_packet.get("answer_pattern"),
            "operating_copilot": truth_packet.get("operating_copilot"),
        },
    )
    return {}, verification, "policy_grounded_deterministic"


def _deliver_sop_workflow_deterministic(
    *,
    db: Session,
    proposal_record: Any,
    actor_payload: dict[str, Any],
    truth_packet: dict[str, Any],
    message: str,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    bundle = truth_packet.get("sop_evidence") or {}
    items = bundle.get("items") or []
    text = format_policy_lookup_answer(
        items,
        normalized_bundle=bundle.get("normalized"),
        decision_workflow=truth_packet.get("decision_workflow"),
        answer_title="SOP / workflow — reference only (confirm with process owners).",
        message=message,
        truth_packet=truth_packet,
    )
    verification = {
        "verified": True,
        "reasons": [],
        "grounding_refs": [],
        "source_refs": [],
        "verified_source_urls": [],
        "fallback_answer": text,
        "delivery_answer": text,
        "delivery_mode": "sop_grounded_deterministic",
    }
    log_malone_action(
        db,
        action="malone.delivery.sop_workflow",
        proposal_id=proposal_record.id,
        actor=actor_payload,
        meta_json={
            "item_count": len(items),
            "ingestion_source_version_id": bundle.get("ingestion_source_version_id"),
            "warnings": bundle.get("warnings"),
            "normalized_fallback": (bundle.get("normalized") or {}).get("fallback_reason"),
            "answer_pattern": truth_packet.get("answer_pattern"),
            "operating_copilot": truth_packet.get("operating_copilot"),
        },
    )
    return {}, verification, "sop_grounded_deterministic"


def _deliver_rendered_response(
    *,
    db: Session,
    proposal_record: Any,
    actor_payload: dict[str, Any],
    truth_packet: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], str]:
    fallback_answer = build_deterministic_fallback(truth_packet=truth_packet)

    allow_web_search = bool(truth_packet.get("retrieval_rules", {}).get("allow_web_search"))
    web_search_enabled = bool(allow_web_search and is_web_search_enabled())

    if not is_openai_enabled():
        rendered_output, verification, delivery_status = _build_render_fallback(
            fallback_answer=fallback_answer,
            reason="openai_not_configured",
        )

        log_malone_action(
            db,
            action="malone.render.skipped",
            proposal_id=proposal_record.id,
            actor=actor_payload,
            meta_json={"reason": "openai_not_configured"},
        )
        return rendered_output, verification, delivery_status

    start = time.time()

    try:
        render_result = render_conversational_response(
            truth_packet=truth_packet,
            allow_web_search=allow_web_search,
        )
        rendered_payload = render_result.to_dict()
        duration_ms = int((time.time() - start) * 1000)

        log_malone_action(
            db,
            action="malone.render.generated",
            proposal_id=proposal_record.id,
            actor=actor_payload,
            meta_json={
                "provider": render_result.provider,
                "model": render_result.model,
                "duration_ms": duration_ms,
                "web_search_used": render_result.web_search_used,
            },
        )

    except OpenAIServiceError as exc:
        return _build_render_fallback(
            fallback_answer=fallback_answer,
            reason=str(exc),
        )

    verification = verify_rendered_response(
        truth_packet=truth_packet,
        render_payload=rendered_payload,
    )

    delivery_status = (
        "llm_verified_web"
        if verification["delivery_mode"] == "llm_verified_web"
        else "llm_verified"
        if verification["verified"]
        else "deterministic_only"
    )

    return rendered_payload, verification, delivery_status


# -----------------------------------------------------------------------------
# MAIN ENTRY
# -----------------------------------------------------------------------------
def handle_malone_request(
    *,
    db: Session,
    message: str,
    actor: Any,
    role_name: str,
) -> dict[str, Any]:
    intent = classify_intent(message)
    actor_payload = _actor_payload(actor, role_name)
    action_key = _resolve_action_key(intent)

    # ---------------------------------------------------------
    # Proposal
    # ---------------------------------------------------------
    proposal = build_proposal_envelope(
        proposal_type=intent["mode"],
        requested_action=intent["action"],
        candidate_output={
            "message": message,
            "intent": intent,
            "action_key": action_key,
        },
        actor=actor_payload,
    )

    proposal_record = create_proposal_record(
        db=db,
        proposal=proposal,
        source_message=message,
        target=intent.get("target"),
    )

    # ---------------------------------------------------------
    # Validate
    # ---------------------------------------------------------
    validation = validate_proposal_envelope(proposal=proposal)

    proposal_record = update_proposal_record(
        db=db,
        proposal_record=proposal_record,
        validation_status="approved" if validation["is_valid"] else "rejected",
        execution_status="blocked" if not validation["is_valid"] else "proposal_only",
        validation_payload=validation,
    )

    # ---------------------------------------------------------
    # Workflow Execution
    # ---------------------------------------------------------
    workflow_instance = None
    status = "rejected" if not validation["is_valid"] else "proposal_only"
    result = None
    deterministic_execution = None
    action_validation = None

    if validation["is_valid"]:
        workflow_instance = start_workflow_instance(
            db,
            workflow_name=DEFAULT_WORKFLOW_NAME,
            entity_type="malone_proposal",
            entity_id=proposal_record.id,
            context={
                "proposal_id": proposal_record.id,
                "message": message,
                "intent": intent,
                "actor": actor_payload,
                "role_name": role_name,
                "action_key": action_key,
                "proposal_validation": validation,
            },
            auto_run=True,
        )

        workflow_instance = get_workflow_instance(db, workflow_instance.id)
        workflow_context = serialize_workflow_instance(workflow_instance).get("context", {})

        action_validation = workflow_context.get("action_validation")
        deterministic_execution = workflow_context.get("deterministic_execution")
        result = workflow_context.get("result")

        # 🔥 CRITICAL STATE HANDLING
        if workflow_instance.status == "blocked_pending_approval":
            status = "pending_approval"

            log_malone_action(
                db,
                action="malone.execution.pending_approval",
                proposal_id=proposal_record.id,
                actor=actor_payload,
                meta_json={
                    "workflow_instance_id": workflow_instance.id,
                },
            )

        elif workflow_instance.status == "blocked":
            status = "blocked"

        elif workflow_instance.status == "completed":
            status = "executed"

        else:
            status = workflow_instance.status

        proposal_record = update_proposal_record(
            db=db,
            proposal_record=proposal_record,
            execution_status=status,
            result_payload=result,
            deterministic_execution_payload=deterministic_execution,
        )

    # ---------------------------------------------------------
    # Truth packet
    # ---------------------------------------------------------
    cross = malone_cross_source_decision_enabled() and cross_source_legal_policy_triggered(message)
    sop_cross = cross and ("[sop]" in message.lower() or "runbook" in message.lower())

    legal_bundle = None
    if malone_legal_evidence_enabled() and (intent.get("target") == "legal_handbook" or cross):
        legal_bundle = build_legal_evidence_bundle(db, message)

    policy_bundle = None
    if malone_policy_evidence_enabled() and (intent.get("target") == "policy_manual" or cross):
        policy_bundle = build_policy_evidence_bundle(db, message)

    sop_bundle = None
    if malone_sop_evidence_enabled() and (intent.get("target") == "sop_workflow" or sop_cross):
        sop_bundle = build_sop_evidence_bundle(db, message)

    truth_packet = build_truth_packet(
        message=message,
        actor=actor_payload,
        intent=intent,
        proposal=proposal,
        validation={
            **validation,
            "action_validation": action_validation,
        },
        result=result,
        status=status,
    )
    truth_packet = enrich_truth_packet_with_legal(
        truth_packet,
        intent=intent,
        legal_evidence_bundle=legal_bundle,
    )
    truth_packet = enrich_truth_packet_with_policy(
        truth_packet,
        intent=intent,
        policy_evidence_bundle=policy_bundle,
    )
    truth_packet = enrich_truth_packet_with_sop(
        truth_packet,
        intent=intent,
        sop_evidence_bundle=sop_bundle,
    )

    decision_block = build_decision_workflow_block(
        message=message,
        legal_bundle=legal_bundle,
        policy_bundle=policy_bundle,
        sop_bundle=sop_bundle,
        enabled=malone_decision_reasoning_enabled(),
    )
    truth_packet = enrich_truth_packet_with_decision_workflow(truth_packet, decision_block)

    copilot_block = build_operating_copilot_block(
        message=message,
        legal_bundle=legal_bundle,
        policy_bundle=policy_bundle,
        sop_bundle=sop_bundle,
        decision_workflow=decision_block,
        enabled=malone_operating_copilot_enabled(),
    )
    truth_packet = enrich_truth_packet_with_operating_copilot(truth_packet, copilot_block)

    if malone_scenario_memory_priors_enabled():
        _vers = source_version_snapshot(
            legal_bundle=legal_bundle,
            policy_bundle=policy_bundle,
            sop_bundle=sop_bundle,
        )
        _priors = find_prior_scenario_analogs(
            db,
            message=message,
            intent=intent,
            current_version_snapshot=_vers,
        )
        truth_packet = attach_prior_scenario_context(
            truth_packet,
            priors=_priors,
            precedence_note=PRECEDENCE_NOTE,
        )

    if malone_legal_evidence_enabled() and intent.get("target") == "legal_handbook" and legal_bundle is not None:
        persist_legal_answer_trace(
            db,
            proposal_id=str(proposal_record.id),
            bundle=legal_bundle,
            query_fingerprint=None,
            verified=bool((legal_bundle.get("items") or [])),
        )

    # ---------------------------------------------------------
    # DELIVERY LOGIC (approval-aware)
    # ---------------------------------------------------------
    if status == "pending_approval":
        delivery = {
            "answer": "This request requires approval before execution.",
            "mode": "approval_required",
            "sources": [],
        }

        rendered_output = {}
        verification = {"verified": True, "delivery_mode": "approval_required"}
        delivery_status = "approval_required"

    elif (
        malone_legal_lookup_enabled()
        and malone_legal_evidence_enabled()
        and intent.get("target") == "legal_handbook"
    ):
        rendered_output, verification, delivery_status = _deliver_legal_handbook_deterministic(
            db=db,
            proposal_record=proposal_record,
            actor_payload=actor_payload,
            truth_packet=truth_packet,
            message=message,
        )
        delivery = {
            "answer": verification.get("delivery_answer"),
            "mode": verification.get("delivery_mode"),
            "sources": [],
        }

    elif (
        malone_policy_lookup_enabled()
        and malone_policy_evidence_enabled()
        and intent.get("target") == "policy_manual"
    ):
        rendered_output, verification, delivery_status = _deliver_policy_manual_deterministic(
            db=db,
            proposal_record=proposal_record,
            actor_payload=actor_payload,
            truth_packet=truth_packet,
            message=message,
        )
        delivery = {
            "answer": verification.get("delivery_answer"),
            "mode": verification.get("delivery_mode"),
            "sources": [],
        }

    elif (
        malone_sop_lookup_enabled()
        and malone_sop_evidence_enabled()
        and intent.get("target") == "sop_workflow"
    ):
        rendered_output, verification, delivery_status = _deliver_sop_workflow_deterministic(
            db=db,
            proposal_record=proposal_record,
            actor_payload=actor_payload,
            truth_packet=truth_packet,
            message=message,
        )
        delivery = {
            "answer": verification.get("delivery_answer"),
            "mode": verification.get("delivery_mode"),
            "sources": [],
        }

    else:
        rendered_output, verification, delivery_status = _deliver_rendered_response(
            db=db,
            proposal_record=proposal_record,
            actor_payload=actor_payload,
            truth_packet=truth_packet,
        )

        delivery = {
            "answer": verification.get("delivery_answer"),
            "mode": verification.get("delivery_mode"),
            "sources": rendered_output.get("web_sources", []),
        }

    proposal_record = update_proposal_record(
        db=db,
        proposal_record=proposal_record,
        delivery_status=delivery_status,
        rendered_output_payload=rendered_output,
        verification_payload=verification,
    )

    trace_ids = persist_scenario_memory_and_trace(
        db,
        proposal_id=str(proposal_record.id),
        actor_user_id=actor_payload.get("id"),
        message=message,
        intent=intent,
        truth_packet=truth_packet,
        decision_workflow=truth_packet.get("decision_workflow"),
        legal_bundle=legal_bundle,
        policy_bundle=policy_bundle,
        sop_bundle=sop_bundle,
        operating_copilot=truth_packet.get("operating_copilot"),
        verification=verification,
        delivery_status=delivery_status,
        delivery_mode=verification.get("delivery_mode") if isinstance(verification, dict) else None,
    )
    if trace_ids:
        pm = truth_packet.setdefault("packet_meta", {})
        pm["scenario_memory_id"] = trace_ids["scenario_memory_id"]
        pm["decision_trace_id"] = trace_ids["decision_trace_id"]
        truth_packet["scenario_memory_id"] = trace_ids["scenario_memory_id"]
        truth_packet["decision_trace_id"] = trace_ids["decision_trace_id"]
        db.commit()

    malone_telemetry = build_turn_telemetry(
        truth_packet=truth_packet,
        verification=verification if isinstance(verification, dict) else {},
        intent=intent,
        proposal_id=str(proposal_record.id),
        cross_source_legal_policy_triggered=bool(cross),
    )
    malone_governance = build_governance_hints_for_turn(db, truth_packet)

    return {
        "mode": intent["mode"],
        "intent": intent,
        "status": status,
        "result": result,
        "deterministic_execution": deterministic_execution,
        "workflow_instance": serialize_workflow_instance(workflow_instance, db=db)
        if workflow_instance
        else None,
        "delivery": delivery,
        "proposal_record": serialize_proposal_record(proposal_record),
        "truth_packet": truth_packet,
        "rendered_output": rendered_output,
        "verification": verification,
        "malone_telemetry": malone_telemetry,
        "malone_governance": malone_governance,
        "capabilities": list_actions(),
    }