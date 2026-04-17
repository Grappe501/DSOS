-- Business-wide ingestion control plane (v0) — companion to Alembic 0005
-- Runtime: sqlite:///./runtime_v5.db (see app/db/session.py)
-- IDs: TEXT UUID strings (matches existing app models).

PRAGMA foreign_keys = ON;

-- Logical business sources (cross-domain registry)
CREATE TABLE IF NOT EXISTS ingestion_sources (
  id TEXT PRIMARY KEY,
  stable_key TEXT NOT NULL UNIQUE,
  source_type TEXT NOT NULL,
  business_domain TEXT NOT NULL DEFAULT 'general',
  owner_steward TEXT,
  authority_tier TEXT NOT NULL DEFAULT 'internal',
  lifecycle_status TEXT NOT NULL DEFAULT 'registered',
  title TEXT NOT NULL DEFAULT '',
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ingestion_sources_stable_key ON ingestion_sources (stable_key);
CREATE INDEX IF NOT EXISTS idx_ingestion_sources_type ON ingestion_sources (source_type);
CREATE INDEX IF NOT EXISTS idx_ingestion_sources_lifecycle ON ingestion_sources (lifecycle_status);

-- Versions / editions; optional link to legal handbook rows when profile is legal_handbook
CREATE TABLE IF NOT EXISTS ingestion_source_versions (
  id TEXT PRIMARY KEY,
  ingestion_source_id TEXT NOT NULL REFERENCES ingestion_sources (id),
  version_label TEXT NOT NULL,
  content_checksum TEXT,
  storage_uri TEXT,
  parser_profile_key TEXT NOT NULL,
  legal_document_id TEXT REFERENCES legal_documents (id),
  legal_source_version_id TEXT REFERENCES legal_source_versions (id),
  status TEXT NOT NULL DEFAULT 'draft',
  retrieval_ready INTEGER NOT NULL DEFAULT 0,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ingestion_source_versions_source ON ingestion_source_versions (ingestion_source_id);
CREATE INDEX IF NOT EXISTS idx_ingestion_source_versions_legal_doc ON ingestion_source_versions (legal_document_id);
CREATE INDEX IF NOT EXISTS idx_ingestion_source_versions_legal_ver ON ingestion_source_versions (legal_source_version_id);

-- Generic segments for non-legal profiles (policy, SOP scaffold, etc.)
CREATE TABLE IF NOT EXISTS ingestion_segments (
  id TEXT PRIMARY KEY,
  ingestion_source_version_id TEXT NOT NULL REFERENCES ingestion_source_versions (id),
  ordinal INTEGER NOT NULL,
  heading TEXT,
  body_text TEXT NOT NULL,
  anchor_key TEXT,
  retrieval_ready INTEGER NOT NULL DEFAULT 0,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ingestion_segments_version ON ingestion_segments (ingestion_source_version_id);

-- Business-layer jobs (parallel to legal_ingestion_jobs for handbook runs)
CREATE TABLE IF NOT EXISTS ingestion_jobs (
  id TEXT PRIMARY KEY,
  ingestion_source_id TEXT NOT NULL REFERENCES ingestion_sources (id),
  ingestion_source_version_id TEXT REFERENCES ingestion_source_versions (id),
  parser_profile_key TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  stage TEXT,
  overall_validation_status TEXT,
  error_message TEXT,
  linked_legal_ingestion_job_id TEXT REFERENCES legal_ingestion_jobs (id),
  counts_json TEXT NOT NULL DEFAULT '{}',
  meta_json TEXT NOT NULL DEFAULT '{}',
  started_at TIMESTAMP,
  finished_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ingestion_jobs_source ON ingestion_jobs (ingestion_source_id);
CREATE INDEX IF NOT EXISTS idx_ingestion_jobs_status ON ingestion_jobs (status);
CREATE INDEX IF NOT EXISTS idx_ingestion_jobs_linked_legal_job ON ingestion_jobs (linked_legal_ingestion_job_id);

CREATE TABLE IF NOT EXISTS ingestion_job_events (
  id TEXT PRIMARY KEY,
  ingestion_job_id TEXT NOT NULL REFERENCES ingestion_jobs (id),
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ingestion_job_events_job ON ingestion_job_events (ingestion_job_id);

CREATE TABLE IF NOT EXISTS ingestion_validations (
  id TEXT PRIMARY KEY,
  ingestion_job_id TEXT NOT NULL UNIQUE REFERENCES ingestion_jobs (id),
  overall_status TEXT NOT NULL,
  failures_json TEXT NOT NULL DEFAULT '[]',
  warnings_json TEXT NOT NULL DEFAULT '[]',
  precheck_json TEXT,
  structure_json TEXT,
  db_counts_json TEXT,
  retrieval_json TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ingestion_promotions (
  id TEXT PRIMARY KEY,
  ingestion_source_version_id TEXT NOT NULL REFERENCES ingestion_source_versions (id),
  from_status TEXT NOT NULL,
  to_status TEXT NOT NULL,
  promotion_outcome TEXT NOT NULL DEFAULT 'pending',
  actor TEXT,
  reason TEXT,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ingestion_promotions_version ON ingestion_promotions (ingestion_source_version_id);

CREATE TABLE IF NOT EXISTS ingestion_tag_definitions (
  id TEXT PRIMARY KEY,
  dimension TEXT NOT NULL,
  slug TEXT NOT NULL,
  label TEXT NOT NULL,
  parent_id TEXT REFERENCES ingestion_tag_definitions (id),
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_ingestion_tag_definitions_dimension_slug
  ON ingestion_tag_definitions (dimension, slug);
CREATE INDEX IF NOT EXISTS idx_ingestion_tag_definitions_dimension ON ingestion_tag_definitions (dimension);

CREATE TABLE IF NOT EXISTS ingestion_tag_assignments (
  id TEXT PRIMARY KEY,
  tag_definition_id TEXT NOT NULL REFERENCES ingestion_tag_definitions (id),
  target_kind TEXT NOT NULL,
  target_id TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ingestion_tag_assignments_target ON ingestion_tag_assignments (target_kind, target_id);
