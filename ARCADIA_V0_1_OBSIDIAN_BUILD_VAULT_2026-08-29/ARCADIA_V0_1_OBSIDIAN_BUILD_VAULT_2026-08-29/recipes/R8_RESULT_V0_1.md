---
title: "A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "recipe-contract"
source_path: "recipes/R8_RESULT_V0_1.md"
source_sha256: "df99133210a4089f113db25ee976f89005aa49a9cd76505577c4f9b4838012f8"
source_bytes: 36297
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/recipe"
  - "status/frozen"
aliases:
  - "R8_RESULT_V0_1.md"
  - "A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `recipe-contract`  
> **Frozen source:** `recipes/R8_RESULT_V0_1.md` · SHA-256 `df99133210a4089f…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT]] · [[03_ARCADIA_V0_1_GLOBAL_CONTRACTS_AND_INVARIANTS]] · [[04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION]] · [[R7_COMPLETION_V0_1]] · [[08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY]] · [[ARCADIA_V0_1_FULL_PIPELINE_AAE_REFERENCE_5_SLICES]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract

**v0.1 integration status:** The detailed semantic recipe body below is carried forward from the final pre-v0.1 trust/recovery specification because R3 intentionally did not change semantic recipe ownership. It is now governed by the v0.1 common runtime/AAE/source/recovery/trace/performance contracts in this bundle.

**Conflict rule:** if this carried-forward body contains older wording about adapter loading, generic adapter runtime, source-quality being unresolved, trace retention, crash replay, global sampling, handwritten AAE framing, or model-call necessity, the v0.1 system documents `01`–`09` supersede that wording. Semantic recipe responsibilities, artifacts, edge cases, and tests remain authoritative unless explicitly superseded.

---

# A.R.C.A.D.I.A. — RESULT RECIPE
## Prototype Build Specification — Conversational Articulation and Final Publication

**Project:** A.R.C.A.D.I.A. — Adaptive Runtime for Compartmentalized Agents, Decisions, Interaction & Automation  
**Recipe:** 8 — Result  
**Date:** 2026-08-28  
**Status:** LOCKED PROTOTYPE BUILD DESIGN  
**Parent:** `ARCADIA_COMPLETION_RECIPE_PROTOTYPE_BUILD_SPEC_2026-08-28.md`  
**Upstream:** immutable Final Standing Packet `FSPxxx` from Recipe 7 Completion  
**Final stage:** user-facing publication  
**Purpose:** Define exactly how A.R.C.A.D.I.A. turns immutable Completion truth into a natural response using the existing Conversational Howard adapter, host-built disclosure and literal constraints, per-requirement conversational comments, deterministic linguistic validation, final composition, and publication without allowing the conversational layer to change requirement standing or invent new reality.

---

> **CONFIRMED LOGIC INTEGRATION — R2 — 2026-08-28**  
> This R2 document integrates the confirmed trust/recovery logic locked after the AAE five-slice review: single-source AAE/runtime/training contracts, base-model baselining, full trace capture with a training-data firewall, packet-projection testing, aggregate loop telemetry, durable-provisional semantic Persistence with next-turn review, controlled user memory correction, deterministic-first semantic support, and mode-specific Howard evaluation.  
> **Source-quality / source-authority ranking is intentionally NOT defined by this update. It remains a separate required design lane.**


# 0. CORE RULE

Result answers:

> **How should the already-decided final standing be communicated to the user clearly, naturally, completely, and without changing reality?**

Result is articulation.

It is not final truth judgment.

The frozen rule:

> **Completion organizes the truth. Conversational Howard articulates it.**

---

# 1. POSITION IN THE FULL SPINE

```text
RECIPE 7 COMPLETION
       |
       v
IMMUTABLE FSPxxx
       |
       v
RECIPE 8 RESULT
       |
       +--> host Result preparation
       |
       +--> Howard per-requirement comments
       |
       +--> host/module validation
       |
       +--> Howard final composition
       |
       +--> host final validation
       |
       +--> publication
       v
USER
```

No later semantic recipe exists after Result.

---

# 2. ADAPTER COUNT — LOCKED

Result adds **zero new specialist adapters**.

It reuses the existing:

```text
CONVERSATIONAL HOWARD
```

Howard is called multiple times with fresh KV:

```text
Howard(R001 final standing)
Howard(R002 final standing)
Howard(R003 final standing)
...
CLEAR KV
Howard(validated comments + final standing summary)
```

Multiple calls do not create multiple adapter contracts.

The complete Completion + Result final stretch therefore adds:

```text
2 new adapters total:
  Completion Assessor
  Completion Composer

1 reused adapter:
  Conversational Howard
