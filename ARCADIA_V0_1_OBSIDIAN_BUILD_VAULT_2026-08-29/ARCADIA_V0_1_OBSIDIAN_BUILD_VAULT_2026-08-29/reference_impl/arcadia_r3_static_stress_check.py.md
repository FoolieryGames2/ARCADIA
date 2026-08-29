---
title: "arcadia_r3_static_stress_check.py"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "reference-implementation"
source_path: "reference_impl/arcadia_r3_static_stress_check.py"
source_sha256: "6941a8e7ceb147baa3633800c046796f1199a358c572f58e5c40228a9d26af45"
source_bytes: 5722
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/reference-implementation"
aliases:
  - "arcadia_r3_static_stress_check.py"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `reference-implementation`  
> **Frozen source:** `reference_impl/arcadia_r3_static_stress_check.py` · SHA-256 `6941a8e7ceb147ba…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[TRACE_STATIC_CHECK.txt]] · [[06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES]]

# Source artifact — `arcadia_r3_static_stress_check.py`

> [!note] Lossless-content conversion
> Original file type: `.py` · decoded as `utf-8`. The complete source text is retained below; the original SHA-256 is in frontmatter.

````python
#!/usr/bin/env python3
"""Reproducible static stress checks for the supplied A.R.C.A.D.I.A. R3 trace.

This intentionally reads only a caller-supplied workstation file. It performs no
network access and does not depend on project history outside that file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


OPEN = "<A.R.C.A.D.I.A_ADAPTER_CALL>"
CLOSE = "</A.R.C.A.D.I.A_ADAPTER_CALL>"


def strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


STRICT_DECODER = json.JSONDecoder(
    object_pairs_hook=strict_object,
    parse_constant=lambda value: (_ for _ in ()).throw(
        ValueError(f"non-finite JSON number: {value}")
    ),
)


def physical_adapter(specialist: str) -> str:
    for shared in ("Conversation Resolver", "Conversational Howard"):
        if specialist == shared or specialist.startswith(shared + " / "):
            return shared
    return specialist


def lru_stats(adapters: list[str], capacity: int = 5) -> tuple[int, int, int]:
    cache: list[str] = []
    loads = evictions = hits = 0
    for adapter in adapters:
        if adapter in cache:
            hits += 1
            cache.remove(adapter)
            cache.append(adapter)
            continue
        loads += 1
        if len(cache) == capacity:
            cache.pop(0)
            evictions += 1
        cache.append(adapter)
    return loads, evictions, hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()

    text = args.trace.read_text(encoding="utf-8")
    failures: list[str] = []

    print(f"file: {args.trace}")
    print(f"envelope tags: open={text.count(OPEN)} close={text.count(CLOSE)}")
    if text.count(OPEN) != text.count(CLOSE):
        failures.append("AAE envelope tag counts differ")

    all_envelopes = re.findall(
        re.escape(OPEN) + r".*?" + re.escape(CLOSE), text, re.S
    )
    slice_start = re.search(r"^# 6\. SLICE", text, re.M)
    if slice_start is None:
        failures.append("Slice 1 start was not found")
        actual_envelopes: list[str] = []
        template_count = len(all_envelopes)
    else:
        template_count = len(
            re.findall(
                re.escape(OPEN) + r".*?" + re.escape(CLOSE),
                text[: slice_start.start()],
                re.S,
            )
        )
        actual_envelopes = re.findall(
            re.escape(OPEN) + r".*?" + re.escape(CLOSE),
            text[slice_start.start() :],
            re.S,
        )
    print(
        f"envelopes: templates={template_count} actual_slice_calls={len(actual_envelopes)}"
    )

    for index, envelope in enumerate(actual_envelopes, 1):
        data_match = re.search(r"\[CALL_DATA\]\s*\n", envelope)
        response_match = re.search(r"\n\[RESPONSE_CONTRACT\]", envelope)
        specialist_match = re.search(r"^specialist: (.+)$", envelope, re.M)
        specialist = specialist_match.group(1) if specialist_match else "UNKNOWN"
        if not data_match or not response_match or response_match.start() <= data_match.end():
            failures.append(f"call {index} ({specialist}): missing/broken CALL_DATA boundary")
            continue
        payload = envelope[data_match.end() : response_match.start()].strip()
        try:
            _, end = STRICT_DECODER.raw_decode(payload)
            if payload[end:].strip():
                raise ValueError("non-JSON trailing content")
        except Exception as exc:  # report the exact fixture failure and continue
            failures.append(f"call {index} ({specialist}): invalid CALL_DATA JSON: {exc}")

    json_fences = re.findall(r"```json\s*\n(.*?)\n```", text, re.S | re.I)
    for index, payload in enumerate(json_fences, 1):
        try:
            _, end = STRICT_DECODER.raw_decode(payload)
            if payload[end:].strip():
                raise ValueError("non-JSON trailing content")
        except Exception as exc:
            failures.append(f"JSON fence {index}: invalid JSON: {exc}")
    print(f"JSON fences parsed strictly: {len(json_fences)}")

    starts = [
        (match.start(), int(match.group(1)))
        for match in re.finditer(r"^# (6|7|8|9|10)\. SLICE", text, re.M)
    ]
    for position, (start, section) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(text)
        chunk = text[start:end]
        specialists = re.findall(r"^specialist: (.+)$", chunk, re.M)
        adapters = [physical_adapter(name) for name in specialists]
        loads, evictions, hits = lru_stats(adapters)
        chars = sum(
            len(block)
            for block in re.findall(
                re.escape(OPEN) + r".*?" + re.escape(CLOSE), chunk, re.S
            )
        )
        print(
            f"slice {section - 5}: calls={len(adapters)} "
            f"distinct_adapters={len(set(adapters))} cold_LRU_loads={loads} "
            f"LRU_evictions={evictions} HOT_hits={hits} model_view_chars={chars}"
        )

    modes = Counter(
        match.group(1)
        for envelope in actual_envelopes
        if (match := re.search(r"^specialist: (.+)$", envelope, re.M))
    )
    print(f"specialist modes represented: {len(modes)}")

    if failures:
        print("FAILURES:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````
