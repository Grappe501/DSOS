"""

End-to-end Arkansas State Board of Pharmacy handbook ingest (text-in or PDF → DB rows).



Purpose:

    One vertical-slice pipeline: families → legal units → subsection chunks → citations,

    with optional PDF page grounding.



Role in Malone:

    Called from admin/batch ingestion (not Malone chat). Produces persisted evidence rows

    for `legal_retrieval` and future `truth_packet_service` attachment.

"""



from __future__ import annotations



import datetime as dt

import hashlib

import json

import os

import re

from typing import Any



from sqlalchemy.orm import Session



from app.models.legal_handbook import (

    LegalCitation,

    LegalDocumentFamily,

    LegalIngestionJob,

    LegalUnit,

    LegalUnitChunk,

)

from app.models.models import gen_id

from app.services.ingestion.normalizer import normalize_extracted_text

from app.services.legal_ingestion.anchor_builder import enrich_anchor_display

from app.services.legal_ingestion.chunk_builder import draft_chunk_rows

from app.services.legal_ingestion.date_layering import (

    record_compilation_edition_layer,

    record_family_embedded_revision,

)

from app.services.legal_ingestion.legal_unit_parser import LegalUnitSpan, find_legal_units_in_span

from app.services.legal_ingestion.page_mapper import PageMap

from app.services.legal_ingestion.pdf_extractor import build_linear_corpus, extract_pdf_pages

from app.services.legal_ingestion.subsection_parser import split_subsection_segments

from app.services.legal_ingestion.source_profiler import estimate_handbook_zones

from app.services.legal_ingestion.toc_parser import parse_family_spans

from app.services.legal_knowledge.citations import (

    build_anchor_json,

    dumps_anchor,

    normalize_statute_like_citation,

    stable_citation_key,

)

from app.services.legal_knowledge.document_registry import (

    create_legal_document,

    create_legal_source_version,

)





def _edition_slug(version_label: str) -> str:

    cleaned = re.sub(r"[^A-Za-z0-9]+", "", version_label.strip())

    return cleaned[:24].upper() or "EDITION"





def _pages_for_span(

    page_map: PageMap | None,

    char_start: int | None,

    char_end: int | None,

) -> tuple[int | None, int | None]:

    if page_map is None or char_start is None or char_end is None:

        return None, None

    if char_end <= char_start:

        p = page_map.global_char_to_page(char_start)

        return p, p

    return page_map.span_to_page_range(char_start, char_end)





def ingest_arkansas_handbook_pdf(

    db: Session,

    *,

    pdf_path: str,

    stable_key: str = "ARK_ASBP_STATUTES_RULES_2025_11",

    document_title: str = "Arkansas State Board of Pharmacy — Statutes and Rules",

    version_label: str = "November 2025 Compilation",

    compiled_publication_date: str | None = "2025-11-01",

    storage_uri: str | None = None,

) -> dict[str, Any]:

    """

    Extract text in page order, build a page map, and run the Arkansas ingest pipeline.

    """

    path = os.path.abspath(pdf_path)

    if not os.path.isfile(path):

        return {"status": "failed", "reason": "pdf_not_found", "path": path}



    digest = hashlib.sha256()

    with open(path, "rb") as f:

        for block in iter(lambda: f.read(65536), b""):

            digest.update(block)

    content_checksum = digest.hexdigest()



    extracted = extract_pdf_pages(path)

    full_text, page_starts = build_linear_corpus(extracted.page_texts)

    page_map = PageMap(

        full_text=full_text,

        page_char_starts=page_starts,

        page_count=extracted.page_count,

    )



    return _ingest_arkansas_corpus(

        db,

        text=full_text,

        page_map=page_map,

        stable_key=stable_key,

        document_title=document_title,

        version_label=version_label,

        compiled_publication_date=compiled_publication_date,

        original_filename=os.path.basename(path),

        storage_uri=storage_uri or f"file://{path}",

        content_checksum=content_checksum,

        ingest_profile="arkansas_asbp_handbook_pdf_v1",

    )





