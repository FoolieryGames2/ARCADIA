---
title: "A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "recipe-contract"
source_path: "recipes/R1_INTENT_V0_1.md"
source_sha256: "82356e106fb1f27a8a26fce185238e3f602b227b369f860b4aec90c1b2833f1c"
source_bytes: 27274
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/recipe"
  - "status/frozen"
aliases:
  - "R1_INTENT_V0_1.md"
  - "A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `recipe-contract`  
> **Frozen source:** `recipes/R1_INTENT_V0_1.md` · SHA-256 `82356e106fb1f27a…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT]] · [[03_ARCADIA_V0_1_GLOBAL_CONTRACTS_AND_INVARIANTS]] · [[04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION]] · [[R0_CONVERSATION_RESOLVER_V0_1]] · [[R2_CONTEXT_V0_1]] · [[ARCADIA_V0_1_FULL_PIPELINE_AAE_REFERENCE_5_SLICES]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract

**v0.1 integration status:** The detailed semantic recipe body below is carried forward from the final pre-v0.1 trust/recovery specification because R3 intentionally did not change semantic recipe ownership. It is now governed by the v0.1 common runtime/AAE/source/recovery/trace/performance contracts in this bundle.

**Conflict rule:** if this carried-forward body contains older wording about adapter loading, generic adapter runtime, source-quality being unresolved, trace retention, crash replay, global sampling, handwritten AAE framing, or model-call necessity, the v0.1 system documents `01`–`09` supersede that wording. Semantic recipe responsibilities, artifacts, edge cases, and tests remain authoritative unless explicitly superseded.

---

# HOWARD INTENT RECIPE
## Prototype Build Specification — Command-Window Reference
**Status:** LOCKED PROTOTYPE DESIGN  
**Scope:** INTENT ONLY  
**Date:** 2026-08-28  
**Purpose:** Archive-ready build reference for implementing and later independently testing Howard's Intent recipe slices before combining them into the larger multi-recipe matrix.

---

> **CONFIRMED LOGIC INTEGRATION — R2 — 2026-08-28**  
> This R2 document integrates the confirmed trust/recovery logic locked after the AAE five-slice review: single-source AAE/runtime/training contracts, base-model baselining, full trace capture with a training-data firewall, packet-projection testing, aggregate loop telemetry, durable-provisional semantic Persistence with next-turn review, controlled user memory correction, deterministic-first semantic support, and mode-specific Howard evaluation.  
> **Source-quality / source-authority ranking is intentionally NOT defined by this update. It remains a separate required design lane.**


# 0. CORE RULE

Intent is a mostly linear five-specialist recipe.

Its job is to understand the current user turn, preserve what the user actually communicated, identify what work is required next, and produce:

1. a visible conversational Intent result for the user; and
2. a structured machine handoff that becomes the root turn ledger for Context and all later recipes.

Intent does NOT:
- read durable SQLite memory;
- search conversation archives;
- resolve historical project knowledge;
- execute tools;
- perform web research;
- treat model guesses as durable truth;
- claim tool success without later receipts.

Intent may KNOW which capabilities/tools currently exist only at the Organizer stage. It may nominate a capability. It may not use it.

---

# 1. HIGH-LEVEL PIPELINE

```text
RAW USER PROMPT
      |
      v
[1] SPELL
      |
      | fresh structured artifact
      | CLEAR KV
      v
[2] TERM / MEANING
      |
      | fresh structured artifact
      | CLEAR KV
      v
[3] PROMPT ANALYST
      |
      | fresh structured artifact
      | CLEAR KV
      v
[4] INTENT ORGANIZER
      |
      | structured Intent ledger
      | CLEAR KV
      +----------------------------+
      |                            |
      v                            v
[5] HOWARD                  CONTEXT HANDOFF
CONVERSATIONALIZER          (next recipe later)
      |
      v
VISIBLE INTENT RESPONSE
      |
      v
