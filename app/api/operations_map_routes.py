"""Department intake + operations map (narrow API; same Malone auth stack)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.operations_map import DepartmentIntakeSession
from app.services.department_intake.intake_session_store import (
    get_session_detail,
    record_answer,
    start_intake_session,
)
from app.services.operations_map.department_store import get_department_map, list_departments
from app.services.operations_map.map_builder import materialize_operations_map

router = APIRouter(prefix="/api/malone/operations-map", tags=["malone-operations-map"])


class IntakeStartBody(BaseModel):
    department_name: str = Field(..., min_length=1, max_length=500)
    department_description: str | None = Field(default=None, max_length=8000)


class IntakeAnswerBody(BaseModel):
    text: str = Field(..., min_length=1, max_length=120_000)
    question_key: str | None = Field(default=None, max_length=120)
    entry_mode: str = Field(default="text", max_length=32)
    transcript_ref: str | None = Field(default=None, max_length=500)


def _is_admin(role: str) -> bool:
    return role in {"owner", "admin"}


@router.post("/intake/sessions")
def operations_map_start_intake(
    payload: IntakeStartBody,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    actor, role_name = current
    uid = getattr(actor, "id", None)
    if not uid:
        raise HTTPException(status_code=400, detail="missing user id")
    try:
        sess = start_intake_session(
            db,
            actor_user_id=str(uid),
            department_name=payload.department_name.strip(),
            department_description=payload.department_description,
        )
        db.commit()
        return {
            "intake_session_id": sess.id,
            "operations_department_id": sess.operations_department_id,
            "proposal_id": sess.proposal_id,
            "scenario_memory_id": sess.scenario_memory_id,
            "governance_note": "Intake is provisional until reviewed; not authoritative over source evidence.",
        }
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/intake/sessions/{session_id}")
def operations_map_get_intake(
    session_id: str,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    actor, role_name = current
    uid = getattr(actor, "id", None)
    try:
        return get_session_detail(
            db,
            session_id=session_id,
            actor_user_id=str(uid) if uid else None,
            is_admin=_is_admin(role_name),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/intake/sessions/{session_id}/answers")
def operations_map_post_answer(
    session_id: str,
    payload: IntakeAnswerBody,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    actor, role_name = current
    uid = getattr(actor, "id", None)
    if not uid:
        raise HTTPException(status_code=400, detail="missing user id")
    try:
        ans = record_answer(
            db,
            session_id=session_id,
            actor_user_id=str(uid),
            answer_text=payload.text,
            question_key=payload.question_key,
            entry_mode=payload.entry_mode,
            transcript_ref=payload.transcript_ref,
        )
        db.commit()
        return {"answer_id": ans.id, "entry_mode": ans.entry_mode, "transcript_ref": ans.transcript_ref}
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/intake/sessions/{session_id}/materialize")
def operations_map_materialize(
    session_id: str,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    actor, role_name = current
    uid = getattr(actor, "id", None)
    if not uid:
        raise HTTPException(status_code=400, detail="missing user id")
    try:
        out = materialize_operations_map(
            db,
            intake_session_id=session_id,
            actor_user_id=str(uid),
            is_admin=_is_admin(role_name),
        )
        db.commit()
        return out
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/intake/sessions/{session_id}/close")
def operations_map_close_session(
    session_id: str,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    actor, role_name = current
    uid = getattr(actor, "id", None)
    q = db.query(DepartmentIntakeSession).filter(DepartmentIntakeSession.id == session_id)
    if not _is_admin(role_name):
        q = q.filter(DepartmentIntakeSession.actor_user_id == str(uid))
    sess = q.one_or_none()
    if sess is None:
        raise HTTPException(status_code=404, detail="session not found")
    sess.status = "closed"
    db.commit()
    return {"intake_session_id": sess.id, "status": sess.status}


@router.get("/departments")
def operations_map_list_departments(
    limit: int = 50,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    return {"departments": list_departments(db, limit=min(max(limit, 1), 200))}


@router.get("/departments/{department_id}/map")
def operations_map_get_map(
    department_id: str,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    try:
        return get_department_map(db, department_id=department_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/inspect/schema")
def operations_map_inspect_schema(current=Depends(require_roles("owner", "admin"))):
    """Describe entities for read-only inspection."""
    _a, _r = current
    return {
        "read_only": True,
        "entities": [
            "operations_departments",
            "department_intake_sessions",
            "department_intake_answers",
            "operations_roles",
            "operations_workflows",
            "operations_system_tools",
            "operations_dependencies",
            "operations_handoffs",
            "operations_escalations",
            "operations_blockers",
            "operations_artifact_refs",
        ],
    }
