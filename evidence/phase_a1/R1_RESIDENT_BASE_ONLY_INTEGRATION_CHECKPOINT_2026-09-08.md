# A.R.C.A.D.I.A. — R0 -> R1 Resident BASE_ONLY Integration Checkpoint

Date: 2026-09-08

Standing: implementation-integrated and deterministic-workstation-gate clean; real-model
T0 semantic qualification remains open; not an adapter, registry, Recipe 2, publication,
or production qualification.

## Integrated bundle

Source archive:

`patch_brige/ARCADIA_R1_RESIDENT_BASE_ONLY_INTEGRATION_SLICE_2026-09-06.zip`

Verified base commit:

`5d7a911c3213ab321ebf62124b5da3e64d1ce079`

The three supplied patches were SHA-256 verified against `SHA256SUMS.txt` and applied in
the bundle's required order:

1. `28ff2e0d8467caf90f73882a6ec118f6f8cd25f22bcde69e8995171bf29746ec`
2. `9c044b8129937cca3e6cb377613cbf206286baa711cf97c80f726b14b47e7eb0`
3. `fa2d3deb8534d030128d8bb2e4c88147cf97b2e3597e74ba0b3010eab3aab4f0`

The integration preserves the frozen boundary:

```text
Recipe 0 Conversation Resolver
  -> frozen ConversationPacket
  -> Recipe 1 Intent host controller
  -> frozen IntentArtifact
  -> optional non-authoritative Intent Comment
  -> STOP: Recipe 2 Context NOT_IMPLEMENTED
```

The model receives no new ID, transcript-write, semantic-memory, tool, publication, or
production authority.

## Workstation gate

Pinned environment:

```text
Python 3.12.10
SQLite 3.49.1 with FTS5
```

Command:

```text
check.bat
```

Result after correcting one deterministic import-order defect in the supplied patch:

```text
pytest: 615 passed
Ruff: PASS
MyPy: PASS (73 source files)
```

## Resident BASE_ONLY smoke evidence

Runtime identity:

```text
foundation model: Qwen/Qwen3-4B-Instruct-2507 candidate
model SHA-256: 4e00d30a00c71456198672a86a155a2935a7201f5112734f7dbf564362243f73
llama.cpp commit: 9a4843cf2f1a3fc8e39f8148e92ee6bfe18e2db6
authority: T0 BASE_ONLY
```

Three bounded resident attempts were made. None completed the full R0 -> R1 path:

1. Checked-in `2048` context / `256` output settings reached `TERM_MEANING`, whose
   response was rejected as truncated invalid JSON.
2. A `4096` context / `1024` output retry was rejected in `SCOPE_PROPOSAL` because the
   model requested history when the authoritative completed-exchange count was zero.
3. A `4096` context / `1024` self-contained-prompt retry reached Meaning and was rejected
   because local key `A1` was outside the frozen `TERM_/REF_` namespace.

These failures show the host boundary failing closed as designed. They do not establish
real-model Recipe 0 or Recipe 1 semantic qualification. No validation was weakened and no
success was inferred from model execution alone.

## Checkpoint conclusion

The newest patch is integrated and its deterministic implementation gate passes on the
pinned workstation. The next evidence-driven task is to characterize and improve the T0
base-model success rate through the existing bounded repair/tuning qualification work,
without granting learned authority or implementing Recipe 2 out of order.