CLEAR KV
```

**KV rule:** clear model KV/attention cache on every adapter switch.

Adapters may remain warm in RAM if the runtime allows it.  
What survives specialist switches is explicit structured data, not hidden neural cache state.

---

# 2. FIVE SPECIALISTS

## 1 — SPELL

### Core question
"What text was probably intended?"

### Input
- raw user prompt

### Host helpers
- optional `ftfy` before Spell only when encoding/Unicode damage is detected
- `difflib` after Spell to create a transparent edit map

### Responsibilities
- obvious spelling repair;
- obvious punctuation repair;
- obvious capitalization repair;
- obvious malformed-word repair;
- preserve the user's wording and style as much as possible;
- flag uncertain corrections rather than inventing replacements.

### Required output
```text
raw_prompt
normalized_prompt
spell_edits[]
uncertain_corrections[]
```

### Hard prohibitions
Spell does not:
- paraphrase the user's idea;
- infer project meaning;
- decide intent;
- resolve history;
- access SQLite;
- use tools.

---

## 2 — TERM / MEANING

### Core question
"What do the user's words probably mean in this current turn?"

### Inputs
- raw prompt
- normalized prompt
- spell uncertainties
- host linguistic map

### Host linguistic support
Use lightweight deterministic parsing before the 3B Meaning specialist.

#### `re`
Use for cheap, common structural detection:
- explicit time expressions;
- URLs;
- obvious IDs;
- quoted spans;
- paths;
- simple protocol-like syntax;
- file-like strings.

#### `regex`
Use only when normal `re` is insufficient:
- advanced Unicode cases;
- overlapping matches;
- deliberately bounded advanced patterns;
- fuzzy regex only when a specific tested case earns it.

Do not use `regex` as a meaning engine.

Compile patterns once at startup. Do not compile per prompt.

#### spaCy
Use for:
- tokens;
- lemmas;
- noun chunks;
- named-entity candidates;
- dependency relationships;
- candidate multi-word terms.

spaCy supports the Meaning specialist. It does not decide durable meaning.

### Responsibilities of Meaning 3B
- interpret current-turn wording;
- identify unusual terms;
- identify named/project-looking terms;
- identify likely aliases;
- identify pronoun/reference candidates that can be understood from the current turn;
- provide provisional meaning;
- mark lookup-worthy terms for Context;
- provide confidence.

### Example
```text
term: "Puppet Theater"
type_guess: named_project_or_capability
current_use_guess: user wants to interact with it
meaning_status: provisional
context_lookup_needed: true
```

### Critical rule
Meaning output is PROVISIONAL.

A model interpretation is never authoritative simply because the model is confident.

### Hard prohibitions
Meaning does not:
- query SQLite;
- search prior conversations;
- load durable project definitions;
- resolve old state;
- call tools;
- claim historical knowledge.

---

## 3 — PROMPT ANALYST

### Core question
"What did the user communicate?"

### Inputs
- raw prompt
- normalized prompt
- Meaning report
- source spans produced by host parsing

### Responsibilities

#### TGT
- Topics
- Goals
- Tasks

#### Communication breakdown
- Statements
- Questions
- Directions
- Approvals

#### Interaction
- interaction_mode

Initial useful vocabulary:
```text
straightforward
conversational
exploratory
playful
joking
ordering_or_directive
excited
upset_sad
upset_disappointed
upset_angry_external
upset_angry_at_model
```

The vocabulary is testable and may evolve later.

#### Additional outputs
- important_claims
- unresolved_items
- control_signals[] when explicitly communicated

R2 control-signal vocabulary is host/schema owned:

```text
AFFIRM_PRIOR
CORRECT_PRIOR
REJECT_PRIOR
UNDO_PRIOR_EFFECT
CONTINUE_PRIOR_STATE
NONE
AMBIGUOUS_TARGET
```

These are communication classifications, not database actions. They preserve exact source spans. The host only gives them operational meaning when a relevant outstanding provisional semantic transaction or reversible host action actually exists.

### Key classification rule
A wish/request is not automatically a factual assertion.

Example:
```text
"Tell me it's not going to rain."
```

Analyst can classify:
```text
direction/request:
- tell me it is not going to rain