def ingest_arkansas_handbook_text(

    db: Session,

    *,

    raw_text: str,

    stable_key: str = "ARK_ASBP_STATUTES_RULES_2025_11",

    document_title: str = "Arkansas State Board of Pharmacy — Statutes and Rules",

    version_label: str = "November 2025 Compilation",

    compiled_publication_date: str | None = "2025-11-01",

    original_filename: str | None = None,

    storage_uri: str | None = None,

    content_checksum: str | None = None,

) -> dict[str, Any]:

    text = normalize_extracted_text(raw_text)

    return _ingest_arkansas_corpus(

        db,

        text=text,

        page_map=None,

        stable_key=stable_key,

        document_title=document_title,

        version_label=version_label,

        compiled_publication_date=compiled_publication_date,

        original_filename=original_filename,

        storage_uri=storage_uri,

        content_checksum=content_checksum,

        ingest_profile="arkansas_asbp_handbook_text_v1",

    )





def _ingest_arkansas_corpus(

    db: Session,

    *,

    text: str,

    page_map: PageMap | None,

    stable_key: str,

    document_title: str,

    version_label: str,

    compiled_publication_date: str | None,

    original_filename: str | None,

    storage_uri: str | None,

    content_checksum: str | None,

    ingest_profile: str,

) -> dict[str, Any]:

    started = dt.datetime.utcnow()

    job = LegalIngestionJob(

        id=gen_id(),

        status="running",

        stage="normalize",

        started_at=started,

        meta_json=json.dumps(

            {"profile": ingest_profile, "page_grounded": page_map is not None},

            ensure_ascii=False,

        ),

    )

    db.add(job)

    db.flush()



    doc = create_legal_document(

        db,

        stable_key=stable_key,

        title=document_title,

        compiled_edition_label=version_label,

        original_filename=original_filename,

        storage_uri=storage_uri,

        content_checksum=content_checksum,

        cover_metadata={"jurisdiction": "US-AR", "issuer": "Arkansas State Board of Pharmacy"},

    )

    zone_profile = estimate_handbook_zones(text, page_map)

    ver = create_legal_source_version(

        db,

        legal_document_id=doc.id,

        version_label=version_label,

        compiled_publication_date=compiled_publication_date,

        content_checksum=content_checksum,

        storage_uri=storage_uri,

        status="active",

        meta={
            "ingest_profile": ingest_profile,
            "page_count": page_map.page_count if page_map else None,
            "handbook_zones": zone_profile,
        },

    )

    job.legal_document_id = doc.id

    job.legal_source_version_id = ver.id

    job.stage = "families"

    db.flush()



    record_compilation_edition_layer(

        db,

        legal_source_version_id=ver.id,

        raw_label=version_label,

        meta={"note": "compilation cover date / edition label"},

    )



    edition = _edition_slug(version_label)

    families = parse_family_spans(text, page_map=page_map)

    if not families:

        job.status = "failed"

        job.error_message = "no_family_headings_found"

        job.finished_at = dt.datetime.utcnow()

        job.stage = "failed"

        db.commit()

        return {"status": "failed", "reason": "no_family_headings_found", "job_id": job.id}



    chunk_total = 0

    citation_total = 0



    for order, fam in enumerate(sorted(families, key=lambda f: f.char_start)):

        fam_ps, fam_pe = _pages_for_span(page_map, fam.char_start, fam.char_end)

        fam_row = LegalDocumentFamily(

            id=gen_id(),

            legal_document_id=doc.id,

            family_code=fam.family_code,

            title=fam.title,

            sort_order=order,

            toc_page_start=fam_ps,

            toc_page_end=fam_pe,

            embedded_source_revision_label=fam.embedded_revision,

            meta_json=json.dumps(
                {
                    "parser": "arkansas_family_map_v2",
                    "page_grounded": fam_ps is not None,
                    "family_map": {
                        "span_provenance": fam.span_provenance,
                        "span_confidence": fam.span_confidence,
                        "toc_anchor_char": fam.toc_char_start,
                        "body_anchor_char": fam.body_char_start,
                        "reconciliation_notes": list(fam.reconciliation_notes),
                    },
                },
                ensure_ascii=False,
            ),

        )

        db.add(fam_row)

        db.flush()

        if fam.embedded_revision:

            record_family_embedded_revision(

                db,

                family_row_id=fam_row.id,

                raw_label=fam.embedded_revision,

                meta={"family_code": fam.family_code},

            )



        span_text = text[fam.char_start : fam.char_end]

        units = find_legal_units_in_span(span_text, base_offset=fam.char_start)

        if not units:

            units = [

                LegalUnitSpan(

                    unit_kind="family_body",

                    primary_citation=None,

                    heading_raw=fam.title,

                    char_start=fam.char_start,

                    char_end=fam.char_end,

                    body_text=span_text.strip(),

                    body_global_char_start=fam.char_start,

                )

            ]



        for u_ord, unit in enumerate(units):

            ups, upe = _pages_for_span(page_map, unit.char_start, unit.char_end)

            unit_row = LegalUnit(

                id=gen_id(),

                legal_document_family_id=fam_row.id,

                parent_legal_unit_id=None,

                unit_kind=unit.unit_kind,

                primary_citation=unit.primary_citation,

                heading_raw=unit.heading_raw,

                toc_path=f"{fam.family_code} / {fam.title}",

                subsection_path=None,

                page_start=ups,

                page_end=upe,

                ordinal=u_ord,

                body_text=unit.body_text,

                meta_json=json.dumps(

                    {

                        "legal_source_version_id": ver.id,

                        "char_start": unit.char_start,

                        "char_end": unit.char_end,

                        "body_global_char_start": unit.body_global_char_start,

                    },

                    ensure_ascii=False,

                ),

            )

            db.add(unit_row)

            db.flush()



            segments = split_subsection_segments(unit.body_text, base_offset=unit.body_global_char_start)

            chunk_rows = draft_chunk_rows(segments)

            for row in chunk_rows:

                cs, ce = row.get("char_start"), row.get("char_end")

                cps, cpe = _pages_for_span(page_map, cs, ce)

                if cps is None and ups is not None:

                    cps, cpe = ups, upe



                ch = LegalUnitChunk(

                    id=gen_id(),

                    legal_unit_id=unit_row.id,

                    legal_source_version_id=ver.id,

                    ordinal=int(row["ordinal"]),

                    subsection_path=row.get("subsection_path"),

                    body_text=row["body_text"],

                    char_start=cs,

                    char_end=ce,

                    page_start=cps,

                    page_end=cpe,

                    retrieval_ready=bool(row.get("retrieval_ready")),

                    meta_json=json.dumps({"legal_source_version_id": ver.id}, ensure_ascii=False),

                )

                db.add(ch)

                db.flush()

                chunk_total += 1



                cite_key = stable_citation_key(

                    edition_slug=edition,

                    family_code=fam.family_code,

                    primary_citation=unit.primary_citation,

                    subsection_path=row.get("subsection_path") or "",

                    ordinal=int(row["ordinal"]),

                    legal_unit_id=unit_row.id,

                )

                anchor = build_anchor_json(

                    family_code=fam.family_code,

                    family_title=fam.title,

                    primary_citation=unit.primary_citation,

                    unit_kind=unit.unit_kind,

                    subsection_path=row.get("subsection_path"),

                    heading_raw=unit.heading_raw,

                    page_start=cps,

                    page_end=cpe,

                    toc_path=f"{fam.family_code} / {fam.title}",

                )

                anchor_enriched = enrich_anchor_display(

                    anchor,

                    compilation_label=version_label,

                )

                cit = LegalCitation(

                    id=gen_id(),

                    legal_unit_chunk_id=ch.id,

                    citation_key=cite_key,

                    citation_kind="arkansas_compilation_unit",

                    normalized_citation=normalize_statute_like_citation(unit.primary_citation),

                    authority_type="state_board_pharmacy",

                    anchor_json=dumps_anchor(anchor_enriched),

                )

                db.add(cit)

                citation_total += 1



    job.status = "completed"

    job.stage = "completed"

    job.finished_at = dt.datetime.utcnow()

    job.meta_json = json.dumps(

        {

            "families": len(families),

            "chunks": chunk_total,

            "citations": citation_total,

            "page_grounded": page_map is not None,

            "pdf_pages": page_map.page_count if page_map else None,

        },

        ensure_ascii=False,

    )

    db.commit()



    return {

        "status": "completed",

        "job_id": job.id,

        "legal_document_id": doc.id,

        "legal_source_version_id": ver.id,

        "family_count": len(families),

        "chunk_count": chunk_total,

        "citation_count": citation_total,

        "page_grounded": page_map is not None,

        "pdf_page_count": page_map.page_count if page_map else None,

    }


