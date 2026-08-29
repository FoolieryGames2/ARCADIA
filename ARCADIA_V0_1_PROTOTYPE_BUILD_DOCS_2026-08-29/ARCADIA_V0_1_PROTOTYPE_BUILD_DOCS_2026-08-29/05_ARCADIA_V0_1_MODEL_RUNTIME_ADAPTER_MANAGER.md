# A.R.C.A.D.I.A. v0.1 — ModelRuntime + AdapterManager Specification

# 1. Canonical runtime

```text
ONE long-lived compatible base GGUF
+ host-owned LoRA GGUF adapter library
+ bounded committed HOT pool
+ temporary transactional STAGING slot/headroom
+ one standard ACTIVE adapter per learned call
+ fresh context + fresh sampler per attempt
```

Recipes never load/free/apply LoRAs.

# 2. Ownership

```text
ModelRuntime:
  base model lifetime
  context/sampler create/destroy
  raw libllama adapter primitives through backend wrapper
  raw inference
  backend/build identity
  memory telemetry

AdapterManager:
  registry readiness
  COLD/READY/HOT
  STAGING transactions
  leases/generations/epochs
  pin/protect policy
  load/eviction commitment
  health routing

SpecialistInvoker:
  logical binding
  atomic lease acquisition
  AAE construction
  inference profile
  output validation/repair
  trace/activation receipt
```

# 3. Residency

```text
COLD: registered, no live adapter handle, readiness not current for epoch
READY: integrity/base/contract checked, no live adapter handle
HOT: manager owns a valid live adapter handle
ACTIVE: HOT handle is bound to this fresh call context
STAGING: temporary replacement handle, not committed HOT and never exposed to recipes
```

READY makes no CPU-RAM/VRAM promise. HOT means a live libllama adapter object exists; physical placement is measured.

# 4. Health

```text
HEALTHY: lifecycle assumptions trustworthy
QUARANTINED: specific adapter blocked while shared runtime remains trustworthy
POISONED: affected runtime domain mechanically uncertain; no new learned calls
```

Bad model answers do not change runtime health.

POISONED cannot return to HEALTHY in the same runtime epoch. Recovery requires controlled teardown/restart, new epoch, base/runtime validation, and zero inherited handles/leases.

# 5. Atomic acquisition

Public learned-call manager API:

```text
ensure_hot_and_acquire(adapter_id, minimum_trust, protect_context=...) -> AdapterLease
release(lease) -> result
snapshot() -> state
```

Independent call-facing `ensure_hot()` + `acquire()` is forbidden.

# 6. Lease identity and linear release

```text
adapter_id
lease_uuid
process_epoch
handle_generation
live_handle token/reference
acquired_at
released state
```

First valid release mutates once. Double release, stale epoch, stale generation, identity mismatch are rejected and forensically logged.

# 7. Transactional pool-full replacement

Given committed HOT `{A,B,C,D,E}` and requested `F`:

```text
select legal victim E
verify swap headroom
load F -> STAGING while E remains HOT
validate F handle/runtime identity

if F fails:
  discard F staging
  committed HOT stays {A,B,C,D,E}

if F succeeds:
  commit E eviction
  promote F HOT
  atomically lease F before exposing it as unprotected demand
```

If failed STAGING cleanup is uncertain, route to health policy rather than pretending rollback succeeded.

`max_hot_adapters` is the steady committed ceiling. Hardware qualification must leave enough physical headroom for one STAGING adapter plus context/inference peak and safety reserve. If not, lower the steady ceiling.

# 8. Protection policy

## Hard protection

- `lease_count > 0`;
- active lifecycle/staging commit guard;
- hard `PINNED` policy.

Hard protection cannot be overridden by ordinary demand.

## Soft protection

- predicted next adapters from validated work graph;
- `HIGH_PRIORITY` preference;
- protect-set generation with expiry/replacement token.

Current demand may override stale/older soft protection when it needs a legal eviction candidate. Soft protection must not become immortal.

# 9. InferenceProfile

Each logical mode binds to an immutable profile covering at least:

```text
chat template identity
prompt serializer version
tokenizer identity/overrides
n_ctx / context budget policy / reserved output
sampler chain
temperature/top-k/top-p/min-p
repeat/frequency/presence penalties
grammar if any
seed policy
max output tokens
stop policy/sequences
qualification-sensitive backend settings
```

Canonical JSON + SHA-256 => `inference_profile_hash`.

Fresh sampler is created for every attempt. Qualification fixtures use deterministic seed policy; actual realized seed is recorded.

# 10. Activation receipt

Minimum host-only fields:

```text
call_uuid / attempt_uuid / turn_uuid
capability_id / specialist_mode_id
base_model_sha256
llama_cpp_build_id
runtime/manager/invoker versions
physical_adapter_id + adapter_sha256 or BASE_ONLY
AAE/input/output/validator versions
inference_profile_id/hash
prompt_render_hash
sampler_instance_uuid
seed_policy + actual_seed
process_epoch + handle_generation + lease_uuid
residency before/after
load/staging/eviction facts
fresh_context=true
fresh_sampler=true
apply status/scale
memory telemetry
timings
```

It is not a Recipe 4 `RECxxx` receipt.

# 11. Base-only mode

`BASE_ONLY_TEST_MODE` goes through the same Invoker path but applies no LoRA. It is qualification infrastructure and never silent fallback after expected adapter failure.

# 12. Runtime shutdown

```text
stop accepting new learned calls
mark/drain active acquisitions
complete or abort safely under journal/health rules
destroy contexts/samplers
release valid leases
free HOT adapters when certainty permits
free base
shutdown backend
```

If lifecycle certainty is lost during destructive operations, poison rather than guessing.

# 13. Default prototype policy

Initial config may request:

```text
max_hot_adapters = 5
standard_active_adapters = 1
standard_scale = 1.0
serialized_manager_mutation = true
```

But the real safe steady HOT ceiling is finalized only by target-hardware measurement with swap/inference headroom.