user factual weather assertion:
- none
```

This avoids forcing the Meaning specialist to perform a long epistemic reasoning chain.

### Hard prohibitions
Analyst does not:
- see or select tools;
- call tools;
- retrieve memory;
- decide whether a tool should execute;
- resolve historical references;
- ask the user a clarification by itself.

---

## 4 — INTENT ORGANIZER

### Core question
"What needs to happen because of what the user communicated?"

### Inputs
- Meaning report
- Analyst report
- current host capability registry

### Tool/capability visibility
Organizer MAY receive compact authoritative knowledge of available capabilities.

Example:
```text
AVAILABLE_CAPABILITIES
- alarm_set
- memory_save
- web_search
- image_generate
- puppet_theater
```

This is capability KNOWLEDGE ONLY.

Organizer has no execution authority.

### Responsibilities
- primary_intent;
- secondary_intents;
- requirement generation;
- requirement grouping;
- priority/order;
- dependencies;
- context needs;
- capability/lane candidates;
- clarification status;
- memory candidates;
- unresolved blockers;
- validated prior-state control signals copied from the Analyst when present.

### Clarification restraint
Ambiguity does not automatically require asking the user.

Example:
```text
"that adapter"
"same test as last time"
```

Organizer may output:
```text
clarification_required: false
context_resolution_first: true
```

Context gets a chance to resolve prior references before the user is bothered.

### Lanes/capabilities
Lanes are extensible routable work branches, not a permanently fixed set.

Examples:
```text
generic/direct_answer
generic/research
generic/reasoning
project/code_lab
project/puppet_theater
game/go_fish
system/tool_operation
```

Organizer needs to know a lane/capability exists and what class of requirement it can satisfy. It does not need to understand that branch's internal recipe.

### RapidFuzz role — LOCKED
RapidFuzz is a bounded canonical-name helper, primarily after Organizer inference.

It does NOT decide semantics.

Preferred flow:
```text
Organizer proposes capability candidate
        |
        v
exact registry ID?
  yes -> accept
  no
        |
        v
exact declared alias?
  yes -> canonicalize
  no
        |
        v
RapidFuzz against SMALL CURRENT REGISTRY
        |
        +-> high score: candidate canonicalization
        +-> medium: leave ambiguous
        +-> low: reject
```

Initial test-only score bands:
```text
90-100  strong candidate
80-89   possible candidate only
<80     ignore
```

Do NOT freeze these thresholds until field testing.

For very short names, prefer exact/alias matching because fuzzy scores can mislead.

RapidFuzz must never be used in Intent to fuzzy-search:
- durable memory;
- old project terms;
- conversation history;
- SQLite;
- semantic knowledge.

### Hard prohibitions
Organizer does not:
- execute tools;
- create final tool packets;
- write SQLite memory;
- claim a tool succeeded;
- convert capability candidacy into a receipt;
- silently replace unresolved history with a guess.

---

## 5 — HOWARD CONVERSATIONALIZER

### Core question
"How should Howard naturally communicate the completed Intent result?"

### Inputs
- Organizer result
- interaction mode
- selected current-turn details

### Responsibilities
- conversationalize structured Intent;
- preserve Organizer decisions;
- maintain Howard voice;
- make the result natural and understandable.

### Hard prohibitions
Howard does not:
- perform new research;
- retrieve memory;
- call tools;
- change the primary intent;
- invent new requirements;
- convert provisional meaning into fact;
- hide or discard required work.

### Reuse rule
This adapter is deliberately reusable later wherever the contract is truly:

```text
STRUCTURED COMPLETED WORK
        ->
NATURAL HOWARD CONVERSATION
```

Confirmed reuse positions are contract-scoped, not free-form:
- Intent commentary;
- Context lane commentary;
- final Context synthesis;
- per-requirement Result commentary;
- final Result composition.

Each mode has its own AAE Specialist Awareness and is evaluated separately even when the adapter hash is the same. Fresh KV is mandatory between learned boundaries. Do not give Howard a second semantic job merely because the adapter is loaded.

---

# 3. HOST/PYTHON INTENT MODULES

## Foundation — use from the beginning

```text
spaCy
jsonschema
difflib
re
uuid
hashlib
dataclasses
```

## Available but invoke only when earned by the input

```text
ftfy
RapidFuzz
regex
```

### Module ownership

```text
ftfy
-> optional encoding/Unicode cleanup before Spell

re
-> cheap structural span detection

regex
-> exceptional advanced structural detection

spaCy
-> linguistic map for Meaning

difflib
-> exact Spell edit provenance

