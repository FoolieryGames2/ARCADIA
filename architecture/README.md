# ARCADIA architecture authority

The current v0.1 architecture authority is the immutable 2026-09-04 freeze at:

`v0.1/freeze-2026-09-04/`

Read its `README_FIRST.md`, full freeze checkpoint, and build handoff before the
applicable recipe freeze document. The older 2026-08-29 prototype bundle remains
an implementation-detail baseline only where it does not conflict with this freeze.

The checked-in payload is byte-preserved through `.gitattributes`. Its exact file
set and all hashes are bound by:

`manifests/architecture_freeze_v0_1_2026-09-04.json`

Verify it with:

```bat
check_architecture_freeze.bat
```

The freeze locks `Qwen/Qwen3-4B-Instruct-2507` as the starting model family. It
does not qualify an exact GGUF, llama.cpp build, inference profile, adapter, or
runtime authority. Those remain measured A3/K work, and learned authority remains T0.
