#!/usr/bin/env python3
"""
Crawl https://www.allcarepharmacy.com/ and emit ingestion-ready pack manifests.

Writes:
  tracking/ingestion_packs/allcare_website/**/entries.json
  tracking/reports/allcare_website_inventory.{json,md}
  tracking/reports/allcare_website_ingestion_pack_state.json
  plus classification/strategy/mapping reports (see --write-reports)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import deque
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from app.services.website_ingestion_pack.manifest_entry import build_manifest_entry  # noqa: E402
from app.services.website_ingestion_pack.validate_crawl import validate_crawl_run  # noqa: E402

DEFAULT_ORIGIN = "https://www.allcarepharmacy.com"
ALLOWED_HOSTS = frozenset({"www.allcarepharmacy.com", "allcarepharmacy.com"})
USER_AGENT = "DSOS-AllCareSitePackBot/1.0 (+internal; ingestion-pack build)"

ASSET_EXT = frozenset({".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"})

# Deterministic same-site paths (public marketing HTML) to supplement thin link graphs.
def _seed_urls(origin: str) -> list[str]:
    base = origin.rstrip("/")
    paths = (
        "/",
        "/index.html",
        "/longterm.html",
        "/assistedliving.html",
        "/correctional.html",
        "/specialty.html",
        "/privacypractices.html",
        "/specialty-forms/",
    )
    return [base + p for p in paths]


class _LinkTitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.title_parts: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v for k, v in attrs if v is not None}
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)


def _strip_tags(html: str) -> str:
    t = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    t = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def _same_site(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and p.netloc.lower() in ALLOWED_HOSTS
    except Exception:
        return False


def _normalize_url(base: str, href: str) -> str | None:
    if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
        return None
    joined = urljoin(base, href)
    p = urlparse(joined)
    if p.scheme not in ("http", "https"):
        return None
    if p.netloc.lower() not in ALLOWED_HOSTS:
        return None
    path = p.path or "/"
    clean = f"{p.scheme}://{p.netloc.lower()}{path}"
    if p.query:
        clean += f"?{p.query}"
    return clean.split("#")[0]


def fetch_url(url: str, *, timeout: float = 20.0) -> tuple[bytes | None, str | None, str | None]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=timeout) as resp:
            ctype = resp.headers.get("Content-Type", "")
            body = resp.read(2_000_000)
            return body, ctype, None
    except (HTTPError, URLError, TimeoutError, OSError) as e:
        return None, None, str(e)


def run_crawl(
    *,
    origin: str,
    max_pages: int,
    max_depth: int,
) -> tuple[bool, list[dict[str, Any]], list[str]]:
    """Returns (reachable, inventory, errors)."""
    seen: set[str] = set()
    recorded: set[str] = set()
    q: deque[tuple[str, int]] = deque()
    for su in _seed_urls(origin):
        q.append((su, 0))
    if not q:
        q.append((origin.rstrip("/") + "/", 0))
    inventory: list[dict[str, Any]] = []
    errors: list[str] = []
    reachable = False

    def _record(inv: dict[str, Any]) -> None:
        u = inv["url"]
        if u in recorded:
            return
        recorded.add(u)
        inventory.append(inv)

    while q and len(recorded) < max_pages:
        url, depth = q.popleft()
        if url in seen:
            continue
        seen.add(url)

        low = url.lower()
        if any(low.endswith(ext) for ext in ASSET_EXT):
            fn = urlparse(url).path.split("/")[-1]
            inv = {
                "url": url,
                "title": fn,
                "snippet": "",
                "content_kind": "download",
                "depth": depth,
            }
            _record(inv)
            continue

        body, ctype, err = fetch_url(url)
        if err:
            errors.append(f"{url}: {err}")
            if url.rstrip("/") == origin.rstrip("/"):
                reachable = False
            continue
        reachable = True
        if not body:
            continue
        if ctype and "pdf" in ctype.lower():
            fn = urlparse(url).path.split("/")[-1] or "document.pdf"
            _record(
                {
                    "url": url,
                    "title": fn,
                    "snippet": "",
                    "content_kind": "pdf",
                    "depth": depth,
                }
            )
            continue

        try:
            text = body.decode("utf-8", errors="replace")
        except Exception:
            text = body.decode("latin-1", errors="replace")

        parser = _LinkTitleParser()
        try:
            parser.feed(text)
        except Exception:
            pass
        title = " ".join(parser.title_parts).strip() or url
        snippet = _strip_tags(text)[:1200]

        _record(
            {
                "url": url,
                "title": title,
                "snippet": snippet,
                "content_kind": "page",
                "depth": depth,
            }
        )

        if depth >= max_depth:
            continue
        for href in parser.links:
            nu = _normalize_url(url, href)
            if not nu or nu in seen:
                continue
            low = nu.lower()
            if any(low.split("?")[0].endswith(ext) for ext in ASSET_EXT):
                fn = urlparse(nu).path.split("/")[-1]
                _record(
                    {
                        "url": nu,
                        "title": fn,
                        "snippet": "",
                        "content_kind": "download",
                        "depth": depth + 1,
                    }
                )
                seen.add(nu)
                continue
            q.append((nu, depth + 1))

    return reachable, inventory, errors


def _write_pack_files(inventory: list[dict[str, Any]], pack_root: str) -> dict[str, list[dict[str, Any]]]:
    by_type: dict[str, list[dict[str, Any]]] = {}
    for item in inventory:
        entry = build_manifest_entry(
            url=item["url"],
            title=item.get("title") or "",
            snippet=item.get("snippet") or "",
            content_kind=item.get("content_kind") or "page",
            crawl_category=None,
            asset_filename=item.get("title") if item.get("content_kind") == "download" else None,
        )
        wst = entry["website_source_type"]
        by_type.setdefault(wst, []).append(entry)

    os.makedirs(pack_root, exist_ok=True)
    for wst, rows in by_type.items():
        d = os.path.join(pack_root, wst)
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "entries.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"entries": rows}, f, indent=2, ensure_ascii=False)
    return by_type


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--origin", default=DEFAULT_ORIGIN)
    p.add_argument("--max-pages", type=int, default=150)
    p.add_argument("--max-depth", type=int, default=3)
    p.add_argument("--pack-root", default=os.path.join(_REPO, "tracking", "ingestion_packs", "allcare_website"))
    p.add_argument(
        "--no-write-reports",
        action="store_true",
        help="Skip writing extended markdown reports (inventory JSON/state still written)",
    )
    args = p.parse_args()

    reachable, inventory, errors = run_crawl(origin=args.origin, max_pages=args.max_pages, max_depth=args.max_depth)

    manifests_written = False
    by_type: dict[str, list[dict[str, Any]]] = {}
    if inventory:
        by_type = _write_pack_files(inventory, args.pack_root)
        manifests_written = True

    entries_by_type = {k: len(v) for k, v in by_type.items()}
    total = max(sum(entries_by_type.values()), len(inventory), 1)
    gen_ref = entries_by_type.get("general_reference", 0)
    weak_ratio = (gen_ref / total) if total else 0.0

    val = validate_crawl_run(
        target_reachable=reachable,
        inventory_count=len(inventory),
        manifests_written=manifests_written,
        entries_by_type=entries_by_type,
        weak_unclassified_ratio=weak_ratio,
    )

    state = {
        "schema_version": 1,
        "origin": args.origin,
        "overall_status": val["overall_status"],
        "validation": val,
        "inventory_count": len(inventory),
        "entries_by_website_source_type": entries_by_type,
        "crawl_errors_sample": errors[:25],
        "manifests_root": os.path.relpath(args.pack_root, _REPO).replace("\\", "/"),
        "verification": {
            "pytest": "run: python -m pytest tests -q",
            "compileall": "run: python -m compileall app tools -q",
            "runner": "python tools/build_allcare_website_ingestion_pack.py",
        },
    }
    state_path = os.path.join(_REPO, "tracking", "reports", "allcare_website_ingestion_pack_state.json")
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    inv_path = os.path.join(_REPO, "tracking", "reports", "allcare_website_inventory.json")
    with open(inv_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "origin": args.origin,
                "items": inventory,
                "errors": errors,
                "validation": val,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    md_lines = [
        "# AllCare Pharmacy — website crawl inventory",
        "",
        f"- Origin: `{args.origin}`",
        f"- Items discovered: **{len(inventory)}**",
        f"- Validation: **{val['overall_status']}**",
        "",
        "## Sample URLs",
        "",
    ]
    for it in inventory[:40]:
        md_lines.append(f"- [{it.get('title', '')[:80]}]({it['url']}) — `{it.get('content_kind')}`")
    if len(inventory) > 40:
        md_lines.append(f"- … plus {len(inventory) - 40} more (see JSON).")
    md_path = os.path.join(_REPO, "tracking", "reports", "allcare_website_inventory.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    agg = []
    for rows in by_type.values():
        agg.extend(rows)
    agg_path = os.path.join(args.pack_root, "allcare_website_manifest.json")
    with open(agg_path, "w", encoding="utf-8") as f:
        json.dump({"entries": agg}, f, indent=2, ensure_ascii=False)

    # Ensure per-type directories exist even if empty (deterministic layout)
    for sub in (
        "company_profile",
        "policy_manual",
        "sop_workflow",
        "training_module",
        "form_template",
        "compliance_notice",
        "reference_sheet",
        "billing_reference",
        "vendor_or_product_reference",
        "general_reference",
    ):
        d = os.path.join(args.pack_root, sub)
        os.makedirs(d, exist_ok=True)
        ep = os.path.join(d, "entries.json")
        if not os.path.exists(ep):
            with open(ep, "w", encoding="utf-8") as f:
                json.dump({"entries": []}, f, indent=2)

    if not args.no_write_reports:
        _write_markdown_reports(_REPO, state, inventory, val)

    print(json.dumps({"status": val["overall_status"], "inventory": len(inventory), "state": state_path}, indent=2))
    return 0 if val["overall_status"] != "FAIL" else 1


def _write_markdown_reports(repo: str, state: dict[str, Any], inventory: list[dict], val: dict[str, Any]) -> None:
    """Optional full report set (sections aligned with pass spec)."""
    rep = os.path.join(repo, "tracking", "reports", "allcare_website_ingestion_pack_report.md")
    with open(rep, "w", encoding="utf-8") as f:
        f.write(
            """# AllCare website → ingestion pack — report

