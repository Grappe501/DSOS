from __future__ import annotations

import time
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import MaloneProposal
from app.services.audit_service import log_malone_action
from app.services.deterministic_actions_schedule import register_schedule_actions
from app.services.deterministic_registry import list_actions
from app.services.intent_service import classify_intent
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
        "capabilities": list_actions(),
    }