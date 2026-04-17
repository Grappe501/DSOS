-- Reference DDL: Malone scenario memory + decision trace (see alembic 0007).

CREATE TABLE IF NOT EXISTS malone_scenario_memories (
    id VARCHAR PRIMARY KEY,
    proposal_id VARCHAR NOT NULL REFERENCES malone_proposals(id),
    actor_user_id VARCHAR REFERENCES users(id),
    prompt_text TEXT NOT NULL DEFAULT '',
    prompt_fingerprint VARCHAR NOT NULL,
    scenario_type VARCHAR NOT NULL DEFAULT 'unknown',
    intent_target VARCHAR,
    source_types_json TEXT NOT NULL DEFAULT '[]',
    source_version_snapshot_json TEXT NOT NULL DEFAULT '{}',
    memory_status VARCHAR NOT NULL DEFAULT 'active',
    review_audit_status VARCHAR NOT NULL DEFAULT 'pending',
    delivery_mode VARCHAR,
    delivery_status VARCHAR,
    meta_json TEXT NOT NULL DEFAULT '{}',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_malone_scenario_memories_proposal_id ON malone_scenario_memories(proposal_id);
CREATE INDEX IF NOT EXISTS ix_malone_scenario_memories_prompt_fingerprint ON malone_scenario_memories(prompt_fingerprint);

CREATE TABLE IF NOT EXISTS malone_decision_traces (
    id VARCHAR PRIMARY KEY,
    scenario_memory_id VARCHAR NOT NULL UNIQUE REFERENCES malone_scenario_memories(id),
    answer_pattern_json TEXT NOT NULL DEFAULT '{}',
    deterministic_legal_mode VARCHAR NOT NULL DEFAULT 'unknown',
    decision_workflow_json TEXT NOT NULL DEFAULT '{}',
    source_evidence_map_json TEXT NOT NULL DEFAULT '{}',
    normalized_unit_refs_json TEXT NOT NULL DEFAULT '[]',
    fallback_flags_json TEXT NOT NULL DEFAULT '{}',
    packet_meta_snapshot_json TEXT NOT NULL DEFAULT '{}',
    operating_copilot_snapshot_json TEXT,
    verification_snapshot_json TEXT NOT NULL DEFAULT '{}',
    meta_json TEXT NOT NULL DEFAULT '{}',
    created_at DATETIME NOT NULL
);