```

All spaCy, regex, RapidFuzz, NetworkX, SQLite, hash, schema, literal-lock, and coverage checks are host modules and add zero adapters.

---

# 3. RESULT AUTHORITY MODEL

| Component | Owns | Must not own |
|---|---|---|
| Completion/FSP | final Rxxx standing | conversational prose |
| Result Host | disclosure, exact literal protection, validation, publication mechanics | terminal semantic rejudgment |
| Conversational Howard comment pass | natural per-requirement explanation | status mutation, new facts |
| Conversational Howard final pass | coherent final response | new truth, tools, persistence, status mutation |
| Publication Host | exact response delivery/transcript finalization | semantic Completion status |

---

# 4. RESULT RECEIVES FROZEN STANDING

Minimum input:

```text
FSP artifact UUID/hash
turn UUID
raw user prompt
resolved request presentation
requirement standings[]
overall turn posture
user-facing fact refs
user-facing blocker refs
user-facing failure refs
result guidance
disclosure seed
protected literal seed
```

Result does not need the entire raw turn ledger.

If an exact user-facing detail is needed, the host retrieves the referenced bounded projection.

---

# 5. RESULT MUST NOT RE-READ THE WORLD

Conversational Howard may not:

```text
query SQLite directly
load old conversation history
browse
call tools
reconcile evidence
inspect raw provider payloads unless explicitly projected
write Persistence
change Rxxx
change FSP
```

All needed truth is already in the Result packet.

If the packet is structurally incomplete, Result fails validation and does not improvise.

---

# 6. RESULT HOST PREPARATION

Before Howard comments, the host derives:

```text
disclosure_map
protected_literals
forbidden_internal_literals/patterns
requirement_comment_packets[]
overall_response_budget
tone/presentation constraints
```

These are deterministic or policy-derived.

---

# 7. DISCLOSURE MAP — LOCKED

Classes:

```text
MUST_MENTION
MAY_MENTION
DO_NOT_EXPOSE
```

Examples:

## MUST_MENTION

```text
requested factual answer
material incomplete portion
blocker
required operation failure
required Persistence failure
user action needed
material uncertainty/conflict
```

## MAY_MENTION

```text
secondary useful detail
optional context
successful housekeeping
nonessential provenance summary
```

## DO_NOT_EXPOSE by default

```text
internal R/W/REC/EF/PRC IDs
adapter names
repair counters
hashes
schema validation messages
SQLite details
internal policy codes
internal graph diagnostics
```

Howard may describe an outcome without exposing its internal machinery.

---

# 8. PER-REQUIREMENT RESULT COMMENT PACKET

For each relevant `Rxxx`, host builds a small packet:

```text
result_comment_packet
  requirement_id
  user_facing_request
  terminal_status

  established_user_facing_facts[]
  unmet_user_facing_components[]
  blockers[]
  failure_messages[]
  persistence_user_facing_effect[]

  must_mention[]
  may_mention[]
  must_not_claim[]
  protected_literals[]

  target_comment_length
  packet_hash
```

Howard sees this, not the giant trace.

## 8.1 References never substitute for required semantic content

If Howard must interpret or verbalize a fact, gap, blocker, failure, persistence effect, or other referenced item, the packet must carry both:

```text
authoritative reference
+ bounded authorized user-facing content
```

A bare `UFxxx`, `BLKxxx`, `FAILxxx`, `GAPxxx`, or other opaque identifier is sufficient only for linkage/echo when the item's meaning is not needed. Result packet construction must never expect Howard to infer content from an ID.

This is an AAE/runtime packet-builder invariant and must be tested as part of projection recall.

---

# 9. WHICH REQUIREMENTS GET COMMENTS

Default:

```text
every Rxxx with user-facing content
every PARTIALLY_SATISFIED Rxxx
every BLOCKED Rxxx
every FAILED Rxxx
```

A trivial internalized requirement that produces no distinct user-facing content may be merged with another comment by host policy, but its standing remains present in FSP.

The host must never hide a blocker/failure merely to shorten the response.

---

# 10. HOWARD COMMENT PASS — CORE QUESTION

> **Given this requirement’s frozen standing and only these authorized user-facing facts/limits, how should Howard explain this one outcome naturally without changing its meaning?**

Howard comment is commentary.

It is not authority.

---

# 11. COMMENT OUTPUT CONTRACT

Recommended structured wrapper:

```text
result_comment
  comment_uuid
  requirement_id
  standing_echo
  text
  mentions_fact_ids[]
  mentions_blocker_ids[]
  mentions_failure_ids[]
