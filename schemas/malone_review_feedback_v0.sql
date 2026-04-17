-- Malone human review loop (see alembic 0008_malone_review_loop_human_feedback)
-- Reference only; authoritative DDL is in Alembic migrations.

CREATE TABLE IF NOT EXISTS malone_review_feedback_events (
    id VARCHAR PRIMARY KEY,
    artifact_type VARCHAR NOT NULL,
    artifact_id VARCHAR NOT NULL,
    reviewer_user_id VARCHAR NOT NULL REFERENCES users(id),
    outcome VARCHAR NOT NULL,
    review_state_before VARCHAR,
    review_state_after VARCHAR,
    trust_level VARCHAR,
    risk_flag BOOLEAN NOT NULL DEFAULT 0,
    notes TEXT,
    meta_json TEXT NOT NULL DEFAULT '{}',
    created_at DATETIME NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_malone_review_feedback_events_pair
    ON malone_review_feedback_events (artifact_type, artifact_id);

CREATE TABLE IF NOT EXISTS malone_review_artifact_heads (
    id VARCHAR PRIMARY KEY,
    artifact_type VARCHAR NOT NULL,
    artifact_id VARCHAR NOT NULL,
    current_review_state VARCHAR NOT NULL DEFAULT 'system_generated',
    current_trust_level VARCHAR,
    last_outcome VARCHAR,
    last_reviewer_user_id VARCHAR REFERENCES users(id),
    last_event_id VARCHAR,
    updated_at DATETIME NOT NULL,
    UNIQUE (artifact_type, artifact_id)
);
