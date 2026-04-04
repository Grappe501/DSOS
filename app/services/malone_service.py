from __future__ import annotations

import time
from typing import Any

from sqlalchemy.orm import Session

from app.services.audit_service import log_malone_action
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
from app.services.schedule_service import list_schedules
from app.services.truth_packet_service import build_truth_packet


MAX_SCHEDULE_ROWS = 100


def _actor_payload(actor: Any, role_name: str) -> dict[str, Any]:
    return {
        "id": getattr(actor, "id", None),
        "email": getattr(actor, "email", None),
        "role": role_name,
        "department": getattr(actor, "department", None),
    }


def _serialize_schedule(row: Any) -> dict[str, Any]:
    return {
        "id": getattr(row, "id", None),
        "title": getattr(row, "title", None),
        "assigned_to": getattr(row, "assigned_to", None),
        "department": getattr(row, "department", None),
        "status": getattr(row, "status", None),
        "start_time": getattr(row, "start_time", None).isoformat()
        if getattr(row, "start_time", None)
        else None,
        "end_time": getattr(row, "end_time", None).isoformat()
        if getattr(row, "end_time", None)
        else None,
    }


def _execute_schedule_read(
    *,
    db: Session,
    actor: Any,
    role_name: str,
) -> dict[str, Any]:
    rows = list_schedules(
        db,
        actor=actor,
        role_name=role_name,
        department=None,
    )[:MAX_SCHEDULE_ROWS]

    serialized = [_serialize_schedule(row) for row in rows]

    return {
        "type": "schedule_list",
        "count": len(serialized),
        "items": serialized,
    }


def _execute_schedule_analysis(
    *,
    db: Session,
    actor: Any,
    role_name: str,
) -> dict[str, Any]:
    rows = list_schedules(
        db,
        actor=actor,
        role_name=role_name,
        department=None,
    )[:MAX_SCHEDULE_ROWS]

    counts = {
        "scheduled": 0,
        "draft": 0,
        "submitted": 0,
        "cancelled": 0,
    }

    for row in rows:
        status = getattr(row, "status", None)
        if status in counts:
            counts[status] += 1

    return {
        "type": "schedule_analysis",
        "total": len(rows),
        "by_status": counts,
    }


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

    if allow_web_search:
        log_malone_action(
            db,
            action="malone.web_search.requested",
            proposal_id=proposal_record.id,
            actor=actor_payload,
            meta_json={
                "enabled": web_search_enabled,
                "reason": truth_packet.get("retrieval_rules", {}).get("web_search_reason"),
            },
        )

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
                "status": render_result.status,
                "duration_ms": duration_ms,
                "web_search_used": render_result.web_search_used,
                "web_source_count": len(render_result.web_sources),
            },
        )

        if allow_web_search:
            log_malone_action(
                db,
                action="malone.web_search.completed" if render_result.web_search_used else "malone.web_search.rejected",
                proposal_id=proposal_record.id,
                actor=actor_payload,
                meta_json={
                    "web_search_used": render_result.web_search_used,
                    "web_source_count": len(render_result.web_sources),
                    "source_urls": [source.get("url") for source in render_result.web_sources],
                },
            )

    except OpenAIServiceError as exc:
        rendered_output, verification, delivery_status = _build_render_fallback(
            fallback_answer=fallback_answer,
            reason=str(exc),
        )

        log_malone_action(
            db,
            action="malone.render.rejected",
            proposal_id=proposal_record.id,
            actor=actor_payload,
            meta_json={"reason": str(exc)},
        )

        if allow_web_search:
            log_malone_action(
                db,
                action="malone.web_search.rejected",
                proposal_id=proposal_record.id,
                actor=actor_payload,
                meta_json={"reason": str(exc)},
            )

        return rendered_output, verification, delivery_status

    verification = verify_rendered_response(
        truth_packet=truth_packet,
        render_payload=rendered_payload,
    )

    log_malone_action(
        db,
        action="malone.render.verified" if verification["verified"] else "malone.render.rejected",
        proposal_id=proposal_record.id,
        actor=actor_payload,
        meta_json={
            "delivery_mode": verification["delivery_mode"],
            "reasons": verification["reasons"],
            "grounding_refs": verification["grounding_refs"],
            "source_refs": verification.get("source_refs", []),
        },
    )

    if verification["delivery_mode"] == "llm_verified_web":
        delivery_status = "llm_verified_web"
    elif verification["verified"]:
        delivery_status = "llm_verified"
    else:
        delivery_status = "deterministic_only"

    return rendered_payload, verification, delivery_status


