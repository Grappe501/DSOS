"""
One-command Arkansas ASBP lawbook PDF: family-map validation, full ingest, DB checks, retrieval QA.

Usage (repo root):

  python tracking/scripts/run_arkansas_handbook_ingest_validate.py --pdf "C:\\path\\Lawbook-November-2025.pdf"

See ``tracking/reports/arkansas_handbook_ingest_validate_report.md`` and ``..._state.json`` for output.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# --- Expected Arkansas handbook families (November 2025-style compilation; display labels) ---
EXPECTED_FAMILY_ROWS: list[tuple[str, str]] = [
    ("A", "Pharmacy Practice Act"),
    ("B", "Miscellaneous Statutes Related to Pharmacy"),
    ("C", "Uniform Controlled Substances Act"),
    ("D", "Insurance Policies – Prescription Drug Benefits"),
    ("E", "Food, Drug, and Cosmetic Act"),
    ("F", "Controlled Substances and Legend Drugs"),
    ("G", "Administrative Procedure Act"),
    ("H", "Rules Pertaining to Arkansas Prescription Drug Monitoring Program"),
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _pages_for_span(
    page_map: Any,
    char_start: int | None,
    char_end: int | None,
) -> tuple[int | None, int | None]:
    if page_map is None or char_start is None or char_end is None:
        return None, None
    if char_end <= char_start:
        p = page_map.global_char_to_page(char_start)
        return p, p
    return page_map.span_to_page_range(char_start, char_end)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _write_md_report(
    path: Path,
    *,
    pdf_path: str,
    overall: str,
    state: dict[str, Any],
) -> None:
    fv = state.get("family_validation") or {}
    ing = state.get("ingestion") or {}
    db = state.get("db_checks") or {}
    ret = state.get("retrieval_checks") or {}
    lines = [
        "# Arkansas Handbook Ingest + Validate",
        "",
        "## 1. INPUT PDF",
        "",
        f"- Path: `{pdf_path}`",
        f"- File exists: {state.get('precheck', {}).get('pdf_exists', False)}",
        f"- PDF text extract usable: {state.get('precheck', {}).get('pdf_readable', False)}",
        "",
        "## 2. FAMILY VALIDATION RESULT",
        "",
        f"- Parsed families: **{fv.get('parsed_family_count', 0)}**",
        f"- Title validation (engine): `{json.dumps(fv.get('title_validation') or {}, ensure_ascii=False)}`",
        f"- Missing expected codes: `{fv.get('missing_expected_codes', [])}`",
        f"- Title mismatch codes: `{fv.get('title_mismatch_codes', [])}`",
        "",
        "### Expected families (reference)",
        "",
    ]
    for code, title in EXPECTED_FAMILY_ROWS:
        lines.append(f"- **{code}** — {title}")
    lines.extend(
        [
            "",
            "### Detected families (summary)",
            "",
        ]
    )
    for row in fv.get("families") or []:
        ps, pe = row.get("page_start"), row.get("page_end")
        pg = f"pp. {ps}–{pe}" if ps is not None and pe is not None else "pages unknown"
        lines.append(
            f"- **{row.get('family_code')}** — {(row.get('title') or '')[:120]} — {pg} "
            f"(provenance={row.get('span_provenance')}, confidence={row.get('span_confidence')})"
        )
    lines.extend(
        [
            "",
            "## 3. INGESTION RESULT",
            "",
            f"- Status: `{ing.get('status')}`",
            f"- Job ID: `{ing.get('job_id')}`",
            f"- Legal document ID: `{ing.get('legal_document_id')}`",
            f"- Source version ID: `{ing.get('legal_source_version_id')}`",
            f"- Message / reason: `{ing.get('reason') or ing.get('error') or ''}`",
            "",
            "## 4. DATABASE SANITY CHECKS",
            "",
            f"- Document row: `{db.get('document_found')}`",
            f"- Source version row: `{db.get('version_found')}`",
            f"- Family count: **{db.get('family_count', 0)}**",
            f"- Legal unit count: **{db.get('legal_unit_count', 0)}**",
            f"- Chunk count: **{db.get('chunk_count', 0)}**",
            f"- Citation count: **{db.get('citation_count', 0)}**",
            "",
            "### Target citation probes (optional)",
            "",
        ]
    )
    for k, v in (db.get("target_citations") or {}).items():
        lines.append(f"- `{k}`: found **{v}** row(s)")
    lines.extend(
        [
            "",
            "## 5. RETRIEVAL SANITY CHECKS",
            "",
        ]
    )
    for r in ret.get("queries") or []:
        lines.append(
            f"- **{r.get('label')}** — hits={r.get('hit_count')}, "
            f"scoped_to_version={r.get('scoped_to_version')}, "
            f"has_family_or_cite={r.get('has_family_or_citation_info')}"
        )
    lines.extend(
        [
            "",
            "## 6. OVERALL PASS / FAIL",
            "",
            f"**{overall}**",
            "",
            "### Decision rules (this run)",
            "",
            "- **FAIL** if precheck fails, PDF cannot be extracted, ingest does not complete,",
            "  document/source version rows are missing, core counts are empty, or every retrieval probe returns zero hits.",
            "- **PASS_WITH_WARNINGS** if ingest and DB are healthy and retrieval works, but family title validation",
            "  misses codes / mismatches titles, optional statute probes are weak, or some (not all) retrieval probes miss.",
            "- **PASS** if family checks are clean, ingest succeeds, counts are healthy, retrieval probes return hits,",
            "  and optional targets are found where the parser exposes them.",
            "",
            "### Warnings",
            "",
        ]
    )
    for w in state.get("warnings") or []:
        lines.append(f"- {w}")
    if not state.get("warnings"):
        lines.append("- (none)")
    lines.extend(["", "### Failures", ""])
    for f in state.get("failures") or []:
        lines.append(f"- {f}")
    if not state.get("failures"):
        lines.append("- (none)")
    lines.extend(
        [
            "",
            "## 7. NEXT ACTION",
            "",
            state.get("next_action") or "—",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _emit(
    state: dict[str, Any],
    reports_dir: Path,
    pdf_path: str,
) -> None:
    """Write tracking reports, optional detail JSON files, and print the console summary."""
    overall = state.get("overall_status") or "FAIL"
    details_path = reports_dir / "arkansas_handbook_ingest_validate_details.json"
    counts_path = reports_dir / "arkansas_handbook_db_counts.json"
    retr_path = reports_dir / "arkansas_handbook_retrieval_checks.json"
    _write_json(
        details_path,
        {
            "family_validation": state.get("family_validation"),
            "ingestion": state.get("ingestion"),
            "precheck": state.get("precheck"),
        },
    )
    _write_json(counts_path, state.get("db_checks") or {})
    _write_json(retr_path, state.get("retrieval_checks") or {})

    report_md = reports_dir / "arkansas_handbook_ingest_validate_report.md"
    state_json = reports_dir / "arkansas_handbook_ingest_validate_state.json"
    _write_md_report(report_md, pdf_path=pdf_path, overall=overall, state=state)
    _write_json(state_json, state)

    pre = state.get("precheck") or {}
    family_block = state.get("family_validation") or {}
    ingest_out = state.get("ingestion") or {}
    db_checks = state.get("db_checks") or {}
    retrieval = state.get("retrieval_checks") or {}

    print("=" * 72)
    print("ARKANSAS HANDBOOK INGEST + VALIDATE")
    print("=" * 72)
    print(f"PDF: {pdf_path}")
    print(
        f"Precheck: pdf_exists={pre.get('pdf_exists')} pdf_readable={pre.get('pdf_readable')} "
        f"schema_ok={pre.get('schema_ok')} db_ok={pre.get('db_ok')}"
    )
    if family_block:
        print(
            f"Family validation: parsed={family_block.get('parsed_family_count')} "
            f"title_ok={family_block.get('passes_title_checks')}"
        )
    print(
        f"Ingestion: {ingest_out.get('status') or 'n/a'} "
        f"families={ingest_out.get('family_count', 'n/a')} chunks={ingest_out.get('chunk_count', 'n/a')}"
    )
    if db_checks and not db_checks.get("skipped"):
        print(
            f"DB: families={db_checks.get('family_count')} units={db_checks.get('legal_unit_count')} "
            f"chunks={db_checks.get('chunk_count')} citations={db_checks.get('citation_count')}"
        )
    nq = len((retrieval.get("queries") or []))
    print(f"Retrieval probes: {nq}")
    print("-" * 72)
    print(f"OVERALL: {overall}")
    for w in state.get("warnings") or []:
        print(f"  WARN: {w}")
    for f in state.get("failures") or []:
        print(f"  FAIL: {f}")
    print(f"Report: {report_md}")
    print(f"State:  {state_json}")
    print("=" * 72)


def run(argv: list[str] | None = None) -> int:
    from sqlalchemy import func, inspect, or_, text
    from sqlalchemy.orm import Session

    import app.models.legal_handbook  # noqa: F401 — register tables for create_all

    from app.db.session import Base, SessionLocal, engine
    from app.models.legal_handbook import (
        LegalCitation,
        LegalDocument,
        LegalDocumentFamily,
        LegalSourceVersion,
        LegalUnit,
        LegalUnitChunk,
    )
    from app.services.legal_ingestion.arkansas_pipeline import ingest_arkansas_handbook_pdf
    from app.services.legal_ingestion.ingest_validate_status import (
        decide_overall_status,
        retrieval_is_broad_failure,
    )
    from app.services.legal_ingestion.page_mapper import PageMap
    from app.services.legal_ingestion.pdf_extractor import build_linear_corpus, extract_pdf_pages
    from app.services.legal_ingestion.toc_parser import family_map_validation_report_payload, parse_family_spans
    from app.services.legal_retrieval.citation_lookup import find_chunks_by_citation_text
    from app.services.legal_retrieval.lexical import search_legal_chunks_lexical

    p = argparse.ArgumentParser(description="Arkansas handbook ingest + validate (one command)")
    p.add_argument("--pdf", required=True, help="Path to Arkansas lawbook PDF")
    p.add_argument(
        "--stable-key",
        default="ARK_ASBP_STATUTES_RULES_2025_11",
        help="Legal document stable_key (must not already exist in DB)",
    )
    p.add_argument(
        "--version-label",
        default=None,
        help="Edition label passed to ingest (drives citation_key edition slug; use a new value when re-ingesting to avoid UNIQUE citation_key collisions)",
    )
    p.add_argument(
        "--no-ingest",
        action="store_true",
        help="Run precheck + family validation only (no DB writes)",
    )
    args = p.parse_args(argv)

    pdf_path = os.path.abspath(args.pdf)
    reports_dir = Path(_REPO_ROOT) / "tracking" / "reports"
    run_ts = _utc_now_iso()

    failures: list[str] = []
    warnings: list[str] = []

    state: dict[str, Any] = {
        "pdf_path": pdf_path,
        "run_timestamp": run_ts,
        "precheck": {},
        "family_validation": {},
        "ingestion": {},
        "db_checks": {},
        "retrieval_checks": {},
        "warnings": [],
        "failures": [],
        "next_action": "",
        "overall_status": "FAIL",
    }

    # --- STAGE 1: PRECHECKS ---
    pre: dict[str, Any] = {"pdf_exists": False, "pdf_readable": False, "db_ok": False, "schema_ok": False}

    try:
        Base.metadata.create_all(bind=engine)
        insp = inspect(engine)
        names = set(insp.get_table_names())
        need = {
            "legal_documents",
            "legal_source_versions",
            "legal_document_families",
            "legal_units",
            "legal_unit_chunks",
            "legal_citations",
        }
        pre["schema_ok"] = need.issubset(names)
        if not pre["schema_ok"]:
            failures.append(f"Missing expected tables (have {sorted(names)})")
    except Exception as exc:
        failures.append(f"Schema init failed: {exc}")

    db: Session | None = None
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        pre["db_ok"] = True
    except Exception as exc:
        failures.append(f"DB session failed: {exc}")
    finally:
        if db is not None:
            db.close()

    if not os.path.isfile(pdf_path):
        failures.append(f"PDF not found: {pdf_path}")
        state["precheck"] = pre
        state["failures"] = failures
        state["warnings"] = warnings
        state["next_action"] = "Provide a valid --pdf path to the November 2025 (or compatible) lawbook PDF."
        state["overall_status"] = decide_overall_status(failures, warnings)
        _emit(state, reports_dir, pdf_path)
        return 1

    pre["pdf_exists"] = True

    try:
        ext = extract_pdf_pages(pdf_path)
        full_text, page_starts = build_linear_corpus(ext.page_texts)
        pre["pdf_readable"] = bool(ext.page_count and len(full_text) > 100)
        pre["pdf_page_count"] = ext.page_count
        pre["corpus_chars"] = len(full_text)
    except Exception as exc:
        failures.append(f"PDF extraction failed: {exc}")
        traceback.print_exc()

    if not pre["pdf_readable"]:
        if not any("PDF extraction failed" in x for x in failures):
            failures.append("PDF extracted empty or too short; cannot validate or ingest.")

    if not args.no_ingest and pre.get("db_ok") and pre["pdf_readable"]:
        db2 = SessionLocal()
        try:
            existing = db2.query(LegalDocument).filter(LegalDocument.stable_key == args.stable_key).first()
            if existing is not None:
                failures.append(
                    f"legal_documents already has stable_key={args.stable_key!r}; "
                    "choose a new --stable-key or remove the row before re-ingesting."
                )
        finally:
            db2.close()

    state["precheck"] = pre

    # --- STAGE 2: FAMILY MAP VALIDATION (no DB) ---
    family_block: dict[str, Any] = {}
    if pre["pdf_readable"]:
        try:
            ext = extract_pdf_pages(pdf_path)
            full_text, page_starts = build_linear_corpus(ext.page_texts)
            page_map = PageMap(
                full_text=full_text,
                page_char_starts=page_starts,
                page_count=ext.page_count,
            )
            spans = parse_family_spans(full_text, page_map=page_map)
            payload = family_map_validation_report_payload(full_text)
            tv = (payload.get("title_validation") or {}) if isinstance(payload, dict) else {}
            missing = list(tv.get("missing_codes") or [])
            mismatch = list(tv.get("title_mismatch_codes") or [])
            fam_rows = []
            for s in sorted(spans, key=lambda x: x.char_start):
                ps, pe = _pages_for_span(page_map, s.char_start, s.char_end)
                fam_rows.append(
                    {
                        "family_code": s.family_code,
                        "title": s.title,
                        "span_provenance": s.span_provenance,
                        "span_confidence": s.span_confidence,
                        "char_start": s.char_start,
                        "char_end": s.char_end,
                        "page_start": ps,
                        "page_end": pe,
                    }
                )
            family_block = {
                "parsed_family_count": len(spans),
                "families": fam_rows,
                "validation_payload": payload,
                "title_validation": tv,
                "missing_expected_codes": missing,
                "title_mismatch_codes": mismatch,
                "passes_title_checks": len(missing) == 0 and len(mismatch) == 0,
            }
            codes_found = {x["family_code"] for x in fam_rows}
            extra = sorted(codes_found - set("ABCDEFGH"))
            family_block["unexpected_codes"] = extra
            if missing or mismatch:
                warnings.append(
                    f"Family map validation: missing_codes={missing}, title_mismatch_codes={mismatch}"
                )
        except Exception as exc:
            failures.append(f"Family validation stage failed: {exc}")
            traceback.print_exc()

    state["family_validation"] = family_block

    # --- STAGE 3: INGESTION ---
    ingest_out: dict[str, Any] = {}
    if not args.no_ingest and not failures and pre["pdf_readable"]:
        db3 = SessionLocal()
        try:
            ingest_kw: dict[str, Any] = {
                "pdf_path": pdf_path,
                "stable_key": args.stable_key,
            }
            if args.version_label:
                ingest_kw["version_label"] = args.version_label
            ingest_out = ingest_arkansas_handbook_pdf(db3, **ingest_kw)
            if ingest_out.get("status") != "completed":
                reason = ingest_out.get("reason") or ingest_out.get("status")
                failures.append(f"Ingestion did not complete: {reason}")
        except Exception as exc:
            failures.append(f"Ingestion raised: {exc}")
            ingest_out = {"status": "error", "error": str(exc)}
            traceback.print_exc()
        finally:
            db3.close()
    elif args.no_ingest:
        ingest_out = {"status": "skipped", "reason": "--no-ingest"}
    else:
        ingest_out = {"status": "skipped", "reason": "precheck or pdf failed"}

    state["ingestion"] = ingest_out

    ver_id = ingest_out.get("legal_source_version_id")
    doc_id = ingest_out.get("legal_document_id")

    # --- STAGE 4: DB CHECKS ---
    db_checks: dict[str, Any] = {}
    if ver_id and doc_id and not args.no_ingest:
        db4 = SessionLocal()
        try:
            doc = db4.get(LegalDocument, doc_id)
            ver = db4.get(LegalSourceVersion, ver_id)
            db_checks["document_found"] = doc is not None
            db_checks["version_found"] = ver is not None
            if not doc:
                failures.append("DB: legal_document row missing after ingest")
            if not ver:
                failures.append("DB: legal_source_version row missing after ingest")

            fam_count = (
                db4.query(func.count(LegalDocumentFamily.id))
                .filter(LegalDocumentFamily.legal_document_id == doc_id)
                .scalar()
                or 0
            )
            unit_count = (
                db4.query(func.count(LegalUnit.id))
                .join(LegalDocumentFamily, LegalUnit.legal_document_family_id == LegalDocumentFamily.id)
                .filter(LegalDocumentFamily.legal_document_id == doc_id)
                .scalar()
                or 0
            )
            chunk_count = (
                db4.query(func.count(LegalUnitChunk.id))
                .filter(LegalUnitChunk.legal_source_version_id == ver_id)
                .scalar()
                or 0
            )
            cite_count = (
                db4.query(func.count(LegalCitation.id))
                .join(LegalUnitChunk, LegalCitation.legal_unit_chunk_id == LegalUnitChunk.id)
                .filter(LegalUnitChunk.legal_source_version_id == ver_id)
                .scalar()
                or 0
            )
            db_checks["family_count"] = int(fam_count)
            db_checks["legal_unit_count"] = int(unit_count)
            db_checks["chunk_count"] = int(chunk_count)
            db_checks["citation_count"] = int(cite_count)

            if fam_count < 3:
                failures.append(f"DB: family_count too low ({fam_count})")
            if unit_count == 0:
                failures.append("DB: legal_unit_count is zero")
            if chunk_count == 0:
                failures.append("DB: chunk_count is zero")
            if cite_count == 0:
                failures.append("DB: citation_count is zero")

            targets = ("17-92-101", "17-92-115", "5-64-101")
            tc: dict[str, int] = {}
            for t in targets:
                n = (
                    db4.query(func.count(LegalCitation.id))
                    .join(LegalUnitChunk, LegalCitation.legal_unit_chunk_id == LegalUnitChunk.id)
                    .filter(
                        LegalUnitChunk.legal_source_version_id == ver_id,
                        or_(
                            LegalCitation.normalized_citation.ilike(f"%{t}%"),
                            LegalCitation.citation_key.ilike(f"%{t}%"),
                        ),
                    )
                    .scalar()
                    or 0
                )
                tc[t] = int(n)
            db_checks["target_citations"] = tc
            missing_targets = [k for k, v in tc.items() if v == 0]
            if missing_targets:
                warnings.append(
                    "Optional statute probes not found in citations table for: " + ", ".join(missing_targets)
                )
        finally:
            db4.close()
    else:
        db_checks["skipped"] = True

    state["db_checks"] = db_checks

    # --- STAGE 5: RETRIEVAL ---
    retrieval: dict[str, Any] = {"queries": []}
    # Run when ingest finished; weak family-map or DB count warnings must not skip retrieval QA.
    if ver_id and ingest_out.get("status") == "completed" and not args.no_ingest:
        db5 = SessionLocal()
        try:
            probes: list[dict[str, Any]] = []
            citation_queries = ["17-92-115", "17-92-101", "5-64-101"]
            for cq in citation_queries:
                hits = find_chunks_by_citation_text(db5, cq, legal_source_version_id=ver_id)
                scoped = True
                if hits:
                    scoped = all(h.get("legal_source_version_id") == ver_id for h in hits)
                probes.append(
                    {
                        "label": f"citation:{cq}",
                        "kind": "citation_lookup",
                        "query": cq,
                        "hit_count": len(hits),
                        "scoped_to_version": scoped,
                        "has_family_or_citation_info": bool(
                            hits
                            and (hits[0].get("family_code") or hits[0].get("citation_key"))
                        ),
                    }
                )
                if hits and not scoped:
                    warnings.append(f"Retrieval {cq}: hits not fully scoped to source version")

            phrase_queries = [
                ("phrase:Pharmacy Practice Act", "Pharmacy Practice Act"),
                ("phrase:PDMP", "Prescription Drug Monitoring Program"),
            ]
            for label, pq in phrase_queries:
                hits = search_legal_chunks_lexical(
                    db5, pq, limit=12, legal_source_version_id=ver_id
                )
                scoped = True
                if hits:
                    scoped = all(h.get("legal_source_version_id") == ver_id for h in hits)
                probes.append(
                    {
                        "label": label,
                        "kind": "lexical",
                        "query": pq,
                        "hit_count": len(hits),
                        "scoped_to_version": scoped,
                        "has_family_or_citation_info": bool(
                            hits and (hits[0].get("family_code") or hits[0].get("citation_key"))
                        ),
                    }
                )
                if hits and not scoped:
                    warnings.append(f"Retrieval {label}: hits not fully scoped to source version")

            retrieval["queries"] = probes
            if retrieval_is_broad_failure(probes):
                failures.append("Retrieval: all probes returned zero hits (broad failure)")
            else:
                zero_labels = [x["label"] for x in probes if int(x.get("hit_count") or 0) == 0]
                if zero_labels:
                    warnings.append("Some retrieval probes returned no hits: " + ", ".join(zero_labels))
        finally:
            db5.close()
    else:
        retrieval["skipped"] = True

    state["retrieval_checks"] = retrieval

    # --- STAGE 6: DECISION ---
    if args.no_ingest:
        warnings.append(
            "Ingestion, database sanity, and retrieval checks were not run (--no-ingest)."
        )

    state["failures"] = list(dict.fromkeys(failures))
    state["warnings"] = list(dict.fromkeys(warnings))

    overall = decide_overall_status(state["failures"], state["warnings"])
    state["overall_status"] = overall

    if args.no_ingest and overall != "FAIL":
        state["next_action"] = "Re-run without --no-ingest to execute full ingest, database checks, and retrieval QA."
    elif overall == "FAIL":
        state["next_action"] = "Fix failures above (PDF path, DB state, stable_key collision, or ingest errors), then re-run."
    elif overall == "PASS_WITH_WARNINGS":
        state["next_action"] = "Review warnings; optionally tune family-map heuristics or citation normalization if probes stay weak."
    else:
        state["next_action"] = "No action required; corpus is ingested and retrieval checks passed."

    _emit(state, reports_dir, pdf_path)

    return 0 if overall != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(run())
