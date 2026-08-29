-- A.R.C.A.D.I.A. v0.1: semantic-memory schema substrate carried forward unchanged from the R2 canonical schema.
-- v0.1 crash/replay requires PRC-success atomicity to be implemented by repository/migration integration as described in 08_RECOVERY_TRACE_PRIVACY; do not silently alter this substrate without a migration.

-- A.R.C.A.D.I.A. Persistence Prototype
-- Semantic Memory Schema
-- Date: 2026-08-28
-- R2: durable-provisional semantic standing + direct user memory-control provenance
-- Parent: ARCADIA_PERSISTENCE_RECIPE_PROTOTYPE_BUILD_SPEC_R2_2026-08-28.md
--
-- Assumes parent checkpoint already provides:
-- system_meta, conversations, conversation_turns, artifacts, artifact_links.
--
-- UUID strings are authoritative identity.
-- Human-readable short IDs are convenience aliases only.
-- All semantic writes are owned by the Persistence Host.

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;

INSERT OR IGNORE INTO system_meta(key, value)
VALUES ('memory_commit_seq', '0');

CREATE TABLE IF NOT EXISTS semantic_id_counters (
    kind TEXT PRIMARY KEY,
    next_value INTEGER NOT NULL CHECK(next_value >= 1)
);

INSERT OR IGNORE INTO semantic_id_counters(kind, next_value) VALUES
('ENTITY', 1),
('CLAIM', 1),
('CONFLICT', 1);

CREATE TABLE IF NOT EXISTS semantic_entities (
    entity_uuid TEXT PRIMARY KEY,
    entity_short_id TEXT NOT NULL UNIQUE,
    entity_type TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK(status IN ('ACTIVE','MERGED','RETIRED')),
    merged_into_entity_uuid TEXT,
    created_at TEXT NOT NULL,
    created_turn_uuid TEXT NOT NULL,
    created_memory_commit_seq INTEGER NOT NULL CHECK(created_memory_commit_seq >= 1),
    retired_at TEXT,
    FOREIGN KEY(created_turn_uuid) REFERENCES conversation_turns(turn_uuid),
    FOREIGN KEY(merged_into_entity_uuid) REFERENCES semantic_entities(entity_uuid),
    CHECK(
        (status = 'MERGED' AND merged_into_entity_uuid IS NOT NULL)
        OR
        (status != 'MERGED')
    )
);

CREATE INDEX IF NOT EXISTS idx_semantic_entities_type_status
ON semantic_entities(entity_type, status);

CREATE INDEX IF NOT EXISTS idx_semantic_entities_merged_into
ON semantic_entities(merged_into_entity_uuid);

CREATE TABLE IF NOT EXISTS semantic_claims (
    claim_uuid TEXT PRIMARY KEY,
    claim_short_id TEXT NOT NULL UNIQUE,
    subject_entity_uuid TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_kind TEXT NOT NULL
        CHECK(object_kind IN ('TEXT','NUMBER','BOOLEAN','DATETIME','ENTITY')),
    object_value_json TEXT NOT NULL,
    object_search_text TEXT,
    claim_cardinality TEXT NOT NULL
        CHECK(claim_cardinality IN ('SINGLE_CURRENT','MULTI_CURRENT')),
    source_authority TEXT NOT NULL
        CHECK(source_authority IN ('USER_ASSERTED','EXTERNALLY_ESTABLISHED','DERIVED')),
    status TEXT NOT NULL
        CHECK(status IN ('ACTIVE','CONTESTED','SUPERSEDED','RETRACTED')),
    durability_class TEXT NOT NULL
        CHECK(durability_class IN ('STABLE','SEMI_STABLE','TIME_BOUNDED','EVENT_HISTORY')),
    observed_at TEXT,
    effective_from TEXT,
    effective_to TEXT,
    expires_at TEXT,
    created_at TEXT NOT NULL,
    created_turn_uuid TEXT NOT NULL,
    created_memory_commit_seq INTEGER NOT NULL CHECK(created_memory_commit_seq >= 1),
    status_memory_commit_seq INTEGER NOT NULL CHECK(status_memory_commit_seq >= 1),
    FOREIGN KEY(subject_entity_uuid) REFERENCES semantic_entities(entity_uuid),
    FOREIGN KEY(created_turn_uuid) REFERENCES conversation_turns(turn_uuid)
);

