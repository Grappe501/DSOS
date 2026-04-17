"""Internal company knowledge intake: discovery, classification, manifest, batch validation."""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base


def _memory_db():
    import app.models.ingestion_control  # noqa: F401
    import app.models.knowledge_normalization  # noqa: F401
    import app.models.legal_handbook  # noqa: F401
    import app.models.models  # noqa: F401

    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    return sessionmaker(bind=eng)()


def test_discover_intake_deterministic_order(tmp_path) -> None:
    from app.services.internal_company_ingest.intake_discovery import discover_intake_files

    (tmp_path / "policy_manual").mkdir()
    (tmp_path / "sop_workflow").mkdir()
    (tmp_path / "policy_manual" / "a.md").write_text("# A\n", encoding="utf-8")
    (tmp_path / "sop_workflow" / "b.md").write_text("# B\n", encoding="utf-8")
    files = discover_intake_files(str(tmp_path))
    assert len(files) == 2
    assert files[0].relative_path < files[1].relative_path


def test_classify_policy_and_sop() -> None:
    from app.services.ingestion_control.source_types import POLICY_MANUAL, SOP_WORKFLOW
    from app.services.internal_company_ingest.classification import classify_intake_file

    p = classify_intake_file(
        relative_folder="policy_manual",
        filename="x.md",
        file_path="/tmp/x.md",
        content_preview="# Policy",
    )
    assert p.source_type == POLICY_MANUAL
    assert p.active_candidate is True
    assert p.review_recommendation.startswith("ready")

    s = classify_intake_file(
        relative_folder="sop_workflow",
        filename="sop.md",
        file_path="/tmp/sop.md",
        content_preview="runbook steps",
    )
    assert s.source_type == SOP_WORKFLOW
    assert s.ingestion_priority == "high"


def test_unknown_folder_defaults_with_warning() -> None:
    from app.services.ingestion_control.source_types import GENERAL_REFERENCE
    from app.services.internal_company_ingest.classification import classify_intake_file

    u = classify_intake_file(
        relative_folder="custom_unknown",
        filename="n.md",
        file_path="/tmp/n.md",
    )
    assert u.source_type == GENERAL_REFERENCE
    assert "unknown_folder" in u.classification_reason


def test_pdf_marked_inactive() -> None:
    from app.services.internal_company_ingest.classification import classify_intake_file

    p = classify_intake_file(
        relative_folder="policy_manual",
        filename="scan.pdf",
        file_path="/tmp/scan.pdf",
    )
    assert p.active_candidate is False
    assert "pdf" in p.notes.lower()


def test_manifest_entry_fields() -> None:
    from app.services.internal_company_ingest.classification import classify_intake_file
    from app.services.internal_company_ingest.intake_discovery import DiscoveredFile
    from app.services.internal_company_ingest.manifest_builder import manifest_entry_from_discovery

    df = DiscoveredFile(absolute_path="/x/y/z.md", relative_path="policy_manual/z.md", folder_segment="policy_manual", filename="z.md")
    cls = classify_intake_file(relative_folder="policy_manual", filename="z.md", file_path="/x/y/z.md")
    m = manifest_entry_from_discovery(df, cls)
    assert m["source_type"] == "policy_manual"
    assert m["parser_profile"] == "policy_manual"
    assert "review_recommendation" in m
    assert "ingestion_priority" in m
    assert m["active_candidate"] is True


def test_batch_dry_run_pass(tmp_path) -> None:
    from app.services.internal_company_ingest.orchestration import run_internal_company_batch

    (tmp_path / "policy_manual").mkdir()
    (tmp_path / "policy_manual" / "p.md").write_text("# T\nbody\n", encoding="utf-8")
    db = _memory_db()
    out = run_internal_company_batch(
        db,
        intake_root=str(tmp_path),
        dry_run=True,
        emit_manifest_path=None,
        emit_report_path=None,
    )
    assert out["batch_validation_status"] in ("PASS", "PASS_WITH_WARNINGS")
    assert out["file_count"] == 1
    assert out["entries"][0]["ingest_status"] == "dry_run"


def test_batch_empty_warns() -> None:
    from app.services.internal_company_ingest.orchestration import run_internal_company_batch

    db = _memory_db()
    import tempfile

    empty = tempfile.mkdtemp()
    try:
        out = run_internal_company_batch(db, intake_root=empty, dry_run=True, emit_manifest_path=None, emit_report_path=None)
        assert "no_files_discovered" in (out.get("warnings") or [])
    finally:
        os.rmdir(empty)
