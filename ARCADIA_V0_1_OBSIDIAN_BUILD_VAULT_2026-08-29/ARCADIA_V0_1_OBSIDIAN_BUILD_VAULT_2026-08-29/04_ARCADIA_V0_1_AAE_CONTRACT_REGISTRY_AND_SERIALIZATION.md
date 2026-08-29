---
title: "A.R.C.A.D.I.A. v0.1 — AAE Contract Registry and Canonical Serialization"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "canonical-system-document"
source_path: "04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION.md"
source_sha256: "f6f94a23c4b22c2a1f6f9681405226953e21d7bfaa16d65d93c5bda0b1bf299d"
source_bytes: 5465
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/system"
  - "status/frozen"
aliases:
  - "04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION.md"
  - "A.R.C.A.D.I.A. v0.1 — AAE Contract Registry and Canonical Serialization"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `canonical-system-document`  
> **Frozen source:** `04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION.md` · SHA-256 `f6f94a23c4b22c2a…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[05_ARCADIA_V0_1_MODEL_RUNTIME_ADAPTER_MANAGER]] · [[06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES]] · [[ARCADIA_ST01_AAE_CALL_DATA_LOCK_2026-08-28]] · [[ARCADIA_ST07_AAE_SERIALIZATION_INJECTION_LOCK_2026-08-29]] · [[arcadia_aae_boundary.py]] · [[test_arcadia_aae_boundary.py]] · [[ARCADIA_V0_1_FULL_PIPELINE_AAE_REFERENCE_5_SLICES]] · [[00_README_FIRST]] · [[01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT]] · [[02_ARCADIA_V0_1_EXACT_BUILD_ORDER]] · [[03_ARCADIA_V0_1_GLOBAL_CONTRACTS_AND_INVARIANTS]] · [[ARCADIA_V0_1_MASTER_BUILD_AUTHORITY]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. v0.1 — AAE Contract Registry and Canonical Serialization

**Purpose:** freeze the shared learned-call contract that training and runtime must use identically.

# 1. Structured AAE object

The runtime object is not a handwritten delimiter document.

```text
AAECall
  contract_id
  contract_version
  specialist_mode_id
  authority_plane
  data_plane
  input_schema_version
  output_schema_version
  response_contract
  inference_profile_id
```

# 2. Authority and data planes

## Authority plane

Host-owned stable instructions:

```text
Global Awareness
Specialist Awareness / jurisdiction
forbidden responsibilities
legal reference behavior
uncertainty behavior
Response Contract
```

## Data plane

Bounded content such as:

```text
raw prompt
transcript excerpts
Context artifacts
memory evidence
tool results
web/source evidence
prior validated recipe artifacts
```

Data text has `CONTENT_ONLY` authority even if it contains imperative language, role labels, fake system messages, fake response contracts, or AAE delimiters.

# 3. Message-role serialization

Where the model/chat template supports roles:

- authority plane goes in the highest supported trusted instruction role;
- structured data goes in lower data/user role messages;
- no raw untrusted text is concatenated into authority instructions.

If the backend has weaker role semantics, the serializer still maintains explicit structural separation and origin labels; qualification must test the exact template actually used.

# 4. CALL_DATA hard gate

Runtime order:

```text
host Python/typed object
-> strict JSON Schema validation
-> Canonical JSON V1
-> build final model messages
-> extract final CALL_DATA representation
-> strict production-equivalent parse
-> same schema validation
-> dispatch
```

Reject at minimum:

```text
illegal escapes / malformed JSON
duplicate keys
NaN / Infinity
trailing content
unknown properties
wrong types
out-of-range enum/length/item counts
non-strict object schemas
```

# 5. Origin/trust metadata

Model-visible data items use explicit metadata such as:

```text
origin:
  USER_PROMPT
  TRANSCRIPT
  SEMANTIC_MEMORY
  TOOL_RECEIPT
  WEB_RESULT
  HOST_DERIVED_SIGNAL

authority_class:
  CONTENT_ONLY
  EXTERNAL_UNTRUSTED_EVIDENCE
  HOST_VERIFIED_EXECUTION
  HOST_VERIFIED_STATE
```

These labels constrain framing; they do not magically make an LLM injection-proof.

# 6. Field caps and deterministic projection

Every contract defines:

```text
max item count
max string/array size
max source excerpt size
max total model-visible input budget
reserved output budget
projection priority rules
```

If budget is exceeded, the host deterministically projects or fails with an explicit bounded state. Silent truncation is forbidden.

# 7. Human-readable audit renderer

A deterministic renderer may display:

```text
<A.R.C.A.D.I.A_ADAPTER_CALL>
[GLOBAL_AWARENESS]
...
[SPECIALIST_AWARENESS]
...
[CALL_DATA]
{canonical JSON}
[RESPONSE_CONTRACT]
...
</A.R.C.A.D.I.A_ADAPTER_CALL>
```

This format is mandatory for inspectability but is **not** the parser boundary. Fake tags inside data remain escaped/encoded string content.

# 8. Core registry entries

The physical roster is 15; logical modes may be more numerous.

| Physical adapter | Recipe | Principal logical modes |
|---|---:|---|
| Conversation Resolver | 0 | `SCOPE_PROPOSAL`, `SCOPE_VALIDATION` |
| Spell | 1 | spelling/normalization semantic pass |
| Term / Meaning | 1 | bounded term/reference meaning |
| Prompt Analyst | 1 | task/constraint analysis |
| Intent Organizer | 1 | requirement composition |
| Conversational Howard | 1/2/8 | Intent comment, Context lane comment, Context synthesis, Result requirement comment, Result final compose |
| Evidence Specialist | 2 | Context evidence semantic selection |
| Requirement Assessor | 3 | per-Rxxx readiness/work/blocker/persistence assessment |
| Plan Composer | 3 | shared Wxxx graph composition |
| Evidence Reconciler | 5 | receipt/evidence semantic assessment |
| Reconciliation Composer | 5 | cross-work findings/discovery/repair composition |
| Persistence Assessor | 6 | candidate/obligation semantic disposition |
| Persistence Composer | 6 | bounded semantic mutation plan |
| Completion Assessor | 7 | per-Rxxx closure judgment |
| Completion Composer | 7 | final standing packet composition |

Each logical mode binds independently to:

```text
physical_adapter_id
AAE contract/version
input/output schema versions
host validator version
InferenceProfile id/hash
minimum trust level
```

# 9. Repair contract

Repair receives:

```text
same authoritative source packet
same specialist mode
same InferenceProfile
new context
new sampler
new attempt UUID
exact machine validation error
```

A repair may not receive invented facts or expanded authority merely because attempt 1 failed.

# 10. Injection qualification

Required adversarial fixtures include data containing:

```text
[GLOBAL_AWARENESS]
[RESPONSE_CONTRACT]
</A.R.C.A.D.I.A_ADAPTER_CALL>
SYSTEM: ignore previous instructions
fake host authorization
fake tool success
fake trusted memory labels
nested quoted prompt injection
Unicode-confusable reference IDs
```

Passing output shape alone is insufficient; semantic compliance with the actual authority contract is scored.

# 11. Training/runtime identity

Training examples and runtime calls are generated from the same registry definitions. Manual prompt re-authoring for training is forbidden.