CREATE INDEX IF NOT EXISTS idx_semantic_claims_subject_predicate_status
ON semantic_claims(subject_entity_uuid, predicate, status);

CREATE INDEX IF NOT EXISTS idx_semantic_claims_status_expiry
ON semantic_claims(status, expires_at);

CREATE TABLE IF NOT EXISTS semantic_claim_transitions (
    transition_uuid TEXT PRIMARY KEY,
    from_claim_uuid TEXT NOT NULL,
    to_claim_uuid TEXT,
    transition_kind TEXT NOT NULL
        CHECK(transition_kind IN (
            'CHANGE',
            'CORRECTION',
            'REFINEMENT',
            'DUPLICATE_COLLAPSE',
            'RETRACTION',
            'CONFLICT_RESOLUTION'
        )),
    created_at TEXT NOT NULL,
    created_turn_uuid TEXT NOT NULL,
    memory_commit_seq INTEGER NOT NULL CHECK(memory_commit_seq >= 1),
    FOREIGN KEY(from_claim_uuid) REFERENCES semantic_claims(claim_uuid),
    FOREIGN KEY(to_claim_uuid) REFERENCES semantic_claims(claim_uuid),
    FOREIGN KEY(created_turn_uuid) REFERENCES conversation_turns(turn_uuid),
    CHECK(
        (transition_kind = 'RETRACTION' AND to_claim_uuid IS NULL)
        OR
        (transition_kind != 'RETRACTION')
    )
);

CREATE INDEX IF NOT EXISTS idx_claim_transitions_from
ON semantic_claim_transitions(from_claim_uuid);

CREATE INDEX IF NOT EXISTS idx_claim_transitions_to
ON semantic_claim_transitions(to_claim_uuid);

CREATE TABLE IF NOT EXISTS semantic_entity_aliases (
    alias_uuid TEXT PRIMARY KEY,
    entity_uuid TEXT NOT NULL,
    alias_text TEXT NOT NULL,
    normalized_alias TEXT NOT NULL,
    alias_kind TEXT NOT NULL
        CHECK(alias_kind IN (
            'NAME',
            'NICKNAME',
            'PROJECT_NAME',
            'HISTORICAL_NAME',
            'IDENTIFIER',
            'USER_LABEL'
        )),
    alias_status TEXT NOT NULL
        CHECK(alias_status IN ('CURRENT','HISTORICAL','SEARCH_ONLY','RETIRED')),
    source_claim_uuid TEXT,
    created_memory_commit_seq INTEGER NOT NULL CHECK(created_memory_commit_seq >= 1),
    retired_memory_commit_seq INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY(entity_uuid) REFERENCES semantic_entities(entity_uuid),
    FOREIGN KEY(source_claim_uuid) REFERENCES semantic_claims(claim_uuid)
);

CREATE INDEX IF NOT EXISTS idx_semantic_aliases_normalized
ON semantic_entity_aliases(normalized_alias);

CREATE INDEX IF NOT EXISTS idx_semantic_aliases_entity_status
ON semantic_entity_aliases(entity_uuid, alias_status);

CREATE TABLE IF NOT EXISTS semantic_conflicts (
    conflict_uuid TEXT PRIMARY KEY,
    conflict_short_id TEXT NOT NULL UNIQUE,
    subject_entity_uuid TEXT NOT NULL,
    predicate TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK(status IN ('OPEN','RESOLVED')),
    created_at TEXT NOT NULL,
    created_turn_uuid TEXT NOT NULL,
    created_memory_commit_seq INTEGER NOT NULL CHECK(created_memory_commit_seq >= 1),
    resolved_at TEXT,
    resolved_memory_commit_seq INTEGER,
    FOREIGN KEY(subject_entity_uuid) REFERENCES semantic_entities(entity_uuid),
    FOREIGN KEY(created_turn_uuid) REFERENCES conversation_turns(turn_uuid)
);

