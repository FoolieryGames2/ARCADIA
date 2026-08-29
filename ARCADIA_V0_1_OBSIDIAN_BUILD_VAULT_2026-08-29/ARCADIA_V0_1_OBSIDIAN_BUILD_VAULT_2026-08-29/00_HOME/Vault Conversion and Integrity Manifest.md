---
title: "Vault Conversion and Integrity Manifest"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
generated_navigation: true
tags:
  - "arcadia/v0-1"
  - "type/integrity"
  - "moc/meta"
---

# Vault Conversion and Integrity Manifest

> [!success] Source integrity verified before transformation
> The original `SHA256SUMS.txt` validated successfully for every listed artifact before this vault was generated.

## Preservation policy

1. Existing Markdown source bodies are copied **byte-for-byte** after the generated Obsidian metadata/navigation layer.
2. `.txt`, `.json`, `.sql`, and `.py` sources are retained in full inside syntax-appropriate fenced blocks.
3. `.pyc` binaries are encoded losslessly as Base64 with original byte length and SHA-256 recorded.
4. Generated MOCs and diagrams contain navigation only; they do not supersede frozen source authority.
5. Original filenames and paths are retained in every note's frontmatter.

## Counts

- Original source artifacts: **46**
- Original Markdown files: **35**
- Text/code artifacts converted to Markdown wrappers: **9**
- Binary artifacts preserved as Base64 Markdown recovery notes: **2**
- Generated navigation/MOC notes: **8**

## File map