```

`standing_echo` must exactly equal FSP standing.

Howard does not output a new status choice.

---

# 12. COMMENT HOST VALIDATION

Host validates:

```text
schema
requirement ID exact
standing echo exact
all fact/blocker/failure IDs allowed
MUST_MENTION coverage appropriate to packet
no must_not_claim violation
protected literals preserved when used
no unsupported number/date/path/version
no internal identifier leak
no tool/persistence action claim not in packet
no statement that contradicts terminal standing
bounded length
```

Invalid comments enter bounded Howard repair.

---

# 13. COMMENT REPAIR

Prototype default:

```text
max_result_comment_repairs = 2
```

Repair input:

```text
same frozen comment packet
previous comment
exact validation violations
```

Howard may rewrite wording only.

FSP never changes.

If repair exhausts:

```text
RESULT_COMMENT_REPAIR_EXHAUSTED
```

The host may fall back to a deterministic minimal template generated solely from authorized user-facing fields.

This fallback does not invent new facts.

---

# 14. WHY A DETERMINISTIC COMMENT FALLBACK IS ALLOWED

Result is presentation, not semantic judgment.

If Howard fails formatting/literal checks repeatedly, the host already has authoritative user-facing data.

A safe fallback can say:

```text
"X was completed."
"Y is blocked because Z is required."
```

using exact validated fields.

This is safer than publishing a hallucinated conversational sentence.

---

# 15. spaCy ROLE — SURFACE INSPECTION ONLY

spaCy is strongly useful after Howard writes.

Use for:

```text
sentence segmentation
named entities
noun chunks
surface pronouns
basic token/part-of-speech structure
```

Do not use spaCy to decide truth.

It helps answer:

```text
What did Howard actually say?
What names/numbers/entities appeared?
How many sentences were generated?
Did the answer appear to introduce a new named entity?
```

Semantic authority stays in FSP.

---

# 16. REGEX ROLE — HARD LITERAL EXTRACTION

Use regex for exact patterns such as:

```text
integers/decimals
percentages
currency
dates
times
version strings
URLs
filesystem paths
file extensions
hashes
Rxxx/Wxxx/RECxxx/EFxxx/PRCxxx/internal IDs
email-like strings where relevant
```

Compare extracted literals against authorized Result packet literals.

---

# 17. RAPIDFUZZ ROLE — PROPER-NAME CORRUPTION SIGNAL

RapidFuzz may detect high-similarity mutations of awkward protected strings.

Example authorized:

```text
Qwen2.5-Coder-3B-Instruct
```

Howard emits:

```text
Qwen 2.5 Coder 3B
```

Policy distinguishes:

```text
EXACT_REQUIRED
DISPLAY_FLEXIBLE
```

For `EXACT_REQUIRED`, exact mismatch fails.

For `DISPLAY_FLEXIBLE`, RapidFuzz is only a warning/signal.

Fuzzy similarity never establishes new truth.

---

# 18. LITERAL LOCK MODULE

Before comments/final composition, host builds a Literal Lock.

Protected categories:

```text
names
version numbers
dates
times
quantities
units
money
filenames
paths
URLs
project names
model names
user-facing codes
hashes when explicitly requested
```

Each literal record:

```text
literal_id
canonical_text
policy:
  EXACT_REQUIRED
  DISPLAY_FLEXIBLE
source_ref
allowed_variants[]
```

No model owns the canonical literal.

---

# 19. INTERNAL-ID LEAK CHECKER

Default internal patterns prohibited from normal final response:

```text
R\d+
W\d+
TRQ\d+
REC\d+
EF\d+
DN\d+
RRQ\d+
PA\d+
PP\d+
PRC\d+
CA\d+
CP\d+
FSP\d+
```

Allow only when the user explicitly asks about internal architecture or IDs.

Host policy supplies exceptions.

---

# 20. RESPONSE COVERAGE MODULE

Using the validated comments and disclosure map, host computes:

```text
must_mention_items
covered_items
missing_items
```

Do not rely on Howard to remember every blocker.

A final response cannot publish while a required disclosure is missing.

---

# 21. RESPONSE BUDGET MODULE

Host derives an approximate response budget from:

```text
number of user-facing requirements
number of MUST_MENTION items
presence of partial/block/failure
number of distinct facts
user requested format/length if any
```

Conceptual result:

```text
response_budget
  target_tokens
  hard_max_tokens
  presentation_mode
```

Examples:

```text
1 simple satisfied Rxxx
  -> concise

several independent findings
  -> moderate structured response

partial/block/failure
  -> enough room to explain limitation clearly
