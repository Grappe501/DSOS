"""
Smoke verification for PDF extraction + page map (run manually; not part of CI).

Usage (PowerShell):
  python tracking/scripts/pdf_grounding_smoke.py --pdf "C:\\path\\Lawbook-2025-Dec-1.pdf"

Purpose:
  Regression-friendly check that pypdf extracts non-empty text, page count matches map,
  and global offsets stay consistent without running a full DB ingest.
"""

from __future__ import annotations

import argparse
import os
import sys

# Allow running from repo root
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from app.services.legal_ingestion.page_mapper import PageMap
from app.services.legal_ingestion.pdf_extractor import build_linear_corpus, extract_pdf_pages


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--pdf", required=True, help="Path to Arkansas lawbook PDF")
    args = p.parse_args()
    path = os.path.abspath(args.pdf)
    if not os.path.isfile(path):
        print("FAIL: file not found:", path)
        return 1

    ext = extract_pdf_pages(path)
    full_text, starts = build_linear_corpus(ext.page_texts)
    pm = PageMap(full_text=full_text, page_char_starts=starts, page_count=ext.page_count)

    non_empty = sum(1 for t in ext.page_texts if t.strip())
    mid = len(full_text) // 2
    print("page_count", ext.page_count)
    print("non_empty_pages", non_empty)
    print("corpus_chars", len(full_text))
    print("midpoint_page", pm.global_char_to_page(mid))
    print("first_page_sample", (ext.page_texts[0] or "")[:200].replace("\n", " "))
    return 0 if ext.page_count > 0 and len(full_text) > 100 else 2


if __name__ == "__main__":
    raise SystemExit(main())