| Original source | Vault note | Source SHA-256 | Bytes | Role | Preservation mode |
|---|---|---:|---:|---|---|
| `00_README_FIRST.md` | `00_README_FIRST.md` | `72f15887b5281490…` | 4469 | `canonical-system-document` | `markdown-preserved-body` |
| `01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT.md` | `01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT.md` | `dc0df5daaf2ddbe6…` | 12766 | `canonical-system-document` | `markdown-preserved-body` |
| `02_ARCADIA_V0_1_EXACT_BUILD_ORDER.md` | `02_ARCADIA_V0_1_EXACT_BUILD_ORDER.md` | `a517189a1e967d96…` | 11181 | `canonical-system-document` | `markdown-preserved-body` |
| `03_ARCADIA_V0_1_GLOBAL_CONTRACTS_AND_INVARIANTS.md` | `03_ARCADIA_V0_1_GLOBAL_CONTRACTS_AND_INVARIANTS.md` | `6516d99eebb52bce…` | 4208 | `canonical-system-document` | `markdown-preserved-body` |
| `04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION.md` | `04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION.md` | `f6f94a23c4b22c2a…` | 5465 | `canonical-system-document` | `markdown-preserved-body` |
| `05_ARCADIA_V0_1_MODEL_RUNTIME_ADAPTER_MANAGER.md` | `05_ARCADIA_V0_1_MODEL_RUNTIME_ADAPTER_MANAGER.md` | `d5b1b08f45f720d2…` | 5718 | `canonical-system-document` | `markdown-preserved-body` |
| `06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES.md` | `06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES.md` | `27ad7a32c2248caf…` | 4963 | `canonical-system-document` | `markdown-preserved-body` |
| `07_ARCADIA_V0_1_SOURCE_POLICY_REGISTRY.md` | `07_ARCADIA_V0_1_SOURCE_POLICY_REGISTRY.md` | `c457569233beb558…` | 3011 | `canonical-system-document` | `markdown-preserved-body` |
| `08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY.md` | `08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY.md` | `7de782b9125e86e3…` | 4798 | `canonical-system-document` | `markdown-preserved-body` |
| `09_ARCADIA_V0_1_PERFORMANCE_FAST_PATH.md` | `09_ARCADIA_V0_1_PERFORMANCE_FAST_PATH.md` | `717c81eace56f1cd…` | 3082 | `canonical-system-document` | `markdown-preserved-body` |
| `10_ARCADIA_V0_1_R3_TO_V0_1_CHANGELOG.md` | `10_ARCADIA_V0_1_R3_TO_V0_1_CHANGELOG.md` | `4bef24c96db0c961…` | 3949 | `canonical-system-document` | `markdown-preserved-body` |
| `ARCADIA_V0_1_BUNDLE_MANIFEST.json` | `ARCADIA_V0_1_BUNDLE_MANIFEST.json.md` | `cbfde5c9b1090810…` | 1401 | `integrity-manifest` | `text-fenced-full-content` |
| `ARCADIA_V0_1_DOCUMENT_VALIDATION_REPORT.txt` | `ARCADIA_V0_1_DOCUMENT_VALIDATION_REPORT.txt.md` | `5c4b060c186e6405…` | 1014 | `validation-report` | `text-fenced-full-content` |
| `ARCADIA_V0_1_MASTER_BUILD_AUTHORITY.md` | `ARCADIA_V0_1_MASTER_BUILD_AUTHORITY.md` | `6f4ade64f4910fa4…` | 55192 | `master-build-authority` | `markdown-preserved-body` |
| `SHA256SUMS.txt` | `SHA256SUMS.txt.md` | `de817029f765a2e6…` | 5242 | `integrity-manifest` | `text-fenced-full-content` |
| `provenance/ARCADIA_R3_STRESS_RESOLUTION_LEDGER_2026-08-28.md` | `provenance/ARCADIA_R3_STRESS_RESOLUTION_LEDGER_2026-08-28.md` | `de482e4b53a2e68a…` | 4566 | `provenance` | `markdown-preserved-body` |
| `provenance/CONSOLIDATION_NOTES.md` | `provenance/CONSOLIDATION_NOTES.md` | `fd143b43cc48a02e…` | 1370 | `provenance` | `markdown-preserved-body` |
| `provenance/stress_locks/ARCADIA_PERF01_DETERMINISTIC_FAST_PATH_LOCK_2026-08-29.md` | `provenance/stress_locks/ARCADIA_PERF01_DETERMINISTIC_FAST_PATH_LOCK_2026-08-29.md` | `5c8147d1851fdb5f…` | 7976 | `stress-lock` | `markdown-preserved-body` |
| `provenance/stress_locks/ARCADIA_ST01_AAE_CALL_DATA_LOCK_2026-08-28.md` | `provenance/stress_locks/ARCADIA_ST01_AAE_CALL_DATA_LOCK_2026-08-28.md` | `6accd7f2070a7ce5…` | 3958 | `stress-lock` | `markdown-preserved-body` |
| `provenance/stress_locks/ARCADIA_ST03_TRANSACTIONAL_HOT_SWAP_LOCK_2026-08-28.md` | `provenance/stress_locks/ARCADIA_ST03_TRANSACTIONAL_HOT_SWAP_LOCK_2026-08-28.md` | `f0f47042ec2d3501…` | 4129 | `stress-lock` | `markdown-preserved-body` |
| `provenance/stress_locks/ARCADIA_ST04_ATOMIC_ADAPTER_LEASE_LOCK_2026-08-28.md` | `provenance/stress_locks/ARCADIA_ST04_ATOMIC_ADAPTER_LEASE_LOCK_2026-08-28.md` | `a05518cb3b7a5e59…` | 5191 | `stress-lock` | `markdown-preserved-body` |
| `provenance/stress_locks/ARCADIA_ST05_RUNTIME_HEALTH_POISON_LOCK_2026-08-29.md` | `provenance/stress_locks/ARCADIA_ST05_RUNTIME_HEALTH_POISON_LOCK_2026-08-29.md` | `c6decaede8f7918d…` | 5892 | `stress-lock` | `markdown-preserved-body` |
| `provenance/stress_locks/ARCADIA_ST06_INFERENCE_PROFILE_QUALIFICATION_LOCK_2026-08-29.md` | `provenance/stress_locks/ARCADIA_ST06_INFERENCE_PROFILE_QUALIFICATION_LOCK_2026-08-29.md` | `d4c99cca7b9d476f…` | 7369 | `stress-lock` | `markdown-preserved-body` |
| `provenance/stress_locks/ARCADIA_ST07_AAE_SERIALIZATION_INJECTION_LOCK_2026-08-29.md` | `provenance/stress_locks/ARCADIA_ST07_AAE_SERIALIZATION_INJECTION_LOCK_2026-08-29.md` | `5fc360e1d3878eaf…` | 9138 | `stress-lock` | `markdown-preserved-body` |
| `provenance/stress_locks/ARCADIA_ST08_SOURCE_QUALITY_POLICY_LOCK_2026-08-29.md` | `provenance/stress_locks/ARCADIA_ST08_SOURCE_QUALITY_POLICY_LOCK_2026-08-29.md` | `98c81980b3c6bb38…` | 6659 | `stress-lock` | `markdown-preserved-body` |
| `provenance/stress_locks/ARCADIA_ST09_CRASH_REPLAY_OUTCOME_LOCK_2026-08-29.md` | `provenance/stress_locks/ARCADIA_ST09_CRASH_REPLAY_OUTCOME_LOCK_2026-08-29.md` | `0a34c26f01a7a5f0…` | 6804 | `stress-lock` | `markdown-preserved-body` |
| `provenance/stress_locks/ARCADIA_ST10_TRACE_PRIVACY_TRAINING_FIREWALL_LOCK_2026-08-29.md` | `provenance/stress_locks/ARCADIA_ST10_TRACE_PRIVACY_TRAINING_FIREWALL_LOCK_2026-08-29.md` | `a9aa924a0750854f…` | 8634 | `stress-lock` | `markdown-preserved-body` |
| `recipes/R0_CONVERSATION_RESOLVER_V0_1.md` | `recipes/R0_CONVERSATION_RESOLVER_V0_1.md` | `f6361279aa8b3ff4…` | 2714 | `recipe-contract` | `markdown-preserved-body` |
| `recipes/R1_INTENT_V0_1.md` | `recipes/R1_INTENT_V0_1.md` | `82356e106fb1f27a…` | 27274 | `recipe-contract` | `markdown-preserved-body` |
| `recipes/R2_CONTEXT_V0_1.md` | `recipes/R2_CONTEXT_V0_1.md` | `c345820c8911eeb0…` | 56184 | `recipe-contract` | `markdown-preserved-body` |
| `recipes/R3_DECISION_V0_1.md` | `recipes/R3_DECISION_V0_1.md` | `ee3621034dd91f26…` | 46193 | `recipe-contract` | `markdown-preserved-body` |
| `recipes/R4_TOOL_EXECUTION_V0_1.md` | `recipes/R4_TOOL_EXECUTION_V0_1.md` | `c94cbeb8a332c234…` | 41886 | `recipe-contract` | `markdown-preserved-body` |
| `recipes/R5_RECONCILIATION_V0_1.md` | `recipes/R5_RECONCILIATION_V0_1.md` | `11f0c17d5722f516…` | 73437 | `recipe-contract` | `markdown-preserved-body` |
| `recipes/R6_PERSISTENCE_V0_1.md` | `recipes/R6_PERSISTENCE_V0_1.md` | `e7c2a02e3698631f…` | 84692 | `recipe-contract` | `markdown-preserved-body` |
| `recipes/R7_COMPLETION_V0_1.md` | `recipes/R7_COMPLETION_V0_1.md` | `d67a952880541049…` | 40161 | `recipe-contract` | `markdown-preserved-body` |
| `recipes/R8_RESULT_V0_1.md` | `recipes/R8_RESULT_V0_1.md` | `df99133210a4089f…` | 36297 | `recipe-contract` | `markdown-preserved-body` |
| `reference/ARCADIA_R3_INDEPENDENT_STRESS_TEST_2026-08-29.md` | `reference/ARCADIA_R3_INDEPENDENT_STRESS_TEST_2026-08-29.md` | `15f5f1de4ed4e187…` | 16172 | `reference` | `markdown-preserved-body` |
| `reference/ARCADIA_V0_1_FULL_PIPELINE_AAE_REFERENCE_5_SLICES.md` | `reference/ARCADIA_V0_1_FULL_PIPELINE_AAE_REFERENCE_5_SLICES.md` | `1b5c8334690ee9ba…` | 351849 | `reference` | `markdown-preserved-body` |
| `reference/ST01_BOUNDARY_UNIT_TEST.txt` | `reference/ST01_BOUNDARY_UNIT_TEST.txt.md` | `f82ab6a801a5e3fb…` | 1567 | `validation-evidence` | `text-fenced-full-content` |
| `reference/TRACE_STATIC_CHECK.txt` | `reference/TRACE_STATIC_CHECK.txt.md` | `5ec49a662677ff66…` | 808 | `validation-evidence` | `text-fenced-full-content` |
| `reference_impl/__pycache__/arcadia_aae_boundary.cpython-313.pyc` | `reference_impl/__pycache__/arcadia_aae_boundary.cpython-313.pyc.md` | `e9fe5c59b419f8af…` | 10380 | `reference-implementation` | `binary-base64-lossless` |
| `reference_impl/__pycache__/test_arcadia_aae_boundary.cpython-313.pyc` | `reference_impl/__pycache__/test_arcadia_aae_boundary.cpython-313.pyc.md` | `6057eb7ad1db4cf5…` | 6414 | `reference-implementation` | `binary-base64-lossless` |
| `reference_impl/arcadia_aae_boundary.py` | `reference_impl/arcadia_aae_boundary.py.md` | `3f38449d8add27b0…` | 7271 | `reference-implementation` | `text-fenced-full-content` |
| `reference_impl/arcadia_r3_static_stress_check.py` | `reference_impl/arcadia_r3_static_stress_check.py.md` | `6941a8e7ceb147ba…` | 5722 | `reference-implementation` | `text-fenced-full-content` |
| `reference_impl/test_arcadia_aae_boundary.py` | `reference_impl/test_arcadia_aae_boundary.py.md` | `c1912ed5411d63b8…` | 3941 | `reference-implementation` | `text-fenced-full-content` |
| `storage/ARCADIA_PERSISTENCE_SQLITE_SCHEMA_V0_1.sql` | `storage/ARCADIA_PERSISTENCE_SQLITE_SCHEMA_V0_1.sql.md` | `c94a5d5a5ada677d…` | 16134 | `storage-schema` | `text-fenced-full-content` |
