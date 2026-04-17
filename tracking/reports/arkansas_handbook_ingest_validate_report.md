# Arkansas Handbook Ingest + Validate

## 1. INPUT PDF

- Path: `H:\DSOS\tracking\data\arkansas_handbook\Lawbook-2025-Dec-1.pdf`
- File exists: True
- PDF text extract usable: True

## 2. FAMILY VALIDATION RESULT

- Parsed families: **8**
- Title validation (engine): `{"expected_codes": ["A", "B", "C", "D", "E", "F", "G", "H"], "detected_codes": ["A", "B", "C", "D", "E", "F", "G", "H"], "missing_codes": [], "title_mismatch_codes": []}`
- Missing expected codes: `[]`
- Title mismatch codes: `[]`

### Expected families (reference)

- **A** — Pharmacy Practice Act
- **B** — Miscellaneous Statutes Related to Pharmacy
- **C** — Uniform Controlled Substances Act
- **D** — Insurance Policies – Prescription Drug Benefits
- **E** — Food, Drug, and Cosmetic Act
- **F** — Controlled Substances and Legend Drugs
- **G** — Administrative Procedure Act
- **H** — Rules Pertaining to Arkansas Prescription Drug Monitoring Program

### Detected families (summary)

- **A** — Pharmacy Practice Act — pp. 12–73 (provenance=toc_confirmed_by_body, confidence=high)
- **B** — Miscellaneous Statutes Related to Pharmacy — pp. 73–79 (provenance=toc_confirmed_by_body, confidence=high)
- **C** — Uniform Controlled Substances Act — pp. 79–108 (provenance=toc_confirmed_by_body, confidence=high)
- **D** — Insurance Policies – Prescription Drug Benefits — pp. 108–113 (provenance=toc_confirmed_by_body, confidence=high)
- **E** — Food, Drug, and Cosmetic Act — pp. 113–129 (provenance=toc_confirmed_by_body, confidence=high)
- **F** — Controlled Substances and Legend Drugs — pp. 129–134 (provenance=toc_confirmed_by_body, confidence=high)
- **G** — Administrative Procedure Act — pp. 134–151 (provenance=toc_confirmed_by_body, confidence=high)
- **H** — Rules Pertaining to Arkansas Prescription Drug Monitoring Program — pp. 151–439 (provenance=toc_confirmed_by_body, confidence=high)

## 3. INGESTION RESULT

- Status: `completed`
- Job ID: `45b95f83-e666-4573-a156-da681467fee1`
- Legal document ID: `ef98ab86-eeb0-4a72-9e43-f7da504ed161`
- Source version ID: `2dd613c7-4744-4d46-aa3a-2c1ae98e8ffb`
- Message / reason: ``

## 4. DATABASE SANITY CHECKS

- Document row: `True`
- Source version row: `True`
- Family count: **8**
- Legal unit count: **184**
- Chunk count: **6289**
- Citation count: **6289**

### Target citation probes (optional)

- `17-92-101`: found **2187** row(s)
- `17-92-115`: found **78** row(s)
- `5-64-101`: found **282** row(s)

## 5. RETRIEVAL SANITY CHECKS

- **citation:17-92-115** — hits=78, scoped_to_version=True, has_family_or_cite=True
- **citation:17-92-101** — hits=2187, scoped_to_version=True, has_family_or_cite=True
- **citation:5-64-101** — hits=282, scoped_to_version=True, has_family_or_cite=True
- **phrase:Pharmacy Practice Act** — hits=12, scoped_to_version=True, has_family_or_cite=True
- **phrase:PDMP** — hits=12, scoped_to_version=True, has_family_or_cite=True

## 6. OVERALL PASS / FAIL

**PASS**

### Decision rules (this run)

- **FAIL** if precheck fails, PDF cannot be extracted, ingest does not complete,
  document/source version rows are missing, core counts are empty, or every retrieval probe returns zero hits.
- **PASS_WITH_WARNINGS** if ingest and DB are healthy and retrieval works, but family title validation
  misses codes / mismatches titles, optional statute probes are weak, or some (not all) retrieval probes miss.
- **PASS** if family checks are clean, ingest succeeds, counts are healthy, retrieval probes return hits,
  and optional targets are found where the parser exposes them.

### Warnings

- (none)

### Failures

- (none)

## 7. NEXT ACTION

No action required; corpus is ingested and retrieval checks passed.
