# A.R.C.A.D.I.A. R3 — ST-01 CALL_DATA Lock

**Date:** 2026-08-28  
**Stress item:** ST-01 — malformed JSON in an exact learned-call `CALL_DATA`  
**Status:** **CLOSED FOR DESIGN / IMPLEMENTED AS SHARED BOUNDARY PROTOTYPE**  
**Scope:** `CALL_DATA` serialization, strict parsing, schema gating, and final rendered-packet pre-dispatch validation only.  
**Explicit non-scope:** whole-AAE injection-safe framing remains ST-07.

## 1. Defect correction

The R3 Slice-4 Result-comment exact call contained a single-backslash Windows path inside JSON. The canonical correction is:

```json
"protected_literals": ["C:\\Arcadia\\exports\\status.txt"]
```

The exact source patch is preserved as `ARCADIA_ST01_R3_TRACE_PATCH.diff`.

## 2. Frozen invariant — ST01-G01

> No AAE `CALL_DATA` is handwritten JSON at runtime. `CALL_DATA` originates as a host-owned structured object, is validated against a strict contract schema, serialized only by Canonical JSON V1, strictly reparsed from the final rendered AAE immediately before dispatch, revalidated against the same schema, and rejected closed on any failure. No specialist invocation may occur after an ST-01 gate failure.

## 3. Required rejection behavior — ST01-G02

The production-equivalent `CALL_DATA` gate must reject at minimum:

- malformed JSON / illegal escapes;
- duplicate object keys;
- non-finite numbers (`NaN`, `Infinity`, `-Infinity`);
- trailing non-JSON content;
- unknown object properties;
- wrong JSON types;
- enum/range/length/item-count violations defined by the contract schema;
- a non-strict object schema that does not explicitly reject unknown properties.

## 4. Required call construction order — ST01-G03

```text
host structured CALL_DATA object
  -> strict contract schema validation
  -> Canonical JSON V1 serialization
  -> insert canonical JSON into rendered AAE
  -> extract CALL_DATA from final rendered AAE
  -> strict production-equivalent JSON parse
  -> same contract schema validation
  -> dispatch allowed
```

Any failure routes to host rejection/repair policy. It does **not** invoke the specialist with a knowingly invalid packet.

## 5. Ownership — ST01-G04

- `SpecialistInvoker` is the only learned-call entry point and owns calling this gate.
- Recipe code passes structured data, never pre-rendered JSON fragments.
- The canonical serializer and strict parser are shared host infrastructure.
- Contract schemas are supplied to the invoker; schema-less learned dispatch is forbidden.
- Schema registry freezing and injection-safe whole-AAE serialization remain ST-07 and are not silently claimed solved here.

## 6. Prototype implementation

`arcadia_aae_boundary.py` implements:

- `strict_json_loads()`
- `canonical_json_dumps()`
- strict-schema enforcement
- JSON Schema Draft 2020-12 validation
- `serialize_call_data()` validate/serialize/reparse/revalidate round trip
- `extract_rendered_call_data()`
- `validate_rendered_aae_call_data()` as the final pre-dispatch gate

`test_arcadia_aae_boundary.py` covers the malformed Windows path plus duplicate-key, non-finite, trailing-content, unknown-field, wrong-type, bound, loose-schema, and final-rendered-AAE rejection cases.

The independent static checker already parses all 87 actual slice `CALL_DATA` blocks rather than only fenced JSON examples. It remains a documentation fixture check; runtime dispatch must use the shared boundary above.

## 7. Acceptance gate

ST-01 remains closed only if all are true:

1. the malformed R3 trace fixture is corrected in the next canonical consolidation;
2. no runtime caller may pass handwritten JSON as `CALL_DATA`;
3. every learned dispatch carries a strict schema;
4. the final rendered `CALL_DATA` is strictly reparsed and revalidated before inference;
5. the boundary unit suite passes;
6. the full exact-call trace checker parses all 87 real calls successfully after the R3 trace correction.

If any item regresses, ST-01 reopens automatically.
