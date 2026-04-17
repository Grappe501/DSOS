"""Orchestrate scan → classify → ingest → optional normalization → reports."""

from __future__ import annotations

import os
from typing import Any, Literal

from sqlalchemy.orm import Session

from app.services.ingestion_control.ingest_runner import run_business_ingest
from app.services.internal_company_ingest.classification import classify_intake_file
from app.services.internal_company_ingest.intake_discovery import discover_intake_files
from app.services.internal_company_ingest.manifest_builder import manifest_entry_from_discovery, write_json
from app.services.knowledge_normalization.normalization_runner import run_normalization
from app.services.knowledge_normalization.normalizer_registry import PROFILE_POLICY_MANUAL_NORM
from app.services.legal_ingestion.ingest_validate_status import decide_overall_status

PromotionMode = Literal["none", "if_pass", "if_pass_or_warn"]


def _read_preview(path: str, n: int = 4000) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(n)
    except OSError:
        return ""


def _normalize_if_applicable(
    db: Session,
    *,
    ingest_out: dict[str, Any],
    source_type: str,
) -> dict[str, Any] | None:
    """Policy/SOP segment paths: reuse policy_manual normalization profile."""
    if ingest_out.get("status") != "completed":
        return None
    if source_type not in ("policy_manual", "sop_workflow"):
        return None
    vid = ingest_out.get("ingestion_source_version_id")
    sid = ingest_out.get("ingestion_source_id")
    if not vid or not sid:
        return None
    return run_normalization(
        db,
        source_type="policy_manual",
        profile_key=PROFILE_POLICY_MANUAL_NORM,
        ingestion_source_version_id=str(vid),
        ingestion_source_id=str(sid),
    )


def run_internal_company_batch(
    db: Session,
    *,
    intake_root: str,
    dry_run: bool = True,
    promotion_mode: PromotionMode = "none",
    version_label: str = "v1",
    emit_manifest_path: str | None = None,
    emit_report_path: str | None = None,
    run_normalization_after_ingest: bool = True,
) -> dict[str, Any]:
    """
    Scan intake folder, classify, optionally ingest each active candidate.

    Does not bypass ``run_business_ingest`` or source registration.
    """
    root = os.path.abspath(intake_root)
    discovered = discover_intake_files(root)
    manifest_entries: list[dict[str, Any]] = []
    runs: list[dict[str, Any]] = []
    failures: list[str] = []
    warnings: list[str] = []

    for df in discovered:
        preview = _read_preview(df.absolute_path)
        cls = classify_intake_file(
            relative_folder=df.folder_segment,
            filename=df.filename,
            file_path=df.absolute_path,
            content_preview=preview,
        )
        entry = manifest_entry_from_discovery(df, cls)
        manifest_entries.append(entry)

        if not cls.active_candidate:
            warnings.append(f"skipped_inactive:{df.relative_path}")
            entry["ingest_status"] = "skipped"
            entry["batch_validation"] = "PASS_WITH_WARNINGS"
            continue

        if dry_run:
            entry["ingest_status"] = "dry_run"
            entry["batch_validation"] = "PASS"
            continue

        title = str(entry["source_title"])
        out = run_business_ingest(
            db,
            stable_key=entry["proposed_stable_key"],
            source_type=cls.source_type,
            parser_profile_key=cls.parser_profile_key,
            source_path=df.absolute_path,
            title=title,
            business_domain=cls.business_domain,
            authority_tier=cls.authority_tier,
            version_label=version_label,
            run_validation=True,
            promotion_mode=promotion_mode,
            dimensional_tags={"internal_category": cls.internal_category, "intake": "internal_company_knowledge"},
        )
        entry["ingestion_result"] = {k: v for k, v in out.items() if k != "ingestion_source_id"}
        entry["ingestion_source_id"] = out.get("ingestion_source_id")
        norm_summary = None
        if run_normalization_after_ingest:
            try:
                norm_summary = _normalize_if_applicable(db, ingest_out=out, source_type=cls.source_type)
                if norm_summary:
                    db.commit()
            except Exception as exc:  # noqa: BLE001
                db.rollback()
                warnings.append(f"normalization_exception:{df.relative_path}:{exc!s}")
                norm_summary = {"error": str(exc)}
        entry["normalization_run"] = norm_summary
        vs = out.get("validation_status") or ""
        st = out.get("status")
        if st != "completed":
            failures.append(f"ingest_failed:{df.relative_path}:{st}")
            entry["ingest_status"] = "failed"
        elif vs == "FAIL":
            failures.append(f"validation_fail:{df.relative_path}")
            entry["ingest_status"] = "validation_fail"
        elif vs == "PASS_WITH_WARNINGS":
            warnings.append(f"validation_warn:{df.relative_path}")
            entry["ingest_status"] = "completed_with_warnings"
        else:
            entry["ingest_status"] = "completed"

        runs.append({"relative_path": df.relative_path, "result": out})
        entry["review_handoff"] = {
            "governance": "use_malone_review_api",
            "artifact_hint": "ingestion_source_version",
            "version_id": out.get("ingestion_source_version_id"),
        }

    # Per-entry batch_validation
    for e in manifest_entries:
        if "batch_validation" not in e:
            st = e.get("ingest_status", "")
            if st == "completed":
                e["batch_validation"] = "PASS"
            elif st == "completed_with_warnings":
                e["batch_validation"] = "PASS_WITH_WARNINGS"
            elif st == "failed" or st == "validation_fail":
                e["batch_validation"] = "FAIL"
            else:
                e["batch_validation"] = "PASS"

    overall_failures = [f for f in failures if f]
    overall_warnings = list(warnings)
    if not discovered:
        overall_warnings.append("no_files_discovered")
    batch_status = decide_overall_status(overall_failures, overall_warnings)

    aggregate = {
        "intake_root": root,
        "dry_run": dry_run,
        "file_count": len(discovered),
        "manifest_entry_count": len(manifest_entries),
        "batch_validation_status": batch_status,
        "failures": overall_failures,
        "warnings": overall_warnings,
        "entries": manifest_entries,
        "runs_summary": runs if not dry_run else [],
    }

    if emit_manifest_path:
        write_json(emit_manifest_path, aggregate)
    if emit_report_path:
        write_json(emit_report_path, aggregate)
    return aggregate
