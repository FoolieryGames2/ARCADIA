---
title: "A.R.C.A.D.I.A. R3 — ST-09 Crash / Replay / Outcome-Uncertainty Lock"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "stress-lock"
source_path: "provenance/stress_locks/ARCADIA_ST09_CRASH_REPLAY_OUTCOME_LOCK_2026-08-29.md"
source_sha256: "0a34c26f01a7a5f043d3f1be0e36f830b171064ba1b4b351292da0d2a8e6e307"
source_bytes: 6804
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/provenance"
  - "type/stress-lock"
  - "status/frozen"
aliases:
  - "ARCADIA_ST09_CRASH_REPLAY_OUTCOME_LOCK_2026-08-29.md"
  - "A.R.C.A.D.I.A. R3 — ST-09 Crash / Replay / Outcome-Uncertainty Lock"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `stress-lock`  
> **Frozen source:** `provenance/stress_locks/ARCADIA_ST09_CRASH_REPLAY_OUTCOME_LOCK_2026-08-29.md` · SHA-256 `0a34c26f01a7a5f0…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY]] · [[R4_TOOL_EXECUTION_V0_1]] · [[ARCADIA_R3_STRESS_RESOLUTION_LEDGER_2026-08-28]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. R3 — ST-09 Crash / Replay / Outcome-Uncertainty Lock

**Date:** 2026-08-29  
**Stress item:** ST-09 — incomplete crash/replay contract for side-effect paths  
**Status:** **CLOSED — DESIGN LOCK**  
**Scope:** external side effects, tool receipts, SQLite semantic persistence receipt freezing, publication/transcript recovery, restart/replay, timeout ambiguity, and outcome uncertainty.

## 1. Core invariant — ST09-G01

> A missing receipt is not proof that an external operation failed. A.R.C.A.D.I.A. MUST NOT infer success or failure across a crash, timeout, network drop, transport interruption, or receipt-loss boundary when the real-world outcome cannot be proven.

When certainty is unavailable, the host owns and preserves the explicit state:

```text
OUTCOME_UNKNOWN
```

Learned specialists may explain host-supplied uncertainty, but they may not upgrade it to success/failure, invent a receipt, assume a retry is safe, or fabricate what the external system did.

## 2. Durable OperationJournal — ST09-G02

Before any side-effecting capability crosses its external boundary, the host MUST persist a durable operation journal record containing at minimum:

```text
operation_uuid
turn_id
requirement/work refs
capability_id + capability_version
request_hash
idempotency_key or null
recovery_policy_id/version
attempt_number
state
created_at / updated_at
provider/external refs when available
verification material when available
receipt_ref when terminally confirmed
```

Minimum lifecycle:

```text
PREPARED
  -> ATTEMPT_ARMED
  -> CONFIRMED_SUCCESS
     | CONFIRMED_FAILURE
     | OUTCOME_UNKNOWN
```

`ATTEMPT_ARMED` means the side effect may have crossed the external boundary. A crash after this state may not be treated as a normal failure.

## 3. Per-capability recovery policy — ST09-G03

Every side-effecting capability declares a host-owned recovery class. Initial classes:

```text
PROVIDER_IDEMPOTENT
VERIFY_THEN_REPLAY
NON_IDEMPOTENT_UNVERIFIABLE
LOCAL_TRANSACTIONAL
```

Rules:

- `PROVIDER_IDEMPOTENT`: retries reuse the original idempotency identity; never mint a fresh semantic operation merely because the process restarted.
- `VERIFY_THEN_REPLAY`: inspect real external state first; replay only after proving the prior effect did not occur.
- `NON_IDEMPOTENT_UNVERIFIABLE`: uncertain attempts are never automatically retried; preserve `OUTCOME_UNKNOWN` pending explicit resolution.
- `LOCAL_TRANSACTIONAL`: use the local transactional store to make semantic mutation + local success proof atomic wherever possible.

Read-only capabilities may use a separate replay-safe policy because they intentionally create no external side effect.

## 4. Tool receipt atomicity — ST09-G04

After a side effect is verified, the journal terminal transition and immutable execution receipt creation MUST commit together in one local database transaction when both are host-local records.

Conceptually:

```text
BEGIN
  journal -> CONFIRMED_SUCCESS / CONFIRMED_FAILURE
  insert immutable RECxxx
  bind RECxxx to operation_uuid / attempt identity
  store verification/provider refs