jsonschema
-> validate every specialist artifact

uuid
-> turn IDs, requirement IDs, span IDs, artifact IDs

hashlib
-> provenance/change hashes

dataclasses
-> host-side structured Intent objects

RapidFuzz
-> bounded canonicalization against current Organizer capability registry
```

---

# 4. JSONSCHEMA GATES

Every specialist output must pass a host-owned schema gate before the next specialist receives it.

```text
SPECIALIST OUTPUT
      |
      v
JSONSCHEMA VALID?
   |        |
  YES       NO
   |        |
   v        v
NEXT      BOUNDED
STAGE     REPROMPT
```

The model supplies judgment.

The host enforces:
- required fields;
- field types;
- enum values;
- array/object shape;
- ID format;
- nullability;
- completion state.

Do not allow "almost valid" specialist packets to leak downstream.

---

# 5. SOURCE SPANS

Intent should preserve stable source spans from the user's actual wording.

Example:
```text
S001
raw_text: "this sunday"
normalized_text: "this Sunday"
kind: relative_date_expression

S002
raw_text: "wake me at 7am"
normalized_text: "Wake me at 7 AM"
kind: direction
```

Later artifacts should reference `S001`, `S002`, etc. rather than repeatedly re-parsing or paraphrasing the original message.

This reduces progressive summarization drift.

---

# 6. PERSISTENT TURN LEDGER

Intent creates the root machine contract for the entire user turn.

This is NOT durable user memory.

It persists only through the active recipe chain and archive/debug record.

Recommended shape:

```text
TURN
  turn_id

SOURCE
  raw_prompt
  normalized_prompt
  spell_edits

SPANS
  S001
  S002
  ...

TERM_CANDIDATES
  T001
  T002
  ...

INTENT
  topics
  goals
  tasks
  statements
  questions
  directions
  approvals
  interaction_mode
  primary_intent
  secondary_intents

REQUIREMENTS
  R001
  R002
  ...

UNRESOLVED
  U001
  U002
  ...

CAPABILITY_CANDIDATES
  ...

MEMORY_CANDIDATES
  ...

CONTEXT_RESOLUTIONS
  ... added later

TOOL_RECEIPTS
  ... added later

LANE_RESULTS
  ... added later

FINAL_COMPLETION
  ... added later
```

### Critical persistence rule
Later recipes APPEND resolutions/evidence.

They do not rewrite history to pretend Intent always knew the answer.

Example:

```text
INTENT TERM CANDIDATE
T001:
"Puppet Theater"
provisional_type: project/capability
```

Later Context may append:

```text
CONTEXT RESOLUTION
T001:
resolved: true
canonical_id: puppet_theater
authoritative_source: saved_term_record_0042
```

The original provisional interpretation stays visible for forensic/training analysis.

---

# 7. WHAT PERSISTS HOW FAR

```text
Raw prompt
-> entire turn + archive

Normalized prompt
-> entire turn

Spell edit map
-> entire turn/debug

spaCy full linguistic dump
-> Intent only; optional debug archive

Source spans
-> entire turn

Provisional term meanings
-> until Context resolves/rejects them

Topics/goals/tasks
-> entire turn

Statements/questions/directions/approvals
-> entire turn

Primary/secondary intent
-> entire turn

Interaction mode
-> through final response, then expire

Requirement IDs
-> ENTIRE TURN; core backbone

Capability candidates
-> until actual tool/lane judgment

Unresolved items
-> until resolved or clarification

Memory candidates
-> until Context judges them

Howard's visible Intent prose
-> UI/log only; NOT downstream authority
```

---

# 8. USER-FACING UI CONTRACT

During processing, only one compact status line must remain visible:

```text
Howard is forming intent... >v
```

The dropdown is collapsed by default.

If opened, it may show status only:

```text
✓ SPELL
Howard reviewed the user's wording.

✓ MEANING
Howard interpreted the user's meaning.

✓ ANALYST
Howard analyzed the communication.

