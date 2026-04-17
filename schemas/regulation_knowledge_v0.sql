-- Regulation knowledge core (v0) — SQLite-oriented DDL
-- Companion: tracking/reports/malone_regulation_schema_plan.md
-- Runtime DB per app/db/session.py: sqlite:///./runtime_v5.db
-- IDs: TEXT UUID strings (matches existing app models style).

PRAGMA foreign_keys = ON;

-- Logical document identity (stable across versions)
CREATE TABLE IF NOT EXISTS regulation_sources (
  id TEXT PRIMARY KEY,
  stable_key TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  source_type TEXT NOT NULL,
  issuing_authority TEXT,
  jurisdiction TEXT,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_regulation_sources_jurisdiction
  ON regulation_sources (jurisdiction);

-- Immutable revision / snapshot anchor
CREATE TABLE IF NOT EXISTS regulation_source_versions (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL REFERENCES regulation_sources (id),
  version_label TEXT NOT NULL,
  effective_date TEXT,
  superseded_at TEXT,
  status TEXT NOT NULL DEFAULT 'draft',
  content_checksum TEXT,
  storage_uri TEXT,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_regulation_source_versions_source
  ON regulation_source_versions (source_id);

CREATE INDEX IF NOT EXISTS idx_regulation_source_versions_status
  ON regulation_source_versions (status);

-- Retrieval unit (chunk of handbook text)
CREATE TABLE IF NOT EXISTS regulation_chunks (
  id TEXT PRIMARY KEY,
  source_version_id TEXT NOT NULL REFERENCES regulation_source_versions (id),
  ordinal INTEGER NOT NULL,
  heading_path TEXT,
  rule_type TEXT,
  plain_summary TEXT,
  body_text TEXT NOT NULL,
  char_start INTEGER,
  char_end INTEGER,
  retrieval_ready INTEGER NOT NULL DEFAULT 0,
  embedding_ref TEXT,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_regulation_chunks_version_ordinal
  ON regulation_chunks (source_version_id, ordinal);

-- Citation anchors for UI and audit
CREATE TABLE IF NOT EXISTS regulation_citations (
  id TEXT PRIMARY KEY,
  chunk_id TEXT NOT NULL REFERENCES regulation_chunks (id),
  citation_key TEXT NOT NULL,
  anchor_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_regulation_citations_key
  ON regulation_citations (citation_key);

CREATE INDEX IF NOT EXISTS idx_regulation_citations_chunk
  ON regulation_citations (chunk_id);

-- Controlled taxonomy
CREATE TABLE IF NOT EXISTS regulation_tags (
  id TEXT PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  label TEXT NOT NULL,
  parent_id TEXT REFERENCES regulation_tags (id)
);

CREATE TABLE IF NOT EXISTS regulation_chunk_tags (
  chunk_id TEXT NOT NULL REFERENCES regulation_chunks (id),
  tag_id TEXT NOT NULL REFERENCES regulation_tags (id),
  PRIMARY KEY (chunk_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_regulation_chunk_tags_tag
  ON regulation_chunk_tags (tag_id);

-- Ingestion pipeline tracking
CREATE TABLE IF NOT EXISTS regulation_ingestion_jobs (
  id TEXT PRIMARY KEY,
  source_version_id TEXT REFERENCES regulation_source_versions (id),
  status TEXT NOT NULL,
  stage TEXT,
  error_message TEXT,
  started_at TIMESTAMP,
  finished_at TIMESTAMP,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_regulation_ingestion_jobs_status
  ON regulation_ingestion_jobs (status);

-- Answer / audit trace (optional link to Malone proposal)
CREATE TABLE IF NOT EXISTS regulation_answer_traces (
  id TEXT PRIMARY KEY,
  proposal_id TEXT REFERENCES malone_proposals (id),
  query_fingerprint TEXT,
  chunk_ids_json TEXT NOT NULL DEFAULT '[]',
  model_id TEXT,
  verified INTEGER NOT NULL DEFAULT 0,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_regulation_answer_traces_proposal
  ON regulation_answer_traces (proposal_id);