def handle_malone_request(
    *,
    db: Session,
    message: str,
    actor: Any,
    role_name: str,
) -> dict[str, Any]:
    intent = classify_intent(message)
    actor_payload = _actor_payload(actor, role_name)

    proposal = build_proposal_envelope(
        proposal_type=intent["mode"],
        requested_action=intent["action"],
        candidate_output={
            "message": message,
            "intent": intent,
        },
        actor=actor_payload,
    )

    proposal_record = create_proposal_record(
        db=db,
        proposal=proposal,
        source_message=message,
        target=intent.get("target"),
    )

    log_malone_action(
        db,
        action="malone.proposal.created",
        proposal_id=proposal_record.id,
        actor=actor_payload,
        meta_json=intent,
    )

    validation = validate_proposal_envelope(proposal=proposal)
    proposal["validation_status"] = "approved" if validation["is_valid"] else "rejected"

    proposal_record = update_proposal_record(
        db=db,
        proposal_record=proposal_record,
        validation_status=proposal["validation_status"],
        approval_status="not_required" if validation["is_valid"] else "pending",
        execution_status="blocked" if not validation["is_valid"] else "proposal_only",
        validation_payload=validation,
    )

    log_malone_action(
        db,
        action="malone.proposal.validated",
        proposal_id=proposal_record.id,
        actor=actor_payload,
        meta_json={
            "is_valid": validation["is_valid"],
            "reasons": validation["reasons"],
        },
    )

    result: dict[str, Any] | None = None
    status = "rejected" if not validation["is_valid"] else "proposal_only"

    if validation["is_valid"]:
        target = intent.get("target")

        if target == "schedules" and intent["action"] == "respond":
            result = _execute_schedule_read(
                db=db,
                actor=actor,
                role_name=role_name,
            )
            status = "executed"

        elif target == "schedules" and intent["action"] == "analyze":
            result = _execute_schedule_analysis(
                db=db,
                actor=actor,
                role_name=role_name,
            )
            status = "executed"

    proposal_record = update_proposal_record(
        db=db,
        proposal_record=proposal_record,
        execution_status=status,
        result_payload=result,
    )

    log_malone_action(
        db,
        action="malone.proposal.executed" if status == "executed" else "malone.proposal.recorded",
        proposal_id=proposal_record.id,
        actor=actor_payload,
        meta_json={
            "execution_status": status,
            "target": intent.get("target"),
            "result_type": result.get("type") if result else None,
        },
    )

    truth_packet = build_truth_packet(
        message=message,
        actor=actor_payload,
        intent=intent,
        proposal=proposal,
        validation=validation,
        result=result,
        status=status,
    )

    rendered_output, verification, delivery_status = _deliver_rendered_response(
        db=db,
        proposal_record=proposal_record,
        actor_payload=actor_payload,
        truth_packet=truth_packet,
    )

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
        "delivery": {
            "answer": verification.get("delivery_answer"),
            "mode": verification.get("delivery_mode"),
            "sources": rendered_output.get("web_sources", []),
        },
        "proposal_record": serialize_proposal_record(proposal_record),
        "truth_packet": truth_packet,
        "rendered_output": rendered_output,
        "verification": verification,
    }