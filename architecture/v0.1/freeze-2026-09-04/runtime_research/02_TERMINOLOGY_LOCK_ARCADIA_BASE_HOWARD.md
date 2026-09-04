# A.R.C.A.D.I.A. — Terminology Lock

**Date:** 2026-09-03  
**Status:** PROJECT-WIDE DOCUMENTATION RULE

## Canonical meanings

### A.R.C.A.D.I.A.

The complete host-authoritative system/runtime/architecture.

### Foundation / base model

The replaceable underlying language-model checkpoint used by A.R.C.A.D.I.A. learned specialists.

For the v0.1 starting family:

```text
Qwen/Qwen3-4B-Instruct-2507
```

### Specialist adapter

A bounded learned adapter trained/qualified for a specific A.R.C.A.D.I.A. semantic role or logical mode.

### Conversational adapter

A presentation/personality adapter used to articulate validated A.R.C.A.D.I.A. results to the user.

### Howard

**Howard is only the named Howard conversational adapter/personality.**

Howard is not:

```text
A.R.C.A.D.I.A. itself
A.R.C.A.D.I.A.'s base model
the generic name for all specialists
the runtime
the AdapterManager
the system's intelligence as a whole
```

Howard may later be one member of a larger set of selectable A.R.C.A.D.I.A. conversational moods/personas.

## Documentation rule

Use `Howard` only when the text directly references the Howard conversational adapter or a Howard-specific presentation mode.

Preferred generic wording:

```text
A.R.C.A.D.I.A. routes the requirement.
The Evidence Specialist evaluates the bounded evidence packet.
The conversational layer presents the validated result.
The foundation model is replaceable.
```

Howard-specific wording:

```text
The Howard conversational adapter renders the validated result.
Howard receives only the bounded presentation packet for this mode.
```

## Legacy cleanup targets

Older documents that use `Howard` as a synonym for the whole system, a recipe, or the underlying model should be treated as terminology debt.

Likewise, old hard-coded phrases such as:

```text
one resident 3B base
primary compatible 3B base family
```

must not be read as an architectural size lock. Where those statements identify the current v0.1 base, update them to the pinned Qwen3-4B family or to a size-neutral phrase such as `pinned compatible foundation model`.

Do not rewrite historical artifacts solely to hide history; patch current authority documents and record supersession where needed.
