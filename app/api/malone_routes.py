from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.services.deterministic_registry import list_actions
from app.services.malone_service import handle_malone_request
from app.services.proposal_service import list_recent_proposals, serialize_proposal_record

router = APIRouter(prefix="/api/malone", tags=["malone"])


class MaloneChatRequest(BaseModel):
    message: str


@router.post("/chat")
def malone_chat(
    payload: MaloneChatRequest,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    actor, role_name = current
    return handle_malone_request(
        db=db,
        message=payload.message,
        actor=actor,
        role_name=role_name,
    )


@router.get("/proposals")
def recent_malone_proposals(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    actor, role_name = current
    actor_user_id = None if role_name in {"owner", "admin"} else getattr(actor, "id", None)
    rows = list_recent_proposals(
        db=db,
        actor_user_id=actor_user_id,
        limit=limit,
    )
    return [serialize_proposal_record(row) for row in rows]


@router.get("/capabilities")
def malone_capabilities(
    current=Depends(get_current_user),
):
    return {
        "actions": list_actions(),
    }


@router.get("/agents")
def list_agents(
    current=Depends(require_roles("owner", "admin")),
):
    return []