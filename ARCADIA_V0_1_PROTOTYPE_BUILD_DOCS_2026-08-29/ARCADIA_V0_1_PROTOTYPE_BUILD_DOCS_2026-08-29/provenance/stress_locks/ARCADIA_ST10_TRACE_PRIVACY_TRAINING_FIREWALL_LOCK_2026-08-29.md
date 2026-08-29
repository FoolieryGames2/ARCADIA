# A.R.C.A.D.I.A. R3 — ST-10 Trace Privacy / Retention / Training-Firewall Lock

**Date:** 2026-08-29  
**Stress item:** ST-10 — persistent full traces lack a supplied data-safety policy  
**Status:** **CLOSED — DESIGN LOCK**  
**Scope:** the complete A.R.C.A.D.I.A. conversational/job lineage: user ingress, Recipes 0–8, all learned calls and repairs, Context re-entry/revisions, work/tool/evidence receipts, Reconciliation, Persistence, Completion, Result/publication, transcript linkage, restart/recovery events, and cross-turn lineage across continuing back-and-forth conversation.

## 1. Core scope invariant — ST10-G01

> Trace safety applies to the full turn graph and every model-visible or host-generated trace fragment, regardless of which recipe, specialist, repair attempt, re-entry path, tool, evidence source, persistence step, publication step, or conversation turn produced it.

No recipe or slice receives an implicit privacy exemption. Cross-turn links may preserve lineage, but linkage does not convert diagnostic trace content into conversation memory, semantic memory, Context, or training data.

## 2. Four trace/training domains — ST10-G02

A.R.C.A.D.I.A. separates observability and training into four logically/physically distinct domains:

```text
1. TRACE_INDEX
2. SECURE_RAW_TRACE
3. TRAINING_CANDIDATE_QUARANTINE
4. TRAINING_APPROVED_DATASET
```

No automatic transition from one domain to the next is allowed merely because a call succeeded, validated, received positive feedback, or was persisted.

## 3. TRACE_INDEX — ST10-G03

Long-lived trace index records may retain non-content identity/provenance/telemetry required for debugging and qualification, including:

```text
trace_uuid
conversation_uuid / turn_uuid
recipe / specialist / mode
artifact/call/attempt refs
base + adapter identity
AAE contract + schema versions
InferenceProfile identity
validation result
repair count
first-pass standing
latency + token/load telemetry
runtime/process epoch
activation/operation/publication refs
raw_trace_available flag
training_state
deletion/tombstone state
```

Raw private prompt/transcript/evidence/model-output content is not required in the durable index.

## 4. SECURE_RAW_TRACE — ST10-G04

Exact forensic trace material is sensitive by definition. It may contain:

```text
exact model messages / canonical AAE packet
CALL_DATA
raw + parsed model output
repair attempts
validation errors
bounded transcript/memory/evidence shown to a model
tool request/result material
file paths and other private literals
```

Prototype policy:

- encrypted at rest;
- owner/debug-authorized access only;
- authenticated integrity protection;
- no unprotected plaintext mirror log;
- no automatic external/cloud export;
- finite default retention;
- explicit pinning may extend retention.

Default prototype raw retention is **30 rolling days**, configurable by a versioned host policy. Pinned diagnostics remain until explicitly unpinned/deleted.

## 5. One canonical trace, deterministic human rendering — ST10-G05

A.R.C.A.D.I.A. stores one authoritative canonical trace representation. The human-readable bracketed AAE/audit view is rendered deterministically from that representation.

```text
CANONICAL TRACE
   -> deterministic readable audit rendering
```

Human readability remains mandatory, but the system does not need a second unprotected copy of the same private packet solely for readability.

## 6. Trace is not memory — ST10-G06

The following are separate authorities:

```text
raw diagnostic trace
conversation transcript
semantic memory
Context
training dataset
```

A stored trace is never automatically model-retrievable state. To cross into another domain it must pass that domain's explicit host-owned transition/authority rules.

## 7. Training Candidate Quarantine — ST10-G07

Runtime may not write directly into a training dataset.

