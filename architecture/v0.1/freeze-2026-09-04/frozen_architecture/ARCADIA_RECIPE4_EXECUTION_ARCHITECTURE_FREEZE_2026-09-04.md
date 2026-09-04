# A.R.C.A.D.I.A. Recipe 4 — Execution Architecture Freeze

**Date:** 2026-09-04  
**Standing:** Architecturally frozen; implementation/testing remains open.

## Purpose

Execution performs already-authorized work. It does not reinterpret why the work exists.

## Semantic ingress

```json
{
  "decision": {
    "artifact_ref": "DR001",
    "hash": "sha256:..."
  },
  "execution_scope": ["W001", "W002"]
}
```

`execution_scope` is an authority boundary. Execution may not silently add prerequisite work outside it.

## Integrity gate

Before request compilation, host validates Decision existence/hash/freeze, scope membership, active/supersession/retry state, in-flight conflicts, capability identity/current availability, work-class compatibility, dependencies, permissions/policy, resource/path rules, and idempotency requirements.

Failure before concrete request compilation creates no fake request or receipt.

## W → TRQ contract

`Wxxx` = semantic executable work.  
`TRQxxx` = exact proposed operation.

Candidate common request:

```json
{
  "tool_request_id": "TRQ001",
  "decision_ref": "DR001",
  "work_id": "W001",
  "capability_id": "WEB_SEARCH",
  "capability_version": "1",
  "operation_kind": "SEARCH",
  "arguments": {"query": "..."},
  "input_refs": [],
  "attempt_number": 1,
  "idempotency_key": null
}
```

Host compiler may copy, deterministic-select/map, canonicalize, validate, resolve exact refs, and apply host policy/defaults. It may not reinterpret, summarize semantically, invent, broaden, narrow by judgment, or guess missing values.

## Invocation / receipt

`RECxxx` = what actually happened operationally.

Candidate common receipt:

```json
{
  "receipt_id": "REC001",
  "tool_request_id": "TRQ001",
  "execution_status": "SUCCESS",
  "started_at": "...",
  "finished_at": "...",
  "result_items": [],
  "error": null,
  "side_effect_confirmation": null,
  "operation_journal_ref": null,
  "receipt_hash": "sha256:..."
}
```

Operational statuses include bounded forms such as `SUCCESS`, `PARTIAL`, `NO_RESULT`, `FAILED`, `TIMEOUT`, `REJECTED_BEFORE_EXECUTION`, `CANCELLED`, and `OUTCOME_UNKNOWN`.

`SUCCESS` proves execution protocol, not semantic establishment.

## State-changing attempt lifecycle

Side-effecting operations use durable OperationJournal states:

```text
PREPARED
ATTEMPT_ARMED
CONFIRMED_SUCCESS
CONFIRMED_FAILURE
OUTCOME_UNKNOWN
```

`ATTEMPT_ARMED` must be durable before crossing the external side-effect boundary. If certainty is lost after arming, absence of a success receipt is not proof of failure.

Recovery classes may include:

- `PROVIDER_IDEMPOTENT`
- `VERIFY_THEN_REPLAY`
- `NON_IDEMPOTENT_UNVERIFIABLE`

`OUTCOME_UNKNOWN` is never guessed away.

## Retry boundary

Transport retry is not semantic retry.

Automatic retry is bounded and only for host-classified safely-repeatable transport failure of the same authorized operation. Semantic insufficiency, irrelevant results, disagreement, discovery, or repair goes through Reconciliation and possibly Decision re-entry.

Each attempt is a new immutable `TRQxxx` and corresponding `RECxxx`.

## Scheduler

Scheduler is deterministic host logic. Runnable state is derived from:

- execution scope;
- authoritative dependencies;
- execution ledger state;
- current capability availability;
- capability concurrency policy;
- integrity-gate success.

No model-authored `parallel_group` is needed. Equally eligible work may use deterministic W-ID ordering when slots are limited.

A dependent work item is released only when its dependency can be satisfied operationally without new semantic interpretation. Otherwise the result must go through Reconciliation/re-entry.

## Finalizer / ER

Execution Finalizer requires no scoped `Wxxx` still `IN_FLIGHT`, valid W→TRQ→REC lineage, valid attempt ordering, correct no-request/no-receipt states, preserved unknown states, and required OperationJournal resolution.

Candidate immutable result:

```json
{
  "execution_id": "ER001",
  "schema_version": "execution_result@1",
  "execution_hash": "sha256:...",
  "decision": {"artifact_ref": "DR001", "hash": "sha256:..."},
  "execution_scope": ["W001", "W002"],
  "work_results": [
    {
      "work_id": "W001",
      "state": "SUCCEEDED",
      "tool_request_refs": ["TRQ001"],
      "receipt_refs": ["REC001"]
    }
  ]
}
```

Recipe 5 receives only the frozen `ERxxx` ref/hash.