✓ ORGANIZER
Howard decided the first requirements.
```

Do not expose raw chain-of-thought or internal specialist reasoning.

After completion, the final Howard Intent result is visible outside the dropdown:

```text
INTENT:
<Howard's conversational intent result>
```

The machine pipeline uses the structured Intent ledger, NOT Howard's user-facing prose.

---

# 9. EXAMPLE — CHURCH PLAN

## User
```text
Howard im going to church this sunday.
wake me at 7am so i can go.
I need to remember to bring my bible and wear my nice shoes.
```

## Spell
```text
Howard, I'm going to church this Sunday.
Wake me at 7 AM so I can go.
I need to remember to bring my Bible and wear my nice shoes.
```

## Host structural spans
```text
S001 = "this Sunday" -> relative_date_expression
S002 = "7 AM" -> time_expression
S003 = "bring my Bible" -> preparation requirement
S004 = "wear my nice shoes" -> preparation requirement
```

## Meaning
```text
"this Sunday"
-> relative date reference
-> resolution deferred

"wake me at 7 AM"
-> user wants a scheduled wake-up

"bring my Bible"
-> outing preparation item

"wear my nice shoes"
-> outing preparation item
```

## Analyst
```text
TOPICS
- church outing
- Sunday
- wake-up time
- preparation items

GOALS
- get up in time for church
- remember preparation items

TASKS
- wake user at 7 AM Sunday
- remember Bible
- remember nice shoes

STATEMENTS
- user plans to go to church this Sunday

DIRECTIONS
- wake me at 7 AM
- remember Bible
- remember nice shoes

QUESTIONS
- none

APPROVALS
- none

INTERACTION_MODE
- straightforward
- planning

UNRESOLVED
- exact calendar date for "this Sunday"
```

## Organizer host capability input
```text
AVAILABLE_CAPABILITIES
- alarm_set
- memory_save
```

## Organizer output
```text
PRIMARY_INTENT
Prepare user for church this Sunday.

REQUIREMENTS

R001
Wake user Sunday at 07:00.
context_needed: exact Sunday date
capability_candidate: alarm_set
execution_status: not_executed

R002
Remember Bible for church outing.
scope_guess: event_bound
capability_candidate: memory/reminder handling
execution_status: not_executed

R003
Remember nice shoes for church outing.
scope_guess: event_bound
capability_candidate: memory/reminder handling
execution_status: not_executed

GROUPING
R001, R002, R003 belong to the same church outing.

CLARIFICATION
not yet required
reason: Context may resolve the relative date and relevant state.
```

## Visible Howard Intent
```text
INTENT:
You've got church this Sunday. You want to be up at 7 AM,
and you need to make sure you have your Bible and your nice
shoes ready. I'll treat those as parts of the same Sunday plan.
```

## Context handoff
```text
PRIMARY_INTENT
Prepare user for church this Sunday.

RELATIVE_REFERENCES
- "this Sunday" -> unresolved

REQUIREMENTS
- R001 wake at 07:00
- R002 remember Bible
- R003 remember nice shoes

GROUP
- same church outing

CAPABILITY_CANDIDATES
- R001 -> alarm_set
- R002/R003 -> memory/reminder handling

TOOLS_EXECUTED
- none

UNRESOLVED
- exact Sunday date

CLARIFICATION
- not yet required
```

---

# 10. EXAMPLE — WEATHER / DESIRED ANSWER DISTINCTION

## User
```text
any idea of its going to rain today.
Im thinking about going to 18th street park.
I really want to get out of the house Howard.
tell me its not goiin rain.
```

## Key Intent distinction
```text
QUESTION
- Is it going to rain today?

DIRECTION / DESIRED OUTCOME
- "Tell me it's not going to rain."