COMMIT
```

The host MUST NOT publish a success fact merely because dispatch returned without a local terminal receipt/verification path accepted by the capability contract.

## 5. Persistence receipt atomicity — ST09-G05

For semantic SQLite Persistence, the semantic mutation, commit-sequence update, and successful `PRC` record MUST be part of the same SQLite transaction.

```text
BEGIN IMMEDIATE
  semantic mutation(s)
  memory commit sequence mutation
  PRC identity + SUCCESS record
COMMIT
```

If COMMIT exists after restart, the success proof exists. If the transaction rolled back, neither exists.

## 6. Publication / transcript recovery — ST09-G06

Publication is journaled independently from semantic Completion.

Persist at minimum:

```text
publication_attempt_uuid
turn_uuid
result_artifact_ref
result_hash
transport_state
transcript_state
published_external_ref when available
```

If response publication succeeds but transcript persistence fails:

- do not regenerate Result;
- do not rerun Recipes 0–8;
- recover/reconcile transcript state using the frozen Result artifact;
- enforce uniqueness on `turn_uuid + result_hash` (or equivalent authoritative identity) so recovery cannot duplicate a completed exchange.

Publication failure never rewrites frozen Completion standing.

## 7. Restart scan — ST09-G07

On startup, the host scans every nonterminal operation/publication journal entry and applies the exact frozen recovery policy for that capability/version.

Allowed recovery actions are limited to:

```text
VERIFY AND RECOVER CONFIRMED RESULT
SAFE REPLAY USING ORIGINAL OPERATION IDENTITY
PRESERVE OUTCOME_UNKNOWN
```

A restart MUST NOT create new semantic work IDs merely because the process died.

## 8. Model authority prohibition — ST09-G08

Models never decide whether an uncertain side effect happened.

They may consume only host-frozen states/receipts such as:

```text
CONFIRMED_SUCCESS
CONFIRMED_FAILURE
OUTCOME_UNKNOWN
```

and must preserve those distinctions through Reconciliation, Completion, and Result.

Specifically forbidden:

- infer `FAILED` from missing receipt after an armed attempt;
- infer `SUCCESS` from plausible tool behavior;
- claim an email/file/event/message was created without accepted host evidence;
- request blind replay of an unknown non-idempotent operation;
- convert `OUTCOME_UNKNOWN` to a terminal success/failure in prose.

## 9. Crash-injection acceptance gate — ST09-G09

Before ST-09 is considered implementation-complete, deterministic crash/restart tests MUST cover at minimum:

1. crash before dispatch;
2. crash immediately after `ATTEMPT_ARMED`;
3. external success then crash before local receipt commit;
4. receipt commit then crash before Completion;
5. Persistence COMMIT boundary;
6. publication succeeds then crash/failure before transcript commit;
7. timeout/network drop where provider outcome is unverifiable;
8. verify-then-replay path where external state proves no prior effect;
9. idempotent provider replay using same idempotency identity;
10. non-idempotent unknown outcome remains unreplayed.

The required invariant for every test:

> Recovery may verify, deduplicate, replay safely, compensate only when explicitly supported, or remain uncertain. It may never invent reality or blindly duplicate a possibly completed side effect.

## 10. Relationship to later work

- ST-09 does not define trace privacy/retention. That is ST-10.
- ST-09 does not grant models tool authority.
- ST-09 does not promise exactly-once behavior from arbitrary external providers.
- Capability-specific compensation semantics may be added later, but compensation is never assumed to exist.
