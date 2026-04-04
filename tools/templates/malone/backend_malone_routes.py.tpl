"""{generated_note} - Malone API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_actor_context, require_roles
from app.services.malone_service import handle_malone_request

router = APIRouter(prefix="/api/malone", tags=["malone"])


class MaloneChatRequest(BaseModel):
    message: str


@router.post("/chat")
def malone_chat(
    payload: MaloneChatRequest,
    actor=Depends(get_actor_context),
):
    return handle_malone_request(payload.message, actor=actor)


@router.get("/agents")
def list_agents(
    current=Depends(require_roles("owner", "admin")),
):
    return []