```

Do not use another adapter merely to choose verbosity.

---

# 22. VALIDATED COMMENT SET

After all per-requirement comments pass:

```text
validated_result_comments[]
```

Each carries:

```text
comment UUID/hash
Rxxx
standing
authorized fact coverage
protected-literal validation
```

Only validated comments reach final Howard composition.

---


# R2. HOWARD MODE-SPECIFIC TRUST AND BOUNDED FAN-OUT/FAN-IN — LOCKED

The same Conversational Howard adapter may serve multiple presentation modes only through distinct AAE Specialist Awareness contracts and separate mode-level evaluation.

Result already uses the preferred structure:

```text
one bounded requirement -> one Result Comment call
...
validated comment set -> final Result composition call
```

Do not replace this with one token-heavy monolithic call that comments on many requirements and composes the final response simultaneously.

If the validated comment set itself exceeds the configured final-composition budget, the host may perform bounded Howard fan-in stages:

```text
validated comments
  -> bounded group composition fragments
  -> host validation
  -> final Howard composition
```

Every stage uses fresh KV and remains presentation-only. No fragment may add facts, change standing, hide required disclosures, or become semantic authority.

Trust/metrics are tracked per Howard mode even when the adapter hash is identical.

---

# 23. CLEAR KV BEFORE FINAL COMPOSITION

Mandatory:

```text
all per-Rxxx comment calls complete
       |
       v
CLEAR KV / ATTENTION
       |
       v
FINAL HOWARD COMPOSITION
```

Final Howard must reconstruct only from explicit Result artifacts.

Do not rely on hidden state from comment passes.

---

# 24. FINAL HOWARD COMPOSER INPUT

Recommended bounded packet:

```text
raw user prompt
resolved user request presentation
overall turn posture
FSP requirement standing summaries
validated_result_comments[]
disclosure map
protected literal lock
response budget
tone/style policy
publication constraints
```

No raw Execution dump.

No SQL state.

No raw web pages unless the user-facing projected quotation/content itself is explicitly authorized.

---

# 25. FINAL HOWARD CORE QUESTION

> **Using only the validated final standing and validated comments, write the user-facing response that best communicates what was accomplished, what remains incomplete or blocked, and any required next information—without changing any fact, status, protected literal, or outcome.**

---

# 26. FINAL HOWARD OUTPUT

Baseline output:

```text
final_response_text
```

Host wraps it as:

```text
result_artifact
  artifact_uuid
  short_id: RST001
  turn_uuid
  FSP_ref
  validated_comment_refs[]
  response_text
  response_hash
  validation_summary
```

---

# 27. FINAL RESPONSE VALIDATION — MULTI-LAYER

Run in this order:

```text
1. UTF-8 / size / basic safety gate
2. forbidden internal-ID pattern scan
3. regex literal extraction
4. Literal Lock validation
5. spaCy surface entity/sentence inspection
6. RapidFuzz protected-name signal
7. MUST_MENTION coverage
8. must_not_claim checks
9. terminal-standing language consistency
10. response budget
11. hash/final artifact creation
```

No single module decides semantic truth.

The modules jointly guard presentation fidelity.

---

# 28. STANDING LANGUAGE CONSISTENCY

Result Host rejects obvious contradictions.

Examples:

FSP:

```text
R002 = FAILED
```

Howard:

```text
"I saved that successfully."
```

Reject.

FSP:

```text
R003 = BLOCKED
```

Howard:

```text
"Everything is done."
```

Reject.

FSP:

```text
R001 = PARTIALLY_SATISFIED
```

Howard:

```text
"I couldn't get anything."
```

when fulfilled components exist.

Reject or repair depending on exact packet.

This validator uses bounded explicit standing/fact language mappings and model-generated claims only as surface text.

It does not rejudge Completion.

---

# 29. FINAL HOWARD REPAIR

Prototype default:

```text
max_final_result_repairs = 2
```

Repair packet:

```text
same frozen final-composition input
previous response text
exact deterministic validation failures
```

Example:

```text
- Required blocker B2 was omitted.
- Protected version literal "4.2" changed to "4.3".
- Response claims save success but R002 is FAILED.
```

Howard may rewrite prose.

He cannot change FSP.

---

# 30. FINAL FALLBACK

If final Howard repair exhausts:

```text
RESULT_FINAL_REPAIR_EXHAUSTED
```

Host generates a minimal deterministic response from:

```text
MUST_MENTION items
user-facing facts
blockers
failures
required next action
```

The fallback is less conversational but remains accurate.

No user-facing response should be withheld merely because style generation failed when a safe exact result can be rendered.

---

# 31. OPTIONAL SPELLING/GRAMMAR POLISH LANE — NOT BASELINE

An existing bounded spelling/grammar specialist may optionally run after final Howard.

It is **disabled by default in the baseline Result recipe** so the final stretch adds no new adapter.

If enabled later:

```text
Howard final
  -> freeze protected spans
  -> spelling/grammar specialist
  -> restore/verify protected spans
  -> rerun full Result validation
