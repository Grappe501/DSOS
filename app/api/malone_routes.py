from __future__ import annotations

import time

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.services.audit_service import write_audit
from app.services.deterministic_registry import list_actions
from app.services.elevenlabs_service import (
    ElevenLabsTTSError,
    is_tts_configured,
    synthesize_speech_mp3,
    voice_status_payload,
)
from app.services.malone_service import handle_malone_request
from app.services.proposal_service import list_recent_proposals, serialize_proposal_record

router = APIRouter(prefix="/api/malone", tags=["malone"])


class MaloneChatRequest(BaseModel):
    message: str


class MaloneTTSRequest(BaseModel):
    text: str = Field(..., min_length=1)
    voice_id: str | None = None


@router.get("/voice/status")
def malone_voice_status(current=Depends(get_current_user)):
    """Expose whether server-side TTS is available (no secrets)."""
    _actor, _role = current
    return voice_status_payload()


@router.post("/tts")
def malone_text_to_speech(
    payload: MaloneTTSRequest,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    """
    Authenticated proxy to ElevenLabs. Returns MP3 bytes; API key never leaves the server.
    """
    actor, _role_name = current
    if not is_tts_configured():
        raise HTTPException(
            status_code=503,
            detail="TTS is not configured. Set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID.",
        )

    start = time.time()
    try:
        audio = synthesize_speech_mp3(payload.text, voice_id=payload.voice_id)
    except ElevenLabsTTSError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    duration_ms = int((time.time() - start) * 1000)
    write_audit(
        db,
        action="malone.tts.completed",
        entity_type="malone_voice",
        entity_id=None,
        actor_user_id=getattr(actor, "id", None),
        meta_json={
            "text_length": len((payload.text or "").strip()),
            "audio_bytes": len(audio),
            "duration_ms": duration_ms,
        },
    )

    return Response(
        content=audio,
        media_type="audio/mpeg",
        headers={"Cache-Control": "no-store"},
    )


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