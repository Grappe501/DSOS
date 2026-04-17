-- Legal handbook knowledge (v0) — Arkansas ASBP-style compiled statutes & rules
-- Companion: tracking/reports/malone_legal_schema_plan.md
-- Runtime DB: sqlite:///./runtime_v5.db (see app/db/session.py)
-- IDs: TEXT UUID strings (matches existing app models).
-- Relationship: complements regulation_knowledge_v0 / migration 0002; adds handbook decomposition.

PRAGMA foreign_keys = ON;

-- One uploaded compiled handbook file (e.g. PDF) and its cover-level identity
CREATE TABLE IF NOT EXISTS legal_documents (
  id TEXT PRIMARY KEY,
  stable_key TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  original_filename TEXT,
  storage_uri TEXT,
  content_checksum TEXT,
  compiled_edition_label TEXT,
  cover_metadata_json TEXT NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'registered',
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_legal_documents_status ON legal_documents (status);

-- Ingest snapshots / editions bound to the same logical document (re-upload, new checksum)
CREATE TABLE IF NOT EXISTS legal_source_versions (
  id TEXT PRIMARY KEY,
  legal_document_id TEXT NOT NULL REFERENCES legal_documents (id),
  version_label TEXT NOT NULL,
  compiled_publication_date TEXT,
  status TEXT NOT NULL DEFAULT 'draft',
  content_checksum TEXT,
  storage_uri TEXT,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_legal_source_versions_document
  ON legal_source_versions (legal_document_id);

-- Major TOC families (A–H) and per-family embedded revision labels (e.g. May 2023 vs Aug 2025)
CREATE TABLE IF NOT EXISTS legal_document_families (
  id TEXT PRIMARY KEY,
  legal_document_id TEXT NOT NULL REFERENCES legal_documents (id),
  family_code TEXT NOT NULL,
  title TEXT,
  sort_order INTEGER NOT NULL DEFAULT 0,
  toc_page_start INTEGER,
  toc_page_end INTEGER,
  embedded_source_revision_label TEXT,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_legal_document_families_doc_code
  ON legal_document_families (legal_document_id, family_code);

-- Normalized legal units: statute blocks, rule articles/sections, nested nodes
CREATE TABLE IF NOT EXISTS legal_units (
  id TEXT PRIMARY KEY,
  legal_document_family_id TEXT NOT NULL REFERENCES legal_document_families (id),
  parent_legal_unit_id TEXT REFERENCES legal_units (id),
  unit_kind TEXT NOT NULL,
  primary_citation TEXT,
  heading_raw TEXT,
  toc_path TEXT,
  subsection_path TEXT,
  page_start INTEGER,
  page_end INTEGER,
  ordinal INTEGER NOT NULL DEFAULT 0,
  body_text TEXT,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_legal_units_family ON legal_units (legal_document_family_id);
CREATE INDEX IF NOT EXISTS idx_legal_units_parent ON legal_units (parent_legal_unit_id);
CREATE INDEX IF NOT EXISTS idx_legal_units_citation ON legal_units (primary_citation);

-- Subsection-preserving retrieval slices (may be finer than one row per display section)
CREATE TABLE IF NOT EXISTS legal_unit_chunks (
  id TEXT PRIMARY KEY,
  legal_unit_id TEXT NOT NULL REFERENCES legal_units (id),
  ordinal INTEGER NOT NULL,
  subsection_path TEXT,
  body_text TEXT NOT NULL,
  char_start INTEGER,
  char_end INTEGER,
  page_start INTEGER,
  page_end INTEGER,
  retrieval_ready INTEGER NOT NULL DEFAULT 0,
  embedding_ref TEXT,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_legal_unit_chunks_unit_ord
  ON legal_unit_chunks (legal_unit_id, ordinal);

-- Citation anchors for deterministic lookup and UI (Ark. Code, board rule, page anchor)
CREATE TABLE IF NOT EXISTS legal_citations (
  id TEXT PRIMARY KEY,
  legal_unit_chunk_id TEXT NOT NULL REFERENCES legal_unit_chunks (id),
  citation_key TEXT NOT NULL,
  citation_kind TEXT,
  normalized_citation TEXT,
  authority_type TEXT,
  anchor_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_legal_citations_key ON legal_citations (citation_key);
CREATE INDEX IF NOT EXISTS idx_legal_citations_chunk ON legal_citations (legal_unit_chunk_id);

-- Parsed cross-references between units/chunks (may be unresolved until linker pass)
CREATE TABLE IF NOT EXISTS legal_cross_references (
  id TEXT PRIMARY KEY,
  from_legal_unit_chunk_id TEXT NOT NULL REFERENCES legal_unit_chunks (id),
  raw_reference_text TEXT,
  to_citation_key TEXT,
  to_legal_unit_id TEXT REFERENCES legal_units (id),
  resolution_status TEXT NOT NULL DEFAULT 'unresolved',
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_legal_xref_from ON legal_cross_references (from_legal_unit_chunk_id);
CREATE INDEX IF NOT EXISTS idx_legal_xref_to_unit ON legal_cross_references (to_legal_unit_id);

-- Explicit date layers: compiled edition vs embedded act dates vs effective dates
CREATE TABLE IF NOT EXISTS legal_date_layers (
  id TEXT PRIMARY KEY,
  scope_type TEXT NOT NULL,
  scope_id TEXT NOT NULL,
  layer_kind TEXT NOT NULL,
  raw_label TEXT,
  iso_date TEXT,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_legal_date_layers_scope ON legal_date_layers (scope_type, scope_id);

CREATE TABLE IF NOT EXISTS legal_tags (
  id TEXT PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  label TEXT NOT NULL,
  parent_id TEXT REFERENCES legal_tags (id)
);

CREATE TABLE IF NOT EXISTS legal_chunk_tags (
  chunk_id TEXT NOT NULL REFERENCES legal_unit_chunks (id),
  tag_id TEXT NOT NULL REFERENCES legal_tags (id),
  PRIMARY KEY (chunk_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_legal_chunk_tags_tag ON legal_chunk_tags (tag_id);

CREATE TABLE IF NOT EXISTS legal_ingestion_jobs (
  id TEXT PRIMARY KEY,
  legal_document_id TEXT REFERENCES legal_documents (id),
  legal_source_version_id TEXT REFERENCES legal_source_versions (id),
  status TEXT NOT NULL,
  stage TEXT,
  error_message TEXT,
  started_at TIMESTAMP,
  finished_at TIMESTAMP,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_legal_ingestion_jobs_status ON legal_ingestion_jobs (status);

CREATE TABLE IF NOT EXISTS legal_answer_traces (
  id TEXT PRIMARY KEY,
  proposal_id TEXT REFERENCES malone_proposals (id),
  query_fingerprint TEXT,
  chunk_ids_json TEXT NOT NULL DEFAULT '[]',
  citation_keys_json TEXT NOT NULL DEFAULT '[]',
  model_id TEXT,
  verified INTEGER NOT NULL DEFAULT 0,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_legal_answer_traces_proposal ON legal_answer_traces (proposal_id);

-- Migration 0004 (additive): retrieval scoping per ingest snapshot
-- ALTER TABLE legal_unit_chunks ADD COLUMN legal_source_version_id TEXT REFERENCES legal_source_versions (id);
-- CREATE INDEX IF NOT EXISTS idx_legal_unit_chunks_source_version ON legal_unit_chunks (legal_source_version_id);