```

It may not alter:

```text
names
numbers
dates
versions
URLs
paths
quotes
technical identifiers
```

Any protected-literal change rejects the polish output and uses the pre-polish response.

---


# R2A. PROVISIONAL MEMORY LANGUAGE GUARD

Result may truthfully report that a requested memory update was saved when the immutable Persistence receipt proves `SUCCESS`, including `SUCCESS + PROVISIONAL`.

Result must not say or imply:

```text
"you confirmed this"
"this was explicitly confirmed"
```

when the only later standing is `STABILIZED_NO_IMMEDIATE_CORRECTION`.

Provisional/stabilized internal terminology is normally `DO_NOT_EXPOSE` unless needed to explain a correction, undo, debugging state, or user-requested memory status.

---

# 32. RESULT ARTIFACT NAMESPACES

Recommended turn-scoped aliases:

```text
RCM001   Result Comment
RST001   validated Result artifact
PUB001   host Publication Receipt
```

All also receive authoritative UUID-backed artifact identity.

---

# 33. PUBLICATION IS HOST-OWNED

Howard does not mark his own response as delivered.

Publication Host receives validated `RSTxxx`.

Conceptual sequence:

```text
RST001 VALIDATED
      |
      v
send exact response_text to active conversation transport/UI
      |
      v
transport acknowledges publication
      |
      v
write exact published text to conversation_turns.final_response
write final_response_hash
set turn status = COMPLETED
increment transcript_commit_seq
create PUB001
```

If transport fails:

```text
do not claim user received it
do not set transcript turn COMPLETED
record publication failure
```

Completion FSP remains unchanged.

---

# 34. PUBLICATION RECEIPT — PUBxxx

Recommended fields:

```text
publication_receipt_uuid
short_id: PUB001
turn_uuid
result_artifact_uuid
response_hash
transport_id
publication_status
published_at
transcript_commit_seq_before
transcript_commit_seq_after
verification
```

Statuses:

```text
PUBLISHED
DELIVERY_FAILED
TRANSCRIPT_COMMIT_FAILED
```

The prototype may adapt transport-specific details, but the authority split remains.

---

# 35. EXACT TRANSCRIPT RULE

The transcript stores:

```text
exact raw user message
exact final response actually published
```

Do not store:

```text
Howard comment drafts
failed response drafts
repair drafts
unpublished fallback drafts
```

Those belong in technical ledger/debug trace, not ordinary transcript history.

---

# 36. RESULT TECHNICAL LEDGER

Technical ledger retains:

```text
Result comment packets
raw Howard comment outputs
comment validation reports
comment repairs
validated RCM artifacts
final composition packet
raw final Howard drafts
final validation reports
final repairs
RST artifact
PUB receipt
timings/token metrics
model/adapter identities
hashes
```

Recipe 0 later sees only the completed transcript exchange, not this internal machinery.

---

# 37. PUBLICATION TRANSACTION CONSISTENCY

If transcript and technical ledger share SQLite:

Prefer one bounded transaction for:

```text
append final RST artifact
append PUB publication artifact basis where transport allows
update conversation_turns exact final response/status
increment transcript_commit_seq
```

When transport acknowledgment must happen outside SQLite:

```text
validate RST
send exact RST text
receive transport success
begin DB transaction
store exact published text + receipt
commit
```

If DB commit fails after transport success, record explicit reconciliation/operational error for system diagnostics.

Do not rewrite Completion standing.

---

# 38. RESULT FAILURE CLASSES

Initial vocabulary:

```text
INVALID_FSP
FSP_HASH_MISMATCH
UNKNOWN_REQUIREMENT_REFERENCE
INVALID_RESULT_COMMENT_PACKET
RESULT_COMMENT_STANDING_MUTATION
RESULT_COMMENT_UNSUPPORTED_FACT
RESULT_COMMENT_MISSING_REQUIRED_DISCLOSURE
RESULT_COMMENT_LITERAL_MISMATCH
RESULT_COMMENT_INTERNAL_ID_LEAK
RESULT_COMMENT_REPAIR_EXHAUSTED
INVALID_FINAL_RESULT_INPUT
RESULT_MISSING_REQUIRED_DISCLOSURE
RESULT_LITERAL_MISMATCH
RESULT_UNSUPPORTED_LITERAL
RESULT_INTERNAL_ID_LEAK
RESULT_STANDING_CONTRADICTION
RESULT_OVER_BUDGET
RESULT_FINAL_REPAIR_EXHAUSTED
PUBLICATION_DELIVERY_FAILED
PUBLICATION_TRANSCRIPT_COMMIT_FAILED
PUBLICATION_HASH_MISMATCH
```

---

# 39. RESULT MODULE STACK

Recommended core:

```text
json
jsonschema
dataclasses or pydantic
hashlib
uuid
re
typing
collections
```

Strongly useful:

```text
spaCy
RapidFuzz
```

Optional:

```text
regex
ftfy
```

NetworkX normally belongs in Completion, not Result.

SQLite is used by the Result Host for technical artifact/transcript publication, not semantic judgment.

---

# 40. COMMENT EXAMPLE — SATISFIED

FSP:

```text
R001 = SATISFIED
UF001 = "Version 4.2 is current."
```

Howard comment:

```text
"The current version is 4.2."
```

Host validates exact literal and fact coverage.

---

# 41. COMMENT EXAMPLE — REQUIRED PERSISTENCE FAILED

FSP:

```text
R001 = SATISFIED
  current version = 4.2

