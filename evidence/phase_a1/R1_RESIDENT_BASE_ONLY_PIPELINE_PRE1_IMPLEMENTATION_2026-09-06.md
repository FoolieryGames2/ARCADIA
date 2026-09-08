# A.R.C.A.D.I.A. — R0 -> R1 Resident BASE_ONLY Pipeline PRE-1 Implementation

Date: 2026-09-06
Standing: implementation checkpoint only; T0 BASE_ONLY qualification infrastructure; not adapter-qualified and not a registry freeze

## Scope implemented

This slice connects the already-implemented Recipe 1 Intent host controller to the real Recipe 0 handoff and the resident BASE_ONLY qualification boundary.

Implemented path:

```text
raw user prompt
  -> Recipe 0 Conversation Resolver
  -> frozen ConversationPacket
  -> Recipe 1 Spell
  -> host source-span allocation
  -> Recipe 1 Term / Meaning
  -> host term canonicalization
  -> Recipe 1 Prompt Analyst
  -> Recipe 1 Intent Organizer
  -> host requirement canonicalization
  -> frozen IntentArtifact
  -> optional non-authoritative Intent Comment
  -> STOP: R2 Context NOT_IMPLEMENTED
```

## Budget and runtime authority

- R0 and R1 share one `BudgetedBaseOnlyRecipeInvoker` instance.
- Every learned call advances the same immutable `WorkBudgetLedger` chain.
- Activation receipts are retained in exact call order and split into R0 and R1 views for trace output.
- The harness reserves capacity for the bounded R0 call ceiling plus four required R1 calls and the optional Intent Comment call.
- Runtime authority remains `T0 BASE_ONLY`; no adapter lease, tool authority, persistence completion, or publication authority is granted.

## R1 authority preserved

The integration keeps the existing host-owned R1 protections:

- model-local source references must resolve to host-created `Sxxx` spans;
- model-local term keys are replaced by host-created `Txxx` aliases;
- model-local requirement keys are replaced by host-created `Rxxx` aliases;
- Organizer capability candidates must exist in the host-supplied availability set;
- requirement dependencies must exist and remain acyclic;
- Organizer cannot mutate accepted Prompt Analyst control signals;
- optional Intent Comment is presentation-only and excluded from the machine Intent artifact hash.

The T0 lab currently defaults `capability_availability` to an empty authoritative set until a separate host capability-registry bridge is implemented. This does not grant the model permission to invent capabilities.

## Transcript boundary

The current user turn is still started as a real OPEN transcript turn for Recipe 0 lifecycle correctness. It is deliberately not completed or published in this slice because Recipe 8/publication authority does not exist yet. The qualification transcript remains isolated in `runtime-data/arcadia_recipe0_lab.sqlite3`.

## Bridge-test correction

The prior R0 resident bridge package contained a test-only constructor using an obsolete three-field `ActivationReceipt` shape. Live `main` uses the full activation receipt structure. This slice corrects that test fixture. The runtime bridge implementation itself did not depend on the obsolete constructor shape.

## Tests executed in the available reconstruction

Focused R0/R1/bridge controller and harness tests pass, including:

- five-mode R1 host orchestration;
- optional Intent Comment exclusion from machine authority;
- source-reference rejection;
- unknown capability rejection;
- dependency-cycle rejection;
- authoritative alias protection;
- shared R0 -> R1 model-call budget progression;
- R0 -> R1 stop at `R2 NOT_IMPLEMENTED`;
- actual `BaseOnlySpecialistInvoker` AAE/schema boundary exercised with a structured fake runtime.

The available sandbox is not the project's pinned Windows qualification environment. Ruff, strict MyPy, the real resident Qwen3 CUDA model, and the canonical `check.bat` gate must be run on the project workstation before any merge or runtime-qualification claim.

## Next boundary

After this slice is applied and workstation-qualified, the next implementation target is Recipe 2 Context. R2 must consume the frozen R1 `IntentArtifact`; this slice does not fabricate a Context result.