Candidate extraction copies only the bounded material actually needed for the target specialist/mode into a distinct `TRAINING_CANDIDATE_QUARANTINE` domain.

Sanitization occurs on the candidate copy, not by rewriting the still-retained forensic raw trace. Candidate sanitization may deterministically replace irrelevant sensitive literals, for example:

```text
private path -> <PATH_1>
email -> <EMAIL_1>
secret/token -> <SECRET_1>
```

The exact sanitization profile/version and source trace lineage are recorded.

## 8. Training approval firewall — ST10-G08

Only an explicit host-authorized review operation may transition:

```text
TRAINING_CANDIDATE
    -> TRAINING_APPROVED
```

A model, recipe, validator pass, user-feedback signal, or runtime logger may not self-approve training data.

Training jobs consume only immutable approved dataset manifests containing at minimum:

```text
dataset_export_uuid
target specialist/mode
source candidate/trace refs
sanitization profile/version
candidate + final record hashes
review/approval identity + time
held-out exclusion result
manifest hash
```

Training code may not query the runtime trace store as an implicit dataset.

## 9. Held-out firewall — ST10-G09

Qualification/evaluation fixtures marked held-out receive a permanent `NEVER_TRAIN` classification for that evaluation lineage.

The training export pipeline MUST fail closed if any held-out fixture, derivative carrying prohibited fixture content, or held-out identity enters an export manifest.

Held-out isolation is mechanical, not advisory.

## 10. Secret minimization before model visibility — ST10-G10

Where sensitive values are not semantically required by a specialist, the host should replace them before AAE construction with protected references, e.g.:

```text
<SECRET_REF:S003>
```

This minimizes both model exposure and trace exposure. It is preferred over relying solely on after-the-fact redaction.

## 11. Deletion and lineage — ST10-G11

Owner-authorized deletion of retained raw trace destroys the encrypted raw payload and leaves only the minimum non-content tombstone required for integrity/audit.

Deletion cascades through unapproved candidate/export copies derived from that trace.

If a not-yet-trained approved dataset is affected, its manifest is invalidated/rebuilt before use.

If model weights have already been trained from the deleted source, A.R.C.A.D.I.A. MUST preserve truthful lineage indicating that fact. Deleting source data does not falsely claim to erase already-learned influence from existing weights.

## 12. Prototype access policy — ST10-G12

Initial local prototype roles:

```text
runtime writer:
  append permitted trace/index records

normal app:
  read trace index and permitted readable/redacted diagnostics

owner/debug authority:
  decrypt full raw trace

training candidate exporter:
  create candidate copies only from explicitly selected sources
  cannot self-approve

training approval authority:
  explicitly approve/reject candidate manifests
```

Broader multi-user RBAC is deferred until the deployment model requires it.

## 13. Acceptance gate — ST10-G13

Before persistent full-trace production use, tests MUST prove at minimum:

1. every Recipes 0–8 learned call and repair is covered by the trace policy;
2. Context re-entry/revision trace fragments inherit the same policy;
3. tool/evidence/persistence/publication/restart lineage is indexed without bypassing raw-trace controls;
4. raw payload encryption/decryption authorization works;
5. human-readable rendering reproduces canonical trace deterministically;
6. retention expiry removes raw payload while keeping allowed index/tombstone data;
7. pinned trace survives ordinary expiry and can later be unpinned/deleted;
8. runtime cannot export directly to `TRAINING_APPROVED`;
9. candidate sanitization preserves lineage and uses a versioned policy;
10. held-out material is rejected from training export;
11. deletion cascades through untrained candidate/export copies;
12. trace content is not automatically available to transcript/Context/semantic-memory retrieval;
13. cross-turn conversational lineage preserves references without creating a shadow memory corpus.

## 14. Frozen summary

> A.R.C.A.D.I.A. may keep rich, exact, human-inspectable observability across the entire back-and-forth and all Recipe 0–8 slices, but raw content is a finite-retention encrypted forensic domain. Trace, transcript, semantic memory, Context, and training are separate authorities. Training requires candidate quarantine plus explicit approval, held-out exclusion, and immutable lineage. No runtime success path automatically converts private traces into model memory or training data.