## 1. WHY A WEBSITE-TO-INGESTION PACK PASS IS NEEDED

Public marketing and operations content for AllCare must enter Malone through the **same ingestion control plane** as other business sources: stable keys, parser profiles, tags, validation, and promotion. A site crawl that stops at “one blob” cannot be governed; structured manifests per source category enable phased ingest and review.

## 2. WHAT THE PUBLIC ALLCARE SITE EXPOSES

The homepage and linked sections describe **long-term care**, **assisted living**, **correctional**, and **specialty** pharmacy lines, corporate contact, and integrations (e.g. ExactMed). Linked pages and downloadable PDFs/Docs are inventoried as separate manifest entries with URL-level classification.

## 3. CRAWL / INVENTORY STRATEGY

- **Scope:** `https://www.allcarepharmacy.com/` same-host HTTP(S) only.
- **Method:** BFS HTML parse for `<a href>`, depth-limited; asset URLs by extension.
- **Outputs:** `tracking/reports/allcare_website_inventory.json`, per-type `entries.json`, aggregate manifest.

## 4. SOURCE-TYPE CLASSIFICATION STRATEGY

Rule-based mapping from URL path, title, and text snippet keywords to **website_source_type** (10 categories). **Malone mapping** uses nearest `ingestion_control` source_type + `parser_profile` (see `app/services/website_ingestion_pack/allcare_rules.py`).

