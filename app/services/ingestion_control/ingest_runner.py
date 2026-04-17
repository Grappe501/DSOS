"""
Orchestrates business ingestion jobs: registry row → profile dispatch → validation → optional promotion.

``legal_handbook`` delegates to the existing Arkansas pipeline without forking it.
``policy_manual`` (and scaffold profiles sharing its executor) write ``ingestion_segments``.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Literal

from sqlalchemy.orm import Session

from app.models.ingestion_control import IngestionSegment, IngestionSourceVersion
from app.models.models import gen_id
from app.services.ingestion_control import ingest_jobs
from app.services.ingestion_control.parser_profiles import (
    PROFILE_CONTRACT_RULES,
    PROFILE_GENERAL_REFERENCE,
    PROFILE_LEGAL_HANDBOOK,
    PROFILE_MEETING_MEMORY,
    PROFILE_POLICY_MANUAL,
    PROFILE_SOP_WORKFLOW,
    PROFILE_TRAINING_MODULE,
    get_profile,
)
from app.services.ingestion_control.promotion import promote_source_version
from app.services.ingestion_control.source_locator import path_exists, resolve_path
from app.services.ingestion_control.source_registry import create_source_version, get_or_create_source
from app.services.ingestion_control.tagging import tag_source_version_from_map
from app.services.ingestion_control.validation import (
    ValidationPayload,
    persist_validation,
    validate_legal_handbook_ingest,
    validate_policy_manual_segments,
)
from app.services.legal_ingestion.arkansas_pipeline import ingest_arkansas_handbook_pdf

PromotionMode = Literal["none", "if_pass", "if_pass_or_warn"]


_NON_LEGAL_PROFILES_USING_TEXT_SPLITTER = frozenset(
    {
        PROFILE_POLICY_MANUAL,
        PROFILE_SOP_WORKFLOW,
        PROFILE_TRAINING_MODULE,
        PROFILE_CONTRACT_RULES,
        PROFILE_MEETING_MEMORY,
        PROFILE_GENERAL_REFERENCE,
    },
)


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _split_markdownish_sections(raw: str) -> list[tuple[str | None, str]]:
    """
    Split on lines that look like markdown headings (# …).
    Returns list of (heading, body) in order.
    """
    lines = raw.replace("\r\n", "\n").split("\n")
    sections: list[tuple[str | None, str]] = []
    cur_heading: str | None = None
    buf: list[str] = []
    heading_re = re.compile(r"^(#{1,6})\s+(.*)$")

    def flush() -> None:
        nonlocal buf, cur_heading
        body = "\n".join(buf).strip()
        if body or cur_heading is not None:
            sections.append((cur_heading, body if body else ""))
        buf = []

    for line in lines:
        m = heading_re.match(line)
        if m:
            flush()
            cur_heading = m.group(2).strip()
            buf = []
        else:
            buf.append(line)
    flush()
    if not sections:
        return [(None, raw.strip())]
    return sections


def ingest_generic_text_profile(
    db: Session,
    *,
    source_id: str,
    file_path: str,
    version_label: str,
    parser_profile_key: str,
    title: str,
) -> dict[str, Any]:
    path = resolve_path(file_path)
    if not path_exists(path):
        return {"status": "failed", "reason": "file_not_found", "path": path}
    checksum = _sha256_file(path)
    raw = open(path, encoding="utf-8", errors="replace").read()
    sections = _split_markdownish_sections(raw)
    ver = create_source_version(
        db,
        ingestion_source_id=source_id,
        version_label=version_label,
        parser_profile_key=parser_profile_key,
        content_checksum=checksum,
        storage_uri=f"file://{path}",
        status="draft",
        retrieval_ready=False,
        meta={"title": title, "segment_count_expected": len(sections)},
    )
    db.flush()
    for i, (heading, body) in enumerate(sections):
        anchor = None
        if heading:
            anchor = re.sub(r"[^a-zA-Z0-9]+", "-", heading.lower()).strip("-")[:80] or None
        seg = IngestionSegment(
            id=gen_id(),
            ingestion_source_version_id=ver.id,
            ordinal=i,
            heading=heading,
            body_text=body,
            anchor_key=anchor,
            retrieval_ready=False,
            meta_json=json.dumps({"parser_profile": parser_profile_key}, ensure_ascii=False),
        )
        db.add(seg)
    db.flush()
    return {
        "status": "completed",
        "ingestion_source_version_id": ver.id,
        "segment_count": len(sections),
        "content_checksum": checksum,
    }


def run_business_ingest(
    db: Session,
    *,
    stable_key: str,
    source_type: str,
    parser_profile_key: str,
    source_path: str,
    title: str,
    business_domain: str = "general",
    owner_steward: str | None = None,
    authority_tier: str = "internal",
    version_label: str = "v1",
    run_validation: bool = True,
    promotion_mode: PromotionMode = "none",
    dimensional_tags: dict[str, str] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    kwargs reserved for profile-specific options (e.g. legal PDF overrides).
    """
    _ = kwargs
    get_profile(parser_profile_key)  # validate
    src, _ = get_or_create_source(
        db,
        stable_key=stable_key,
        source_type=source_type,
        title=title,
        business_domain=business_domain,
        owner_steward=owner_steward,
        authority_tier=authority_tier,
    )
    job = ingest_jobs.create_job(
        db,
        ingestion_source_id=src.id,
        parser_profile_key=parser_profile_key,
        meta={"source_path": source_path},
    )

    precheck_ok = path_exists(resolve_path(source_path))
    outcome: dict[str, Any] = {
        "business_job_id": job.id,
        "ingestion_source_id": src.id,
        "parser_profile_key": parser_profile_key,
    }

    try:
        if parser_profile_key == PROFILE_LEGAL_HANDBOOK:
            path = resolve_path(source_path)
            precheck_ok = path_exists(path)
            result = ingest_arkansas_handbook_pdf(
                db,
                pdf_path=path,
                stable_key=stable_key,
                document_title=title,
                version_label=version_label,
            )
            outcome.update(result)
            if result.get("status") != "completed":
                ingest_jobs.mark_job_failed(db, job, result.get("reason") or "legal_ingest_failed")
                vpayload = validate_legal_handbook_ingest(
                    db,
                    legal_source_version_id=result.get("legal_source_version_id"),
                    ingest_succeeded=False,
                    precheck_ok=precheck_ok,
                )
                if run_validation:
                    persist_validation(db, ingestion_job_id=job.id, payload=vpayload)
                    job.overall_validation_status = vpayload.overall()
                db.commit()
                outcome["validation_status"] = job.overall_validation_status
                return outcome

            db.refresh(job)
            ingest_jobs.link_legal_job(db, job, str(result["job_id"]))
            biz_ver = create_source_version(
                db,
                ingestion_source_id=src.id,
                version_label=version_label,
                parser_profile_key=parser_profile_key,
                content_checksum=None,
                storage_uri=f"file://{path}",
                legal_document_id=result.get("legal_document_id"),
                legal_source_version_id=result.get("legal_source_version_id"),
                status="validated",
                retrieval_ready=False,
                meta={"linked_legal_job_id": result.get("job_id")},
            )
            job.ingestion_source_version_id = biz_ver.id
            ingest_jobs.mark_job_completed(
                db,
                job,
                counts={
                    "families": result.get("family_count"),
                    "chunks": result.get("chunk_count"),
                    "citations": result.get("citation_count"),
                },
            )
            vpayload = validate_legal_handbook_ingest(
                db,
                legal_source_version_id=result.get("legal_source_version_id"),
                ingest_succeeded=True,
                precheck_ok=precheck_ok,
            )
            if run_validation:
                pv = persist_validation(db, ingestion_job_id=job.id, payload=vpayload)
                job.overall_validation_status = pv.overall_status
            if dimensional_tags:
                tag_source_version_from_map(db, ingestion_source_version_id=biz_ver.id, tags=dimensional_tags)
            outcome["status"] = "completed"
            outcome["ingestion_source_version_id"] = biz_ver.id
            outcome["validation_status"] = job.overall_validation_status
            _maybe_promote(db, biz_ver.id, job.overall_validation_status or "", promotion_mode)
            db.commit()
            return outcome

        if parser_profile_key in _NON_LEGAL_PROFILES_USING_TEXT_SPLITTER:
            res = ingest_generic_text_profile(
                db,
                source_id=src.id,
                file_path=source_path,
                version_label=version_label,
                parser_profile_key=parser_profile_key,
                title=title,
            )
            outcome.update(res)
            if res.get("status") != "completed":
                ingest_jobs.mark_job_failed(db, job, res.get("reason") or "generic_ingest_failed")
                vp = validate_policy_manual_segments(segment_count=0, checksum_present=False)
                if run_validation:
                    persist_validation(db, ingestion_job_id=job.id, payload=vp)
                    job.overall_validation_status = vp.overall()
                db.commit()
                outcome["validation_status"] = job.overall_validation_status
                return outcome

            biz_ver_id = res["ingestion_source_version_id"]
            job.ingestion_source_version_id = biz_ver_id
            ingest_jobs.mark_job_completed(db, job, counts={"segments": res["segment_count"]})
            vp = validate_policy_manual_segments(
                segment_count=int(res["segment_count"]),
                checksum_present=bool(res.get("content_checksum")),
            )
            if run_validation:
                pv = persist_validation(db, ingestion_job_id=job.id, payload=vp)
                job.overall_validation_status = pv.overall_status
            if dimensional_tags:
                tag_source_version_from_map(db, ingestion_source_version_id=biz_ver_id, tags=dimensional_tags)
            db.commit()
            outcome["status"] = "completed"
            outcome["ingestion_source_version_id"] = biz_ver_id
            outcome["validation_status"] = job.overall_validation_status
            _maybe_promote(db, biz_ver_id, job.overall_validation_status or "", promotion_mode)
            db.commit()
            return outcome

        ingest_jobs.mark_job_failed(db, job, f"unsupported_parser_profile:{parser_profile_key}")
        db.commit()
        outcome["status"] = "failed"
        return outcome

    except Exception as exc:  # noqa: BLE001 — surface to job row
        ingest_jobs.mark_job_failed(db, job, str(exc))
        if run_validation:
            p = ValidationPayload(failures=[f"exception:{exc}"])
            persist_validation(db, ingestion_job_id=job.id, payload=p)
            job.overall_validation_status = p.overall()
        db.commit()
        outcome["status"] = "failed"
        outcome["error"] = str(exc)
        return outcome


def _maybe_promote(db: Session, version_id: str, validation_status: str, mode: PromotionMode) -> None:
    if mode == "none" or not validation_status:
        return
    if validation_status == "FAIL":
        return
    if mode == "if_pass" and validation_status != "PASS":
        return
    if mode == "if_pass_or_warn" and validation_status not in ("PASS", "PASS_WITH_WARNINGS"):
        return
    promote_source_version(db, ingestion_source_version_id=version_id, to_status="promoted_active", reason="auto_promotion")