USER FACTUAL WEATHER CLAIM
- none
```

Organizer may conclude:
```text
current weather information is required
```

It must NOT convert:
```text
"tell me it's not going to rain"
```
into:
```text
"it will not rain"
```

This is a training target:
```text
wish/request != assertion
```

---

# 11. CONTEXT BOUNDARY

Intent says:
```text
What appears to matter?
What did the user communicate?
What needs to happen?
What remains unresolved?
Which known capabilities might later satisfy requirements?
```

Downstream Context owns:
```text
What do we actually already know?
Have we talked about this before?
What prior meaning/state is authoritative?
Can provisional Intent interpretations be repaired?
What unresolved references can be grounded without bothering the user?
```

SQLite is reserved for Context in this architecture.

Intent may emit:
```text
term_lookup_needed: true
```

Intent does NOT perform the lookup.

---

# 12. NON-GOALS FOR THE INTENT COMPARTMENT — R2

Intent itself does not implement downstream recipe work:

- Context retrieval/grounding;
- SQLite semantic-memory lookup;
- date/current-fact resolution that belongs to Context or external work;
- web research;
- tool execution;
- attachment/tool receipt generation;
- durable semantic-memory judgment;
- Completion;
- Result publication.

Cross-recipe Howard reuse is now confirmed only through mode-specific AAE contracts. Intent still owns only its own Howard presentation call.

This artifact remains independently testable even though the full R2 spine is now designed.

---

# 13. LATER INDEPENDENT SLICE TESTING

Each slice should eventually have its own test harness.

Suggested independent targets:

```text
test_spell
test_host_surface_parser
test_meaning
test_analyst
test_organizer
test_capability_canonicalizer
test_howard_conversationalizer
test_intent_end_to_end
```

Each test should record:
- exact input;
- specialist adapter/version;
- structured output;
- schema pass/fail;
- reprompt count;
- latency;
- token count;
- KV clear confirmation;
- human judgment;
- known failure category.

Do not combine slices until each slice can be characterized independently.

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


# R2A. EARLY-INTENT ERROR CONTAINMENT FOCUS

Intent immutability remains a strength only if the initial semantic capture is correct.

Therefore Intent trust qualification must over-sample near-neighbor cases such as:

```text
wish vs factual assertion
future possibility vs current requirement
advisory idea vs explicit direction
remember request vs casual mention
correction vs change
undo/reject signal vs ordinary negation
multi-requirement dependency vs one blended requirement
ambiguous reference that requires Context vs safe current-turn interpretation
```

Schema validity is not sufficient evidence that Intent is correct.

No additional Intent adapter is allocated by R2. This is a training/evaluation focus, not a new learned compartment.

---

# 14. COMMAND-WINDOW PROTOTYPE DISPLAY

A future CLI runner should be able to look approximately like:

```text
C:\Howard\intent> python intent_prototype.py

[TURN] 8f8d...
[INTENT] Howard is forming intent...

[SPELL]      PASS  0.42s
[MEANING]    PASS  0.71s
[ANALYST]    PASS  0.66s
[ORGANIZER]  PASS  0.63s
[HOWARD]     PASS  0.58s

[KV] cleared between every adapter switch
[SCHEMA] all specialist packets valid
[TOOLS] none executed

INTENT:
You've got church this Sunday. You want to be up at 7 AM,
and you need to make sure you have your Bible and your nice
shoes ready. I'll treat those as parts of the same Sunday plan.

[HANDOFF]
turn_id: 8f8d...
requirements: 3
unresolved: 1
capability_candidates: 2
ready_for_context: true
```

This display is a prototype reference only. Exact formatting can change during implementation.

---

# 15. LOCKED DESIGN SUMMARY

```text
SPECIALISTS
1. Spell
2. Term / Meaning
3. Prompt Analyst
4. Intent Organizer
5. Howard Conversationalizer

KV
clear on every adapter switch

MODEL CONTINUITY
explicit structured artifacts only

SQLITE
not available to Intent

TOOL KNOWLEDGE
Organizer only

TOOL USE
not available to Intent

RAPIDFUZZ
bounded Organizer capability canonicalization only

REGEX
advanced structural detection only

SPACY
Meaning linguistic support

JSONSCHEMA
hard gate after every specialist

TURN LEDGER
Intent creates persistent requirement/source backbone

HOWARD PROSE
user-facing only; never downstream authority

CONTEXT
receives structured handoff and may resolve provisional meaning without mutating accepted Intent
```

---

# 16. BUILD PHILOSOPHY

Keep the five specialist jobs narrow.

If a deterministic host module can reliably do a mechanical task, let the host do it.

If a specialist must judge human meaning, train the specialist for that bounded judgment.

Do not let convenience quietly move Context, memory, tool execution, or historical authority backward into Intent.

Do not add more Intent slices until real independent testing shows a repeatable failure that the current five-part design cannot cleanly own.

**END OF INTENT PROTOTYPE BUILD SPEC**