CREATE TABLE IF NOT EXISTS semantic_conflict_members (
    conflict_uuid TEXT NOT NULL,
    claim_uuid TEXT NOT NULL,
    PRIMARY KEY(conflict_uuid, claim_uuid),
    FOREIGN KEY(conflict_uuid) REFERENCES semantic_conflicts(conflict_uuid),
    FOREIGN KEY(claim_uuid) REFERENCES semantic_claims(claim_uuid)
);

CREATE TABLE IF NOT EXISTS semantic_entity_merges (
    merge_uuid TEXT PRIMARY KEY,
    from_entity_uuid TEXT NOT NULL,
    into_entity_uuid TEXT NOT NULL,
    reason_kind TEXT NOT NULL
        CHECK(reason_kind IN ('USER_CONFIRMED','EVIDENCE_ESTABLISHED','DUPLICATE_REPAIR')),
    created_at TEXT NOT NULL,
    created_turn_uuid TEXT NOT NULL,
    memory_commit_seq INTEGER NOT NULL CHECK(memory_commit_seq >= 1),
    FOREIGN KEY(from_entity_uuid) REFERENCES semantic_entities(entity_uuid),
    FOREIGN KEY(into_entity_uuid) REFERENCES semantic_entities(entity_uuid),
    FOREIGN KEY(created_turn_uuid) REFERENCES conversation_turns(turn_uuid),
    CHECK(from_entity_uuid != into_entity_uuid)
);

CREATE INDEX IF NOT EXISTS idx_entity_merges_from
ON semantic_entity_merges(from_entity_uuid);

CREATE INDEX IF NOT EXISTS idx_entity_merges_into
ON semantic_entity_merges(into_entity_uuid);

CREATE TABLE IF NOT EXISTS semantic_provenance (
    provenance_uuid TEXT PRIMARY KEY,
    target_kind TEXT NOT NULL
        CHECK(target_kind IN (
            'ENTITY',
            'CLAIM',
            'ALIAS',
            'TRANSITION',
            'CONFLICT',
            'ENTITY_MERGE'
        )),
    target_uuid TEXT NOT NULL,
    source_authority TEXT NOT NULL
        CHECK(source_authority IN ('USER_ASSERTED','EXTERNALLY_ESTABLISHED','DERIVED')),
    source_channel TEXT NOT NULL DEFAULT 'CONVERSATION'
        CHECK(source_channel IN ('CONVERSATION','DIRECT_USER_MEMORY_CONTROL','TOOL_EVIDENCE','SYSTEM_DERIVED')),
    source_turn_uuid TEXT NOT NULL,
    source_artifact_uuid TEXT,
    source_ref_type TEXT,
    source_ref_value TEXT,
    source_hash TEXT,
    persistence_item_uuid TEXT,
    created_at TEXT NOT NULL,
    memory_commit_seq INTEGER NOT NULL CHECK(memory_commit_seq >= 1),
    FOREIGN KEY(source_turn_uuid) REFERENCES conversation_turns(turn_uuid),
    FOREIGN KEY(source_artifact_uuid) REFERENCES artifacts(artifact_uuid)
);

CREATE INDEX IF NOT EXISTS idx_semantic_provenance_target
ON semantic_provenance(target_kind, target_uuid);

CREATE INDEX IF NOT EXISTS idx_semantic_provenance_source_turn
ON semantic_provenance(source_turn_uuid);

