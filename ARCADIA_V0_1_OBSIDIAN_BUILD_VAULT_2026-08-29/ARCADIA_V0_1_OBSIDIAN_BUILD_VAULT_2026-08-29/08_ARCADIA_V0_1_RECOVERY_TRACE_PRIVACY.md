---
title: "A.R.C.A.D.I.A. v0.1 — Recovery, Trace Privacy, and Training Firewall"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "canonical-system-document"
source_path: "08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY.md"
source_sha256: "7de782b9125e86e3cd21374a7454f0adc66e684d3348506a97db7fbb9dd53c76"
source_bytes: 4798
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/system"
  - "status/frozen"
aliases:
  - "08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY.md"
  - "A.R.C.A.D.I.A. v0.1 — Recovery, Trace Privacy, and Training Firewall"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `canonical-system-document`  
> **Frozen source:** `08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY.md` · SHA-256 `7de782b9125e86e3…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[R4_TOOL_EXECUTION_V0_1]] · [[R6_PERSISTENCE_V0_1]] · [[R8_RESULT_V0_1]] · [[ARCADIA_ST09_CRASH_REPLAY_OUTCOME_LOCK_2026-08-29]] · [[ARCADIA_ST10_TRACE_PRIVACY_TRAINING_FIREWALL_LOCK_2026-08-29]] · [[00_README_FIRST]] · [[01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT]] · [[03_ARCADIA_V0_1_GLOBAL_CONTRACTS_AND_INVARIANTS]] · [[ARCADIA_V0_1_MASTER_BUILD_AUTHORITY]] · [[ARCADIA_ST05_RUNTIME_HEALTH_POISON_LOCK_2026-08-29]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. v0.1 — Recovery, Trace Privacy, and Training Firewall

# Part A — Side-effect crash/replay

## A1. OperationJournal

Before an external side-effect attempt crosses its execution boundary, persist a journal record.

States:

```text
PREPARED
ATTEMPT_ARMED
CONFIRMED_SUCCESS
CONFIRMED_FAILURE
OUTCOME_UNKNOWN
```

Once ATTEMPT_ARMED is durable, a crash means the effect **may** have occurred. Absence of a success receipt is not proof of failure.

## A2. Capability recovery classes

```text
PROVIDER_IDEMPOTENT
  replay same idempotency key; provider deduplicates

VERIFY_THEN_REPLAY
  query external state first; replay only after proving no effect

NON_IDEMPOTENT_UNVERIFIABLE
  never auto-retry an uncertain armed attempt; remain OUTCOME_UNKNOWN
```

Read-only capabilities are separately classified and normally replayable under their own transport policy.

## A3. Save File prototype

Use atomic write where possible, post-write verification, desired content hash, and stable idempotency identity. After restart:

```text
matching file/hash -> recovered confirmed success
provably absent -> safe replay if policy permits
cannot determine -> OUTCOME_UNKNOWN
```

## A4. Persistence PRC atomicity

For semantic Persistence, successful semantic mutations and the durable PRC-success row should commit inside the same SQLite transaction. Either the semantic commit and its local proof exist together or both roll back.

## A5. PublicationJournal

Result publication and transcript commit are distinct.

Journal at least:

```text
turn_uuid
result_hash
publication_attempt_uuid
transport_state
transcript_state
```

If publication succeeds but transcript commit fails, recover the transcript relation for the same immutable `result_hash`; do not regenerate Result or rerun the semantic pipeline.

## A6. Model prohibition

Models never decide an uncertain external outcome. OUTCOME_UNKNOWN propagates through Reconciliation/Completion/Result honestly until host verification changes it.

# Part B — Trace scope and privacy

## B1. Scope

Trace policy covers the complete causal graph:

```text
raw turn
Recipe 0–8 artifacts
all learned calls
all repair attempts
all re-entry slices
all tool/evidence receipts
Persistence transactions
Completion
Result/publication
cross-turn lineage/back-and-forth references
```

## B2. Four trace/training domains

### TRACE INDEX
Long-lived low-content metadata:

```text
trace/call/turn IDs
recipe/mode/runtime identities
schema/AAE/InferenceProfile hashes
validation/repair metrics
timings/tokens
raw trace availability flag
training status
deletion tombstone state
```

### SECURE RAW TRACE
Exact forensic packet/output data. Sensitive by definition.

Prototype requirements:

```text
encrypted at rest
owner/debug authority only
no plaintext mirror log
finite default retention (prototype default 30 days)
explicit PIN can extend retention
```

### TRAINING CANDIDATE QUARANTINE
A separate copy created only by explicit extraction. Copy only fields needed for the target specialist. Sanitization/redaction happens on this copy, not by corrupting the exact forensic source.

### TRAINING_APPROVED
Only explicit review/host authorization can promote candidate data. Runtime/model/validation success cannot self-promote.

## B3. Secret minimization

Where credentials/tokens/passwords need not be model-visible, replace them before AAE construction with host-held protected references such as `<SECRET_REF:S003>`. What the model never sees, the trace need not retain.

## B4. Held-out firewall

Frozen qualification fixtures are permanently classified:

```text
NEVER_TRAIN
```

Training export rejects them regardless of later convenience.

## B5. Dataset manifest

Approved exports record:

```text
dataset_export_uuid
target adapter/mode
source trace refs
sanitization profile version
record hashes
review/approval identity and time
heldout_exclusion_check
manifest hash
```

Training consumes manifests, never arbitrary trace DB queries.

## B6. Deletion

Deleting a raw trace destroys its encrypted payload and leaves a minimal safe tombstone/index as policy permits. Untrained candidate/export copies cascade-delete/revoke. If already-trained weights consumed the record, lineage records that fact; deleting JSON cannot truthfully claim to erase influence already embedded in weights.

## B7. Trace is not memory

Normal models cannot retrieve arbitrary diagnostic traces merely because they exist. Any content must cross an explicit host-owned transition into transcript, Context, semantic memory, or approved training data.

## B8. Human-readable view

The authoritative canonical machine trace deterministically renders the readable AAE/audit view. Do not store a second uncontrolled plaintext duplicate solely for readability.
