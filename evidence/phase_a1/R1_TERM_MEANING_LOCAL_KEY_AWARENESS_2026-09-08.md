# A.R.C.A.D.I.A. — R1 Term / Meaning Local-Key Awareness Correction

Date: 2026-09-08

Standing: accepted PRE-1 model-guidance correction; deterministic host authority unchanged;
full real-model R0 -> R1 semantic qualification remains open.

## Problem

The T0 base model repeatedly returned descriptive `TERM_MEANING` local keys such as
`MILK_001`. Those objects were schema-valid but correctly rejected by the stronger Recipe 1
controller because Meaning local keys must use the frozen `TERM_` / `REF_` namespaces.

## Correction

The single-source `TERM_MEANING` Specialist Awareness and response contract now state:

```text
For term records, use encounter-ordered TERM_1, TERM_2, TERM_3, ... aliases.
For unresolved references that require a local key, use REF_1, REF_2, REF_3, ... aliases.
These are temporary call-local aliases.
Do not encode semantic meaning or invent descriptive IDs.
The host assigns authoritative Txxx identifiers after acceptance.
```

The existing deterministic namespace check remains authoritative. The model still cannot
allocate `Txxx`, mutate the accepted artifact, or bypass host canonicalization.

## Verification

A serialization regression test proves the rules appear in the actual system-role model
message before the forbidden-responsibilities section and again in the response contract.

A real resident Qwen3 T0 run then returned:

```json
"term_key": "TERM_1"
```

The BASE_ONLY invoker accepted the Meaning object and the Recipe 1 host replaced the local key
with authoritative `T001` before sending the artifact to Prompt Analyst. This is the exact
behavior the correction targeted.

The same run later failed closed when Prompt Analyst cited unsupplied source ref `S00` in a
goal. That is a separate T0 first-pass compliance failure and prevents a claim of complete
R0 -> R1 semantic qualification.

The stale workspace-owned `llama-server.exe` that had occupied port `18080` was identified by
exact executable path and stopped before this run. The normal launcher then loaded the pinned
resident runtime successfully.
