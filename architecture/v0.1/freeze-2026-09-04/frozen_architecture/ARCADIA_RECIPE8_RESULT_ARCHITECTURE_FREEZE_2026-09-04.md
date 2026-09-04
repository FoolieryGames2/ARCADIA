# A.R.C.A.D.I.A. Recipe 8 — Result Architecture Freeze

**Date:** 2026-09-04  
**Standing:** Architecturally frozen for v0.1 prototype implementation/testing.

## Purpose

Result answers only:

> **How should the already-decided final standing be communicated to the user clearly and naturally without changing reality?**

Result may choose wording, ordering, tone, and presentation. It may not alter terminal standing, invent facts, hide required blockers/failures, claim unverified actions, reopen work, or write persistence.

## Ingress

Recipe 8 receives only the immutable Final Standing Packet reference/hash:

```json
{
  "completion": {
    "artifact_ref": "FSP001",
    "hash": "sha256:..."
  }
}
```

No conversational-model call is allowed until the host validates the FSP and required lineage.

## Result Host preparation

The host deterministically builds:

1. **Disclosure Map**
   - `MUST_MENTION`
   - `MAY_MENTION`
   - `DO_NOT_EXPOSE`
2. **Literal Lock**
   - exact names, model IDs, versions, dates, quantities, filenames, paths, URLs, codes, exact quotes when required;
   - modes such as `EXACT_REQUIRED` vs display-flexible policy.
3. **Response Budget**
   - enough room for accurate communication, derived without a model.
4. **One small presentation packet per user-facing requirement.**

Internal IDs/hashes/adapter names/SQL details/repair history are not user-facing merely because they exist.

## Selected conversational adapter terminology

Architectural role name:

**selected conversational adapter**

`Howard` is only the concrete Howard personality/adapter when it occupies this role. Result architecture must not use “Howard” as a generic name for Arcadia, the base model, or all conversational variants.

## Per-requirement conversational comment

For v0.1, each relevant requirement gets one small fresh-KV presentation call.

Representative packet:

```json
{
  "user_facing_request": "Save the established model information to the user's model notes file.",
  "terminal_status": "BLOCKED",
  "established_facts": [],
  "unmet_components": [
    "The requested file save was not completed."
  ],
  "blockers": [
    "No unambiguous destination file could be resolved."
  ],
  "failures": [],
  "must_mention": [
    "The save did not happen.",
    "A destination file/path is needed."
  ],
  "may_mention": [],
  "must_not_claim": [
    "Do not claim the file was saved.",
    "Do not claim a destination was selected."
  ],
  "protected_literals": [],
  "target_comment_length": "concise"
}
```

The learned burden is intentionally small:

```text
Do not investigate.
Do not decide.
Do not remember.
Do not execute.
Do not reconcile.

Here is what is true.
Here is what must be said.
Here is what must not be claimed.
Here are strings you cannot alter.

Say it naturally.
```

Result packet sizes should be kept small and measured during implementation; broaden only from test evidence.

## Per-requirement validation

Host validates each conversational comment against:

- terminal standing consistency;
- allowed/support refs;
- Literal Lock;
- internal-ID leakage;
- `MUST_MENTION` coverage;
- must-not-claim rules;
- response budget.

Bounded wording repair may occur. If repair is exhausted, host produces a deterministic safe comment fallback. Truth wins over style.

Failed drafts never enter the normal transcript.

## Final conversational composition

After all validated requirement comments are produced, clear conversational KV and perform one fresh final composition call using only bounded validated presentation material.

Representative input:

```json
{
  "original_request": "Check what base model Arcadia is using and save that answer to my model notes file.",
  "overall_posture": "MIXED",
  "validated_comments": [
    "Arcadia's selected base model is Qwen/Qwen3-4B-Instruct-2507.",
    "I couldn't save it yet because I don't have a definite destination for your model notes file."
  ],
  "must_mention": [
    "Qwen/Qwen3-4B-Instruct-2507",
    "The save did not happen.",
    "A destination is needed."
  ],
  "protected_literals": [
    "Qwen/Qwen3-4B-Instruct-2507"
  ],
  "response_budget": {
    "presentation": "concise"
  }
}
```

The final conversational adapter combines already-approved statements; it does not re-decide what happened.

## Final host validation

Candidate final prose is not authoritative merely because the conversational adapter produced it.

Host validates in layers such as:

```text
UTF-8 / size
↓
internal-ID leak scan
↓
literal extraction + Literal Lock
↓
surface entity/sentence inspection
↓
proper-name corruption signals
↓
MUST_MENTION coverage
↓
must-not-claim / standing consistency
↓
response budget
```

Prototype bounded final wording repair: maximum 2 attempts.

If still invalid, host emits a deterministic minimal safe fallback from authoritative facts/blockers/failures/required next action. A boring truthful answer is preferred over fabricated prose.

## Validated Result artifact

After validation, host freezes exact publication-authorized text as `RSTxxx`:

```json
{
  "result_id": "RST001",
  "schema_version": "result@1",
  "result_hash": "sha256:...",
  "completion": {
    "artifact_ref": "FSP001",
    "hash": "sha256:..."
  },
  "validated_comment_refs": ["RCM001", "RCM002"],
  "response_text": "The selected model is ...",
  "validation": "PASS"
}
```

`RSTxxx` proves that **this exact text is validated for publication**. It does not prove delivery.

## Publication Host / transcript completion

Publication is host-owned:

```text
RSTxxx VALIDATED
    ↓
Publication Host
    ↓
send exact response text
    ↓
transport acknowledgement where supported
    ↓
store exact same published text in transcript
    ↓
verify transcript response hash == RST response hash
    ↓
increment transcript_commit_seq exactly once
    ↓
turn status = COMPLETED
    ↓
PUBxxx
```

The selected conversational adapter does not publish its own draft and does not mark the turn complete.

Candidate publication receipt:

```json
{
  "publication_receipt_id": "PUB001",
  "result_ref": "RST001",
  "response_hash": "sha256:...",
  "publication_status": "PUBLISHED",
  "transcript_commit_seq_before": 208,
  "transcript_commit_seq_after": 209,
  "verification": "PASS"
}
```

Relevant publication statuses include:

- `PUBLISHED`
- `DELIVERY_FAILED`
- `TRANSCRIPT_COMMIT_FAILED`

Publication/storage failures do not mutate `FSPxxx` or rerun semantic recipes merely because transport/transcript bookkeeping failed.

## Exact transcript rule

> **The normal transcript contains exactly what the user sent and exactly what Arcadia successfully published back to them.**

It does not contain failed conversational drafts, internal comments, repair prompts, validation errors, adapter traces, or safe fallbacks that were never published.

This rule is required so future Recipe 0 continuity retrieves the exact exchange the user actually experienced.

## v0.1 prototype scope lock

The compact Result presentation architecture is sufficient for the v0.1 prototype. Broaden conversational context or presentation affordances only when implementation/testing demonstrates a concrete need. Such broadening must not weaken the frozen authority boundary.

## Final authority chain

```text
FSPxxx
"What is finally true about every requirement?"
     ↓
selected conversational adapter
"How should I say that?"
     ↓
RSTxxx
"This exact response is validated for publication."
     ↓
Publication Host
"Did this exact text reach the user and enter completed transcript history?"
     ↓
PUBxxx
```

Only the successful publication/transcript path marks the turn `COMPLETED`.
