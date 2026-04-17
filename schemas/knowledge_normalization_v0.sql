-- Reference DDL for knowledge normalization layer (see Alembic 0006).

CREATE TABLE IF NOT EXISTS normalization_runs (
  id TEXT PRIMARY KEY,
  profile_key TEXT NOT NULL,
  source_type TEXT NOT NULL,
  ingestion_source_id TEXT REFERENCES ingestion_sources(id),
  ingestion_source_version_id TEXT REFERENCES ingestion_source_versions(id),
  legal_document_id TEXT REFERENCES legal_documents(id),
  legal_source_version_id TEXT REFERENCES legal_source_versions(id),
  validation_status TEXT NOT NULL DEFAULT 'PENDING',
  unit_count INTEGER NOT NULL DEFAULT 0,
  failures_json TEXT NOT NULL DEFAULT '[]',
  warnings_json TEXT NOT NULL DEFAULT '[]',
  meta_json TEXT NOT NULL DEFAULT '{}',
  started_at TIMESTAMP,
  finished_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS normalized_knowledge_units (
  id TEXT PRIMARY KEY,
  normalization_run_id TEXT NOT NULL REFERENCES normalization_runs(id),
  ordinal INTEGER NOT NULL,
  normalized_unit_type TEXT NOT NULL,
  source_type TEXT NOT NULL,
  ingestion_source_id TEXT REFERENCES ingestion_sources(id),
  ingestion_source_version_id TEXT REFERENCES ingestion_source_versions(id),
  ingestion_segment_id TEXT REFERENCES ingestion_segments(id),
  legal_document_id TEXT REFERENCES legal_documents(id),
  legal_source_version_id TEXT REFERENCES legal_source_versions(id),
  legal_unit_id TEXT REFERENCES legal_units(id),
  legal_unit_chunk_id TEXT REFERENCES legal_unit_chunks(id),
  title TEXT,
  source_text TEXT NOT NULL,
  plain_language_summary TEXT,
  applies_to_role TEXT,
  action_type TEXT,
  requirement_level TEXT,
  condition_text TEXT,
  exception_text TEXT,
  escalation_text TEXT,
  output_outcome_text TEXT,
  citation_keys_json TEXT NOT NULL DEFAULT '[]',
  anchor_json TEXT NOT NULL DEFAULT '{}',
  structured_facets_json TEXT NOT NULL DEFAULT '{}',
  confidence_level TEXT NOT NULL DEFAULT 'medium',
  review_state TEXT NOT NULL DEFAULT 'system_generated',
  superseded INTEGER NOT NULL DEFAULT 0,
  superseded_by_unit_id TEXT REFERENCES normalized_knowledge_units(id),
  retrieval_headline TEXT,
  retrieval_blob TEXT,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (normalization_run_id, ordinal)
);

CREATE TABLE IF NOT EXISTS normalized_knowledge_review_events (
  id TEXT PRIMARY KEY,
  normalized_knowledge_unit_id TEXT NOT NULL REFERENCES normalized_knowledge_units(id),
  from_state TEXT,
  to_state TEXT NOT NULL,
  actor TEXT,
  reason TEXT,
  meta_json TEXT NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
