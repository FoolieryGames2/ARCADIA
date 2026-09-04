from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify_architecture_freeze.py"


def _load_verifier() -> ModuleType:
    spec = importlib.util.spec_from_file_location("verify_architecture_freeze", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_architecture_freeze_payload_is_exact_and_hash_verified() -> None:
    verifier = _load_verifier()
    results = verifier.verify()

    assert results
    assert all(result.passed for result in results)
    assert {result.name for result in results} == {
        "payload_manifest",
        "payload_count",
        "payload_hashes",
        "authority_file_set",
    }


def test_architecture_manifest_preserves_open_qualification_standing() -> None:
    verifier = _load_verifier()
    manifest = verifier.load_manifest(verifier.MANIFEST_PATH)

    assert manifest["checkpoint_id"] == "ARCADIA-V0.1-ARCHITECTURE-FREEZE-2026-09-04"
    assert manifest["standing"] == (
        "ARCHITECTURE_FROZEN_IMPLEMENTATION_AND_RUNTIME_QUALIFICATION_OPEN"
    )
    assert manifest["foundation_model"]["repository"] == "Qwen/Qwen3-4B-Instruct-2507"
    assert manifest["foundation_model"]["deployment_identity_status"] == "UNQUALIFIED"
    assert manifest["supersession"]["disposition"] == (
        "HISTORICAL_PHASE0_SPIKE_EVIDENCE_ONLY"
    )
    assert manifest["runtime_authority"] == "T0"
    assert manifest["gate_a1"] == "OPEN"