R002 = FAILED
  required save did not commit
```

Howard comments:

```text
R001:
"I found the current version: 4.2."

R002:
"I wasn't able to save that into durable memory."
```

Final Howard may combine:

```text
"I found the current version—4.2—but the memory save didn't complete."
```

He may not say:

```text
"Done, I saved 4.2."
```

---

# 42. COMMENT EXAMPLE — BLOCKED

FSP:

```text
R003 = BLOCKED
blocker = destination path required
```

Howard:

```text
"I still need the destination path before I can save the file."
```

Natural language is allowed.

Changing the blocker is not.

---

# 43. COMMENT EXAMPLE — PARTIAL

FSP:

```text
R001 = PARTIALLY_SATISFIED

fulfilled:
  release date
  platforms

unmet:
  price
```

Howard:

```text
"I found the release date and supported platforms, but I couldn't establish the price."
```

This is exactly the kind of final articulation the Result recipe is for.

---

# 44. FINAL COMPOSITION EXAMPLE

Validated comments:

```text
C1: current version is 4.2
C2: durable save failed
C3: no other user action required
```

Final packet:

```text
raw prompt
FSP
validated comments
MUST_MENTION = version + failed save
protected = "4.2"
budget = concise
```

Howard:

```text
"The current version is 4.2. I found it successfully, but the durable memory save failed, so I haven't stored it as persistent knowledge."
```

Host validates and publishes exact text.

---


# R2. TRUST, BASELINE, TRACE, AND CONTRACT-DRIFT LOCK

The prototype does not treat a structurally valid adapter output as earned semantic trust.

## R2.1 Trust qualification ladder

```text
T0  untrained / architecture-only
T1  fixture tests pass
T2  held-out semantic tests pass
T3  adversarial + composition tests pass
T4  shadow runtime; outputs logged but not authoritative
T5  limited authority under host gates
T6  production-authorized for this exact runtime identity
```

Trust attaches to the complete runtime identity, not merely an adapter name:

```text
base_model_hash
+ adapter_hash
+ AAE_contract_version
+ specialist_mode_contract_version
+ input_schema_version
+ output_schema_version
+ host_validation_version
```

Changing any component creates a new qualification target.

## R2.2 Base GGUF baseline is mandatory

Before adapter training is credited, run the exact frozen evaluation suite against:

```text
BASE GGUF
+ final AAE contract
+ real host packet builder
+ real validators
```

Record at minimum:

```text
schema accuracy
first-pass semantic accuracy
repair frequency
repaired semantic accuracy
hallucinated/unknown refs
uncertainty-state accuracy
latency
token counts
```

Then run the trained adapter against the **same held-out suite**. Adapter quality is measured as a delta from the frozen base baseline, not by impression.

## R2.3 Training/runtime single-source invariant

Training envelopes and runtime envelopes must be generated from the same machine-readable contract registry.

Do not maintain one prompt definition for training and a second manually copied definition for runtime.

The registry owns, at minimum:

```text
Global Awareness
Specialist Awareness
legal input artifact classes
input schema
output schema
legal enums
uncertainty behavior
repair shape
next consumer
contract version
```

## R2.4 Full trace and training-data firewall

Every model boundary preserves:

```text
exact AAE version
exact bounded packet
raw model output
parsed output
host validation result
repair packet/output when present
accepted artifact hash
adapter/base identities
latency/tokens
next-turn user correction/control signal when relevant
```

Runtime traces **do not automatically become training data**.

Required promotion path:

```text
RAW TRACE
  -> candidate extraction
  -> validation/review
  -> TRAINING_APPROVED
