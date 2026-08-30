# Phase A Item 9 — Privacy-Minimized Trace Index

Date: 2026-08-30
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- `TracePolicy` copies Config V1 tracing, raw-retention, and training-export
  switches into an immutable versioned Canonical JSON snapshot with a typed
  SHA-256 identity. Disabled tracing cannot silently enable raw capture/export.
- The index accepts only fixed non-content metadata: trace/project/conversation/
  turn identity, locked recipe/slice kind, typed causal references, bounded
  specialist mode, exact runtime/contract/schema/profile hashes, validation and
  first-pass standing, repair count, process epoch, and fixed numeric telemetry.
  There is no arbitrary metadata, prompt, transcript, evidence, model-output,
  filesystem-path, or free-form diagnostic-content field.
- Slice kinds cover raw turn, Recipe artifact, learned call, repair, re-entry,
  tool/evidence, Persistence, Completion, Result/publication, recovery, and
  cross-turn lineage. Learned and repair slices require exact identity hashes;
  repairs require typed call and attempt references.
- Registration requires prior-only parent traces in the same project. Cross-turn
  links require a parent from another turn in the same conversation. Repair call
  references must resolve to an already indexed learned-call trace in the same
  project and turn. This prevents dangling parent/call links and parent cycles.
- Records start only as `NOT_SELECTED` or permanent `NEVER_TRAIN`; held-out input
  mechanically selects `NEVER_TRAIN`. This module exposes no candidate,
  approval, export, trained, or runtime self-promotion operation. Those remain
  separate future training-firewall authorities.
- Optional raw forensic payloads are represented only by a secure-store UUID,
  payload hash, availability flag, and rolling policy deadline. The index never
  stores or decrypts the payload. Capture is rejected when raw tracing is off.
- Pin/unpin transitions are explicit immutable revisions. Pinned records survive
  ordinary retention expiry; unpinned expired records appear in a deterministic
  due set.
- `confirm_raw_deleted` records a tombstone only after the secure payload owner
  supplies the exact live raw UUID and confirms destruction. Tombstones remove
  the live reference/deadline, preserve the non-content payload hash and reason,
  and cannot resurrect. Expiry deletion requires an elapsed deadline and rejects
  pinned traces; explicit owner deletion may remove pinned traces.
- Every registration/lifecycle revision receives a host event UUID, contiguous
  sequence, canonical UTC time, predecessor hash, record hash, and event hash.
  Replay enforces policy identity, nondecreasing chronology, creation ordering,
  unique events, chain integrity, contiguous record revisions, resolved lineage,
  and exact allowed-field transition sets. Optimistic index-head and record-
  revision matching prevent stale updates.
- Actual encrypted raw storage/destruction, owner/debug authorization, candidate
  cascade deletion, and approved dataset manifests remain assigned to their
  later storage, trust, and training components. The next exact item supplies
  the trust registry used to authorize these host operations.

## Evidence

Command: `check.bat`

```text
259 tests passed
Ruff: PASS
strict MyPy: PASS (14 source files)
```

Trace-index tests cover Config V1 policy copying/hash, contradictory policies,
fixed low-content records, `NEVER_TRAIN`, raw capture/deadlines, partial raw
identity rejection, learned/repair identities, canonical mode rejection,
cross-turn/parent/reference rules, telemetry types, disabled registration,
policy binding, dangling parent/repair rejection, matching learned-call repair
lineage, chronological legality, optimistic conflicts, pin/unpin/expiry,
confirmed tombstones, owner deletion, pinned-expiry rejection, hash-chain replay,
deletion/reorder/duplicate/unauthorized-field tampering, immutability, and
canonical content-free rendering.

Gate A remains open for the trust registry and authority-separated storage.
