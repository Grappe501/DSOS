"""Department intake: interactive capture on the single Malone stack (API + storage)."""

from __future__ import annotations

from app.services.department_intake.followup_generator import compute_followup_questions
from app.services.department_intake.intake_session_store import (
    get_session_detail,
    record_answer,
    start_intake_session,
)
from app.services.department_intake.safety import evidence_precedence_rank

__all__ = [
    "compute_followup_questions",
    "get_session_detail",
    "record_answer",
    "start_intake_session",
    "evidence_precedence_rank",
]