```

Held-out evaluation cases are separately tagged and must never enter training.

## R2.5 First-pass and repaired performance are separate metrics

Track independently:

```text
first_pass_structurally_valid
first_pass_semantically_correct
repaired_structurally_valid
repaired_semantically_correct
repair_exhausted
```

Repair is resilience. It must not camouflage weak first-pass behavior.


# R2B. HOWARD MODE TESTING

Evaluate separately:

```text
Intent comment mode
Context lane-comment mode
Context final-synthesis mode
Result per-requirement comment mode
Result final-composition mode
```

A pass in one mode does not automatically qualify another mode.

---

# 45. RESULT ACCEPTANCE TESTS — COMMENTS

1. Satisfied fact comment.
2. Partial comment includes fulfilled + missing.
3. Blocked comment names actual blocker.
4. Failed comment does not imply success.
5. Required Persistence failure preserved.
6. Advisory Persistence failure omitted when irrelevant.
7. Exact version preserved.
8. Exact filename preserved.
9. Exact path preserved.
10. Internal R/REC/EF/PRC ID not leaked.
11. Comment attempts status change -> reject.
12. Comment invents number -> reject.
13. Comment omits mandatory blocker -> repair.
14. Comment over target length -> repair or trim under safe policy.
15. Comment repair exhaustion -> deterministic fallback.

---

# 46. RESULT ACCEPTANCE TESTS — FINAL COMPOSITION

1. One satisfied requirement -> concise response.
2. Several satisfied requirements -> coherent response.
3. Mixed satisfied/failed -> both clearly communicated.
4. Partial result -> no “all done” language.
5. Blocked result -> required next information surfaced.
6. Shared fact not needlessly repeated.
7. MUST_MENTION coverage exact.
8. MAY_MENTION omission allowed.
9. DO_NOT_EXPOSE internals absent.
10. Protected literals survive.
11. Final Howard cannot change FSP standing.
12. Final Howard cannot claim a failed save succeeded.
13. Final repair fixes missing disclosure.
14. Repair exhaustion -> safe deterministic final.
15. Response hash reproducible.

---

# 47. PUBLICATION ACCEPTANCE TESTS

1. Exact RST text delivered.
2. Successful transport writes exact same text to transcript.
3. Hash of transcript text matches RST hash.
4. `transcript_commit_seq` increments exactly once.
5. Turn status becomes `COMPLETED` only after successful publication path.
6. Failed delivery does not mark turn completed.
7. Failed delivery does not rewrite FSP.
8. Failed DB transcript commit after transport is explicitly logged.
9. Recipe 0 retrieves exact published response next turn.
10. Failed Howard drafts never enter normal transcript.

---

# 48. ADVERSARIAL RESULT TESTS

1. Howard changes 4.2 -> 4.3.
2. Howard changes user name spelling.
3. Howard fabricates URL.
4. Howard fabricates path.
5. Howard says “saved” with failed PRC.
6. Howard says “done” when any MUST_MENTION blocker exists.
7. Howard hides failed requirement.
8. Howard exposes internal receipt IDs.
9. Howard invents a new requirement.
10. Howard asks to run another search.
11. Howard states unsupported confidence.
12. Howard comments on facts absent from packet.
13. Howard drops a required safety/policy limitation.
14. Howard violates exact quote/literal rule.
15. Howard final composer mutates comment meaning.
16. Optional grammar pass mutates protected literal.
17. Transport changes response bytes/text.
18. Transcript stores a different response than published.
19. Publication receipt hashes mismatch.
20. Recipe 0 sees unpublished draft.

---

# 49. TRAINING TARGET — CONVERSATIONAL HOWARD COMMENT PASS

Reuse Howard but train/evaluate the role with packets containing:

```text
frozen standing
bounded facts
bounded blockers
bounded failures
must-not-claim list
target length
```

Desirable behavior:

```text
natural
direct
truth-preserving
status-faithful
does not expose internal machinery
does not over-explain simple outcomes
does not hide partial/failure/blocker
```

---

# 50. TRAINING TARGET — CONVERSATIONAL HOWARD FINAL PASS

Train/evaluate on:

```text
validated per-requirement comments
overall posture
response budget
disclosure map
protected literals
raw user prompt
```

Target:

```text
one coherent response
minimal repetition
appropriate ordering
all mandatory disclosures
natural conversational voice
no semantic mutation
```

---

# 51. RESULT POLICY SNAPSHOT

Host-owned policy:

```text
result_policy_snapshot_uuid
policy_version
internal_id_disclosure_rules
literal_lock_rules
must_mention_rules
response_budget_rules
comment_repair_limit
final_repair_limit
fallback_template_version
publication_policy
policy_hash
```

Howard cannot change this policy.

---

# 52. RESULT SOURCE LAYOUT

```text
result/
  __init__.py
  models.py
  schemas.py
  policy.py
  prepare.py
  disclosure.py
  literal_lock.py
  literal_extract.py
  spacy_signals.py
  fuzzy_names.py
  internal_id_guard.py
  coverage.py
  response_budget.py
  fan_in.py
  comment_runner.py
  comment_validation.py
  final_runner.py
  final_validation.py
  fallback.py
  publication.py
  receipt.py
  trace.py

prompts/
  conversational_howard_result_comment.txt
  conversational_howard_final_result.txt

