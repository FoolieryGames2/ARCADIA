# A.R.C.A.D.I.A. R3 — ST-06 Inference Profile / Qualification Identity Lock

**Date:** 2026-08-29  
**Stress item:** ST-06 — qualification identity is incomplete  
**Status:** **CLOSED — design lock**  
**Scope:** output-affecting inference configuration, per-specialist/per-mode profiles, qualification identity, fresh sampler construction, deterministic qualification seeding, and receipt identity.

## 1. Frozen principle

Qualification belongs to the complete learned-runtime configuration, not merely the base GGUF and adapter hashes.

Every learned specialist mode MUST bind to one immutable, host-owned `InferenceProfile` whose content includes every configuration choice that can materially change model-visible input or generated output.

Changing an output-affecting setting creates a new qualification target.

## 2. Mode-specific profiles — ST06-G01

Inference settings are NOT globally fixed across a runtime epoch.

A.R.C.A.D.I.A. may bind different profiles to different specialist modes while sharing the same base model and adapter residency system.

Examples:

```text
Intent / Meaning / Assessor
  -> low-variance structured profile

Analyst / Composer
  -> mode-appropriate bounded reasoning profile

Conversational Howard
  -> more expressive profile where contract permits

Result exact-literal mode
  -> tightly constrained / near-deterministic profile

Repair mode
  -> dedicated constrained repair profile
```

The semantic binding is conceptually:

```text
specialist_mode_id
  + physical_adapter_id (or BASE_ONLY_TEST_MODE)
  + AAE contract / schemas
  + InferenceProfile
```

A profile change for one specialist/mode does not automatically invalidate unrelated specialist/mode qualifications.

## 3. InferenceProfile required coverage — ST06-G02

At minimum, the immutable profile MUST cover:

### Prompt/rendering identity
- chat template identity/version;
- prompt serializer identity/version;
- message-role/rendering policy where applicable.

### Tokenizer identity
- tokenizer identity/version/hash as available;
- tokenizer overrides or special-token policy.

### Context and budget
- `n_ctx` / context parameters;
- token-budget policy version;
- reserved output budget;
- truncation/projection policy if it can affect model-visible input.

### Sampler chain
- ordered sampler chain;
- temperature;
- top-p;
- top-k;
- min-p where used;
- repetition/frequency/presence penalties where used;
- grammar/constrained-decoding identity where used;
- seed policy.

### Generation
- maximum output tokens;
- stop policy version;
- exact stop sequences / stop-token policy;
- any other generation limit that changes output behavior.

### Qualification-sensitive backend settings
- deterministic GPU/backend settings or inference flags relied upon by qualification.

Transient telemetry such as current HOT pool composition, load latency, memory usage, or eviction victim is NOT part of the profile unless it directly changes model behavior by policy.

## 4. Canonical identity — ST06-G03

The profile MUST be serialized under Canonical JSON V1 and hashed:

```text
inference_profile_hash = SHA256(CanonicalJSON(InferenceProfile))
```

The exact learned-runtime qualification identity MUST include `inference_profile_hash` in addition to the existing base/adapter/runtime/AAE/schema/validator identities.

Therefore:

```text
same base hash
+ same adapter hash
+ same runtime/build versions
+ same AAE/schema/validator versions
+ DIFFERENT inference_profile_hash
= DIFFERENT qualification target
```

No existing trust certificate may silently transfer across a profile-hash change.

## 5. Fresh sampler per attempt — ST06-G04

Fresh KV/context alone is insufficient for call isolation.

Every inference attempt MUST construct:

```text
fresh llama_context
+
fresh sampler chain built from the bound InferenceProfile
```

This applies independently to:

- first-pass specialist calls;
- repair attempts;
- retries that legally re-enter the learned contract;
- BASE_ONLY_TEST_MODE qualification calls;
- adapter-backed qualification calls.

Sampler/RNG state MUST NOT be inherited across attempts.

## 6. Qualification seed policy — ST06-G05

Qualification uses a deterministic seed policy so base-only and adapter-backed runs can be compared under the same inference conditions.

A frozen fixture MUST either contain or deterministically derive its qualification seed.

The comparison boundary is:

```text
same frozen fixture
same AAE / packet builder / schemas / validators
same InferenceProfile
same qualification seed policy + realized seed
BASE_ONLY_TEST_MODE
vs.
BASE + adapter
```

Production may use another explicitly defined seed policy (for example random-per-attempt) if the profile specifies it. The policy remains part of `inference_profile_hash`, and the realized seed is recorded per attempt.

## 7. Receipt requirements — ST06-G06

Activation/inference observability MUST record enough identity to reproduce or diagnose the call. At minimum:

```text
inference_profile_id
inference_profile_hash
sampler_instance_uuid
sampler_fresh = true
seed_policy
actual_seed
context_parameters_hash
prompt_render_hash
```

`prompt_render_hash` identifies the exact rendered model input produced by the canonical prompt serializer. Exact rendered content may be retained under the separate trace/privacy policy; the hash is always cheap identity evidence.

## 8. BASE_ONLY_TEST_MODE compatibility — ST06-G07

The first plain-GGUF baseline remains valid and expected.

`BASE_ONLY_TEST_MODE` binds the same specialist-mode InferenceProfile used for the corresponding adapter qualification while applying no LoRA.

Poor semantic performance does not alter mechanical runtime health under ST-05. It is qualification evidence.

## 9. Qualification invalidation rules — ST06-G08

Requalification is required when any qualification-bound field changes, including but not limited to:

- temperature / sampler chain changes;
- token limits / context budget changes;
- tokenizer or tokenizer override changes;
- chat template or prompt serializer changes;
- stop rules change;
- grammar/constrained decoding changes;
- seed policy changes;
- qualification-sensitive backend setting changes.

A runtime may continue to execute an unqualified profile only at whatever low trust/authority tier policy explicitly permits; it MUST NOT inherit the prior profile's qualification status.

## 10. Acceptance tests

At minimum:

```text
test_profile_canonical_hash_stable
test_temperature_change_changes_profile_hash
test_token_budget_change_changes_profile_hash
test_stop_policy_change_changes_profile_hash
test_template_change_changes_profile_hash
test_unrelated_mode_profile_change_does_not_change_other_mode_hash
test_fresh_sampler_created_each_attempt
test_repair_gets_fresh_sampler_and_context
test_no_sampler_rng_state_bleed_across_calls
test_base_only_and_adapter_qualification_use_same_profile_and_seed
test_profile_hash_in_qualification_identity
test_profile_hash_and_realized_seed_in_receipt
test_old_qualification_not_reused_after_profile_change
```

## 11. Explicit non-claims

This lock does not choose final numerical temperature/top-p/token values for every specialist. It creates the safe/versioned mechanism that allows each adapter/mode to be tuned later without one global temperature/token policy spanning the epoch.