## 5. INGESTION CONTROL-PLANE MAPPING

Each manifest entry includes `malone_source_type`, `parser_profile`, dimensional `suggested_tags`, `authority_hint`, `ingestion_priority` (P1–P3), and `review_recommendation`.

## 6. WHAT THIS PASS IMPLEMENTED

- Crawler runner `tools/build_allcare_website_ingestion_pack.py`.
- Library `app/services/website_ingestion_pack/` for rules, manifests, validation.
- Packs under `tracking/ingestion_packs/allcare_website/`.

## 7. WHAT REMAINS DEFERRED

- Full download/mirror of assets to `tracking/data/allcare_website_assets/` (optional `--fetch` in a follow-on).
- Finer NLP on page body; sitemap.xml ingestion if published.
- Human review workflow integration in DB.

## 8. HARD-FAIL COMPLIANCE CHECK

- No parallel ingestion platform; manifests feed existing `run_business_ingest` contract.
- No legal-layer replacement; website packs are **non-legal** business reference unless separately classified.
- Weak classifications are visible in manifests and validation warnings, not hidden.

---
"""
        )
        f.write(f"**Run validation:** `{state.get('validation', {}).get('overall_status')}`\n\n")
        f.write(f"**Inventory count:** {len(inventory)}\n")

    cls_path = os.path.join(repo, "tracking", "reports", "allcare_website_source_classification.md")
    with open(cls_path, "w", encoding="utf-8") as f:
        f.write("# AllCare — source classification (rule-based)\n\n")
        f.write("See `app/services/website_ingestion_pack/allcare_rules.py` for ordered keyword and URL rules.\n")
        f.write(f"\n**Last validation:** {val.get('overall_status')}\n")

    strat = os.path.join(repo, "tracking", "reports", "allcare_website_source_pack_strategy.md")
    with open(strat, "w", encoding="utf-8") as f:
        f.write("# Source pack strategy\n\n")
        f.write("One folder per `website_source_type` with `entries.json`; aggregate `allcare_website_manifest.json`.\n")

    mpath = os.path.join(repo, "tracking", "reports", "allcare_website_ingestion_mapping.md")
    with open(mpath, "w", encoding="utf-8") as f:
        f.write("# Ingestion mapping\n\n")
        f.write("| website_source_type | malone_source_type | parser_profile |\n")
        f.write("|---|---|---|\n")
        f.write("| policy_manual, compliance_notice | policy_manual | policy_manual |\n")
        f.write("| sop_workflow | sop_workflow | sop_workflow |\n")
        f.write("| training_module | training_module | training_module |\n")
        f.write("| form_template | form_template | general_reference (until form profile) |\n")
        f.write("| others / company / reference / billing / vendor | general_reference | general_reference |\n")

    nt = os.path.join(repo, "tracking", "reports", "NEXT_THREAD_PROMPT_ALLCARE_WEBSITE_INGESTION_PACK.md")
    with open(nt, "w", encoding="utf-8") as f:
        f.write(
            """# Next thread — AllCare website ingestion pack

1. Optionally add `--download-assets` to mirror PDFs into `tracking/data/allcare_website_assets/`.
2. Run `python tools/run_business_ingest.py` per manifest entry after content is on disk.
3. Wire review_state tags to ingestion DB.

```bash
python tools/build_allcare_website_ingestion_pack.py --write-reports
```
"""
        )


if __name__ == "__main__":
    raise SystemExit(main())
