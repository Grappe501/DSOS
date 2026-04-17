"""Business-layer ingest jobs, events, and persistence helpers."""

from __future__ import annotations

import datetime as dt
import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.ingestion_control import IngestionJob, IngestionJobEvent
from app.models.models import gen_id


def create_job(
    db: Session,
    *,
    ingestion_source_id: str,
    parser_profile_key: str,
    ingestion_source_version_id: str | None = None,
    meta: dict[str, Any] | None = None,
) -> IngestionJob:
    now = dt.datetime.utcnow()
    job = IngestionJob(
        id=gen_id(),
        ingestion_source_id=ingestion_source_id,
        ingestion_source_version_id=ingestion_source_version_id,
        parser_profile_key=parser_profile_key,
        status="running",
        stage="start",
        started_at=now,
        meta_json=json.dumps(meta or {}, ensure_ascii=False),
        counts_json="{}",
    )
    db.add(job)
    db.flush()
    append_event(db, job.id, "job_created", {"parser_profile_key": parser_profile_key})
    return job


def mark_job_completed(
    db: Session,
    job: IngestionJob,
    *,
    counts: dict[str, Any] | None = None,
    meta_patch: dict[str, Any] | None = None,
) -> None:
    job.status = "completed"
    job.stage = "completed"
    job.finished_at = dt.datetime.utcnow()
    if counts is not None:
        job.counts_json = json.dumps(counts, ensure_ascii=False)
    if meta_patch:
        cur = json.loads(job.meta_json or "{}")
        cur.update(meta_patch)
        job.meta_json = json.dumps(cur, ensure_ascii=False)
    append_event(db, job.id, "job_completed", {"counts": counts or {}})


def mark_job_failed(db: Session, job: IngestionJob, message: str) -> None:
    job.status = "failed"
    job.stage = "failed"
    job.error_message = message
    job.finished_at = dt.datetime.utcnow()
    append_event(db, job.id, "job_failed", {"message": message})


def link_legal_job(db: Session, job: IngestionJob, legal_ingestion_job_id: str) -> None:
    job.linked_legal_ingestion_job_id = legal_ingestion_job_id
    append_event(db, job.id, "linked_legal_job", {"legal_ingestion_job_id": legal_ingestion_job_id})


def append_event(db: Session, job_id: str, event_type: str, payload: dict[str, Any]) -> None:
    ev = IngestionJobEvent(
        id=gen_id(),
        ingestion_job_id=job_id,
        event_type=event_type,
        payload_json=json.dumps(payload, ensure_ascii=False),
    )
    db.add(ev)
    db.flush()