CREATE TABLE IF NOT EXISTS memory_transactions (
    transaction_uuid TEXT PRIMARY KEY,
    persistence_run_uuid TEXT NOT NULL,
    turn_uuid TEXT NOT NULL,
    base_memory_commit_seq INTEGER NOT NULL CHECK(base_memory_commit_seq >= 0),
    result_memory_commit_seq INTEGER,
    status TEXT NOT NULL
        CHECK(status IN ('PENDING','COMMITTED','ROLLED_BACK','FAILED')),
    semantic_standing TEXT
        CHECK(semantic_standing IN ('PROVISIONAL','STABILIZED_NO_IMMEDIATE_CORRECTION','CONFIRMED_EXPLICIT','REVERTED_BY_USER_CONTROL')),
    compensates_transaction_uuid TEXT,
    standing_updated_at TEXT,
    standing_source_turn_uuid TEXT,
    standing_reason TEXT,
    transaction_hash TEXT NOT NULL,
    mutation_count INTEGER NOT NULL CHECK(mutation_count >= 0),
    created_at TEXT NOT NULL,
    committed_at TEXT,
    FOREIGN KEY(turn_uuid) REFERENCES conversation_turns(turn_uuid),
    FOREIGN KEY(compensates_transaction_uuid) REFERENCES memory_transactions(transaction_uuid),
    FOREIGN KEY(standing_source_turn_uuid) REFERENCES conversation_turns(turn_uuid),
    CHECK(
        (status = 'COMMITTED' AND semantic_standing IS NOT NULL)
        OR
        (status != 'COMMITTED' AND semantic_standing IS NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_memory_transactions_turn
ON memory_transactions(turn_uuid);

CREATE INDEX IF NOT EXISTS idx_memory_transactions_commit_seq
ON memory_transactions(result_memory_commit_seq);

CREATE INDEX IF NOT EXISTS idx_memory_transactions_standing
ON memory_transactions(status, semantic_standing);

CREATE INDEX IF NOT EXISTS idx_memory_transactions_compensates
ON memory_transactions(compensates_transaction_uuid);

CREATE TABLE IF NOT EXISTS memory_transaction_standing_events (
    standing_event_uuid TEXT PRIMARY KEY,
    transaction_uuid TEXT NOT NULL,
    from_standing TEXT
        CHECK(from_standing IS NULL OR from_standing IN (
            'PROVISIONAL',
            'STABILIZED_NO_IMMEDIATE_CORRECTION',
            'CONFIRMED_EXPLICIT',
            'REVERTED_BY_USER_CONTROL'
        )),
    to_standing TEXT NOT NULL
        CHECK(to_standing IN (
            'PROVISIONAL',
            'STABILIZED_NO_IMMEDIATE_CORRECTION',
            'CONFIRMED_EXPLICIT',
            'REVERTED_BY_USER_CONTROL'
        )),
    reason_kind TEXT NOT NULL
        CHECK(reason_kind IN (
            'INITIAL_PROVISIONAL_COMMIT',
            'EXPLICIT_USER_AFFIRMATION',
            'NO_IMMEDIATE_CORRECTION_WINDOW',
            'DIRECT_USER_MEMORY_CONTROL',
            'USER_REJECT_OR_UNDO',
            'SYSTEM_RECOVERY'
        )),
    source_turn_uuid TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(transaction_uuid) REFERENCES memory_transactions(transaction_uuid),
    FOREIGN KEY(source_turn_uuid) REFERENCES conversation_turns(turn_uuid)
);

CREATE INDEX IF NOT EXISTS idx_memory_standing_events_transaction
ON memory_transaction_standing_events(transaction_uuid, created_at);

CREATE TABLE IF NOT EXISTS memory_mutations (
    mutation_uuid TEXT PRIMARY KEY,
    transaction_uuid TEXT NOT NULL,
    mutation_order INTEGER NOT NULL CHECK(mutation_order >= 1),
    mutation_kind TEXT NOT NULL
        CHECK(mutation_kind IN (
            'CREATE_ENTITY',
            'CREATE_CLAIM',
            'SUPERSEDE_CLAIM',
            'RETRACT_CLAIM',
            'SET_CLAIM_CONTESTED',
            'ADD_ALIAS',
            'SET_ALIAS_STATUS',
            'CREATE_CONFLICT',
            'RESOLVE_CONFLICT',
            'MERGE_ENTITY',
            'NO_CHANGE'
        )),
    target_uuid TEXT,
    payload_json TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    inverse_payload_json TEXT,
    inverse_payload_hash TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(transaction_uuid) REFERENCES memory_transactions(transaction_uuid),
    UNIQUE(transaction_uuid, mutation_order)
);


CREATE TABLE IF NOT EXISTS semantic_transaction_targets (
    transaction_uuid TEXT NOT NULL,
    target_kind TEXT NOT NULL
        CHECK(target_kind IN ('ENTITY','CLAIM','ALIAS','TRANSITION','CONFLICT','ENTITY_MERGE')),
    target_uuid TEXT NOT NULL,
    effect_kind TEXT NOT NULL
        CHECK(effect_kind IN ('CREATED','UPDATED','SUPERSEDED','RETRACTED','CONTESTED','MERGED','RESTORED')),
    PRIMARY KEY(transaction_uuid, target_kind, target_uuid, effect_kind),
    FOREIGN KEY(transaction_uuid) REFERENCES memory_transactions(transaction_uuid)
);

CREATE INDEX IF NOT EXISTS idx_semantic_transaction_targets_target
ON semantic_transaction_targets(target_kind, target_uuid);

CREATE VIRTUAL TABLE IF NOT EXISTS semantic_entity_aliases_fts USING fts5(
    alias_uuid UNINDEXED,
    entity_uuid UNINDEXED,
    alias_text,
    normalized_alias
);

CREATE VIRTUAL TABLE IF NOT EXISTS semantic_claims_fts USING fts5(
    claim_uuid UNINDEXED,
    subject_entity_uuid UNINDEXED,
    predicate,
    object_search_text
);

CREATE VIEW IF NOT EXISTS semantic_active_claims AS
SELECT c.*
FROM semantic_claims c
JOIN semantic_entities e
  ON e.entity_uuid = c.subject_entity_uuid
WHERE c.status = 'ACTIVE'
  AND e.status IN ('ACTIVE','MERGED');

-- HOST-SIDE INVARIANTS NOT FULLY EXPRESSIBLE IN STATIC SQL:
--
-- 1. Only Persistence Host may write semantic tables.
-- 2. memory_commit_seq increments exactly once per committed semantic transaction.
-- 3. Failed/rolled-back transactions do not increment memory_commit_seq.
-- 4. All writes verify expected base memory_commit_seq before mutation.
-- 5. SINGLE_CURRENT conflicts must be resolved/contested, never silently coexist.
-- 6. Entity merge graph must be acyclic.
-- 7. Permanent UUIDs/short IDs are host-generated.
-- 8. Every committed Claim receives semantic_provenance.
-- 9. FTS rows are maintained in the same transaction as semantic state.
-- 10. Expired TIME_BOUNDED claims are not returned as clean current truth.
-- 11. SEARCH_ONLY aliases aid resolution but are not asserted truth.
-- 12. Historical claims attached to merged entities are not destructively rewritten.
-- 13. Normal conversation-origin semantic transactions commit with semantic_standing=PROVISIONAL.
-- 14. PROVISIONAL effects are excluded from clean Context truth projection by repository policy.
-- 15. STABILIZED_NO_IMMEDIATE_CORRECTION must never be represented as explicit user confirmation.
-- 16. User correction/undo uses a compensating transaction; original transaction/receipt remain immutable.
-- 17. Direct Memory Inspector operations use source_channel=DIRECT_USER_MEMORY_CONTROL.
-- 18. Compensation records inverse payload/basis sufficient for deterministic audit/replay.
-- 19. Current semantic views that need transaction-standing awareness are repository queries, not this simple static view alone.
-- 20. Every semantic_standing transition is appended to memory_transaction_standing_events.
-- 21. Clean Context projection masks the entire delta of PROVISIONAL transactions and exposes the last eligible pre-provisional state.
-- 22. A standing change may update memory_transactions.semantic_standing only in the same host transaction that appends its standing event.