schemas/
  result_comment_packet.schema.json
  result_comment.schema.json
  result_final_input.schema.json
  result_artifact.schema.json
  publication_receipt.schema.json

tests/
  test_disclosure.py
  test_literal_lock.py
  test_internal_id_guard.py
  test_result_comment_validation.py
  test_result_fan_in.py
  test_result_final_validation.py
  test_publication.py
  test_result_e2e.py
```

---

# 53. RESULT INVARIANTS — LOCKED

```text
RES01. Result adds no new specialist adapter.

RES02. Conversational Howard is reused.

RES03. Howard comments only after Completion freezes FSP.

RES04. Per-Rxxx comments are bounded.

RES05. Howard comments may explain but never alter terminal standing.

RES06. Host validates every comment.

RES07. Clear KV before final Howard composition.

RES08. Final Howard receives validated comments, not raw giant trace.

RES09. Completion/FSP remains semantic authority.

RES10. Result calls no tools.

RES11. Result writes no semantic memory.

RES12. Result creates no new requirements.

RES13. spaCy is surface inspection, not truth authority.

RES14. regex protects exact literals/patterns.

RES15. RapidFuzz is a corruption signal, not identity authority.

RES16. Literal Lock protects user-facing exact values.

RES17. MUST_MENTION items cannot silently disappear.

RES18. DO_NOT_EXPOSE internals stay hidden by default.

RES19. Internal IDs are blocked unless explicitly authorized.

RES20. Optional grammar polish is disabled in baseline and cannot change protected spans.

RES21. Final response is validated before publication.

RES22. Repair changes prose only, never FSP.

RES23. Safe deterministic fallback exists.

RES24. Publication is host-owned.

RES25. Transcript stores exact published response only.

RES26. Failed drafts remain technical ledger only.

RES27. Turn becomes COMPLETED only through successful publication/transcript path.

RES28. Publication failure does not rewrite Completion standing.

RES29. Every Result artifact has UUID/hash provenance.

RES30. Final user-facing response is the last semantic articulation step.
```

---

# 54. FINAL RESULT FLOW — LOCKED

```text
FSPxxx
   |
   v
RESULT HOST PREPARATION
   |
   +--> disclosure map
   +--> Literal Lock
   +--> internal-ID guard policy
   +--> response budget
   +--> per-Rxxx comment packets
   |
   v
FOR EACH USER-FACING Rxxx
   |
   v
CONVERSATIONAL HOWARD COMMENT
   |
   v
spaCy / regex / RapidFuzz / literal / coverage validation
   |
   +--> invalid -> bounded Howard wording repair
   |
   v
validated RCMxxx
   |
   v
CLEAR KV
   |
   v
CONVERSATIONAL HOWARD FINAL COMPOSER
   |
   v
FINAL MODULE VALIDATION
   |
   +--> invalid -> bounded final Howard repair
   |
   +--> repair exhausted -> deterministic safe fallback
   |
   v
RSTxxx VALIDATED
   |
   v
PUBLICATION HOST
   |
   v
SEND EXACT RESPONSE
   |
   +--> failed -> publication failure; transcript not completed
   |
   v
ACKNOWLEDGED
   |
   v
STORE EXACT PUBLISHED RESPONSE
HASH VERIFY
INCREMENT transcript_commit_seq
TURN status = COMPLETED
   |
   v
PUBxxx
   |
   v
USER
```

---

# 55. LAST RESULT — WHAT THE USER ACTUALLY RECEIVES

The final user receives only:

```text
exact validated final response text
```

They do not receive the internal Completion packet unless they ask for it.

They do not receive:

```text
CAxxx
CPxxx
FSPxxx
RCMxxx
RSTxxx
PUBxxx
raw receipts
hashes
SQL
validation traces
repair attempts
```

unless the product explicitly exposes those artifacts.

The visible response is natural conversational Howard speaking from already-frozen truth.

---

# 56. FINAL DESIGN SUMMARY

```text
RESULT QUESTION
  How do we communicate frozen Completion truth?

NEW ADAPTERS
  0

REUSED
  Conversational Howard

PASS 1
  one Howard comment per relevant final Rxxx

HOST
  validates comments with:
    schema
    disclosure map
    spaCy
    regex
    RapidFuzz
    Literal Lock
    internal-ID guard
    coverage

PASS 2
  fresh-KV Howard final composition

HOST
  validates again

FAILSAFE
  deterministic minimal response

PUBLICATION
  host sends exact validated text
  exact published response enters transcript
  transcript commit seq advances
  PUB receipt proves publication path

USER
  receives only the final validated conversational response
```

**END OF A.R.C.A.D.I.A. RESULT RECIPE PROTOTYPE BUILD SPECIFICATION — 2026-08-28**
