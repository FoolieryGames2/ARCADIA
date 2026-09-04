from __future__ import annotations

import importlib.util
import json
import struct
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify_qwen3_source.py"
MANIFEST = ROOT / "manifests" / "qwen3_4b_source_2026-09-04.json"
RUNTIME_MANIFEST = ROOT / "manifests" / "qwen3_runtime_candidate_b10796_q4_k_m_2026-09-04.json"


def _load_verifier() -> ModuleType:
    spec = importlib.util.spec_from_file_location("verify_qwen3_source", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_source_manifest_locks_identity_but_not_runtime_authority() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["repository"] == "Qwen/Qwen3-4B-Instruct-2507"
    assert manifest["repository_revision"] == "cdbee75f17c01a7cc42f958dc650907174af0554"
    assert manifest["standing"] == "SOURCE_INPUT_VERIFIED_RUNTIME_UNQUALIFIED"
    assert manifest["runtime_authority"] == "T0"
    assert manifest["qualification_boundary"] == {
        "source_package_verified": True,
        "gguf_conversion_verified": False,
        "cuda_load_verified": False,
        "specialist_invoker_verified": False,
        "adapter_isolation_verified": False,
        "authority_promotion_permitted": False,
    }
    assert len(manifest["safetensors_shards"]) == 3
    assert len(manifest["files"]) == 13


def test_safetensors_header_reader_rejects_out_of_range_tensor(tmp_path: Path) -> None:
    verifier = _load_verifier()
    header = json.dumps(
        {"weight": {"dtype": "F32", "shape": [1], "data_offsets": [0, 8]}},
        separators=(",", ":"),
    ).encode("utf-8")
    path = tmp_path / "bad.safetensors"
    path.write_bytes(struct.pack("<Q", len(header)) + header + b"1234")

    try:
        verifier.read_safetensors_header(path)
    except ValueError as exc:
        assert "invalid tensor offsets" in str(exc)
    else:
        raise AssertionError("out-of-range safetensors data offset was accepted")


def test_runtime_candidate_records_smoke_without_promoting_authority() -> None:
    manifest = json.loads(RUNTIME_MANIFEST.read_text(encoding="utf-8"))

    assert manifest["runtime_authority"] == "T0"
    assert manifest["llama_cpp"]["commit"] == ("9a4843cf2f1a3fc8e39f8148e92ee6bfe18e2db6")
    assert manifest["conversion"]["candidate"] == {
        "filename": "qwen3-4b-instruct-2507-q4_k_m.gguf",
        "quantization": "Q4_K_M",
        "size_bytes": 2497279008,
        "sha256": "4e00d30a00c71456198672a86a155a2935a7201f5112734f7dbf564362243f73",
    }
    assert manifest["base_only_smoke"]["layers_offloaded"] == "37/37"
    assert manifest["base_only_smoke"]["process_exit_code"] == 0
    assert manifest["native_tests"] == {
        "registered": 43,
        "passed": 43,
        "failed": 0,
        "ctest_elapsed_seconds": 444.24,
    }
    assert manifest["qualification_boundary"]["cuda_base_load_verified"] is True
    assert manifest["qualification_boundary"]["specialist_invoker_verified"] is False
    assert manifest["qualification_boundary"]["adapter_load_verified"] is False
    assert manifest["qualification_boundary"]["gate_a3_closed"] is False
    assert manifest["qualification_boundary"]["authority_promotion_permitted"] is False
