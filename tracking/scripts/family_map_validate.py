"""
Validate Arkansas family-map extraction against expected A–H structure (manual / CI helper).

Usage (repo root):

  python tracking/scripts/family_map_validate.py --fixture tracking/fixtures/arkansas_handbook_vertical_slice_sample.txt

With a local PDF (runs pypdf extraction; no DB):

  python tracking/scripts/family_map_validate.py --pdf "C:\\path\\Lawbook.pdf"

Emits JSON to stdout for pasting into ``tracking/reports/malone_family_map_hardening_state.json``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from app.services.legal_ingestion.pdf_extractor import build_linear_corpus, extract_pdf_pages
from app.services.legal_ingestion.toc_parser import family_map_validation_report_payload, parse_family_spans


def main() -> int:
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--fixture", help="Path to UTF-8 text fixture")
    g.add_argument("--pdf", help="Path to Arkansas lawbook PDF")
    args = p.parse_args()

    if args.fixture:
        path = os.path.abspath(args.fixture)
        with open(path, encoding="utf-8") as f:
            text = f.read()
    else:
        path = os.path.abspath(args.pdf or "")
        if not os.path.isfile(path):
            print("FAIL: PDF not found:", path, file=sys.stderr)
            return 1
        ext = extract_pdf_pages(path)
        text, _ = build_linear_corpus(ext.page_texts)

    spans = parse_family_spans(text)
    payload = family_map_validation_report_payload(text)
    out = {
        "source_path": path,
        "family_count": len(spans),
        "families": [
            {
                "family_code": s.family_code,
                "title": s.title,
                "span_provenance": s.span_provenance,
                "span_confidence": s.span_confidence,
                "char_start": s.char_start,
                "char_end": s.char_end,
            }
            for s in sorted(spans, key=lambda x: x.char_start)
        ],
        "validation": payload,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
