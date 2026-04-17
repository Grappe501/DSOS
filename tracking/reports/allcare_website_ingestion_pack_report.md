# AllCare website → ingestion pack — report

## 1. WHY A WEBSITE-TO-INGESTION PACK PASS IS NEEDED

Public marketing and operations content for AllCare must enter Malone through the **same ingestion control plane** as other business sources: stable keys, parser profiles, tags, validation, and promotion. A site crawl that stops at “one blob” cannot be governed; structured manifests per source category enable phased ingest and review.

## 2. WHAT THE PUBLIC ALLCARE SITE EXPOSES

The homepage and linked sections describe **long-term care**, **assisted living**, **correctional**, and **specialty** pharmacy lines, corporate contact, and integrations (e.g. ExactMed). Linked pages and downloadable PDFs/Docs are inventoried as separate manifest entries with URL-level classification.

## 3. CRAWL / INVENTORY STRATEGY

- **Scope:** `https://www.allcarepharmacy.com/` same-host HTTP(S) only; external links are not followed (only recorded as out-of-scope in inventory when linked from a page).
- **Method:** BFS on `<a href>` with deduplicated URLs, depth-limited crawl, plus a **deterministic seed list** of known public HTML paths (e.g. `longterm.html`, `assistedliving.html`, `correctional.html`, `specialty.html`, `privacypractices.html`) so thin navigation graphs still yield a usable inventory.
- **Assets:** PDF/DOC/XLS/PPT links on-domain are captured as download rows (metadata-first; bulk download optional).
- **Outputs:** `tracking/reports/allcare_website_inventory.json`, `allcare_website_inventory.md`, per-type `entries.json`, and `allcare_website_manifest.json`.

### Validation outcome rules (`validate_crawl_run`)

| Status | Conditions |
|--------|------------|
| **FAIL** | Target unreachable; inventory &lt; 3; manifests not written; or classification overwhelmingly `general_reference` on large crawls (&gt;30 items, &gt;95% general). |
| **PASS_WITH_WARNINGS** | Crawl and manifests OK but inventory &lt; 8, or weak general-reference ratio, or “full PASS” bar not met (see code). |
| **PASS** | Reachable, manifests written, inventory ≥ 12, at least **three** distinct non-`general_reference` website source types, and no FAIL triggers. |

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
**Run validation:** `PASS`

**Inventory count:** 13
