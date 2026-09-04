"""Verify the immutable local Qwen3 source package without ML dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "manifests" / "qwen3_4b_source_2026-09-04.json"


@dataclass(frozen=True, slots=True)
class Result:
    name: str
    passed: bool
    detail: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def check_manifest(manifest: dict[str, Any]) -> Result:
    expected = {
        "manifest_version": 1,
        "standing": "SOURCE_INPUT_VERIFIED_RUNTIME_UNQUALIFIED",
        "runtime_authority": "T0",
        "repository": "Qwen/Qwen3-4B-Instruct-2507",
        "repository_revision": "cdbee75f17c01a7cc42f958dc650907174af0554",
        "license": "Apache-2.0",
        "architecture": "Qwen3ForCausalLM",
    }
    failures = [
        f"{key}={manifest.get(key)!r}"
        for key, value in expected.items()
        if manifest.get(key) != value
    ]
    boundary = manifest.get("qualification_boundary")
    if not isinstance(boundary, dict) or boundary.get("authority_promotion_permitted") is not False:
        failures.append("qualification boundary does not fail closed")
    return Result("manifest_identity", not failures, "; ".join(failures) or "T0 source identity")


def check_files(manifest: dict[str, Any], model_root: Path) -> Result:
    failures: list[str] = []
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        return Result("source_files", False, "manifest files list is missing")
    for row in files:
        if not isinstance(row, dict):
            failures.append("invalid file row")
            continue
        local_name = row.get("local_name")
        if not isinstance(local_name, str):
            failures.append("invalid local_name")
            continue
        path = model_root / local_name
        if not path.is_file():
            failures.append(f"missing:{local_name}")
        elif path.stat().st_size != row.get("size_bytes"):
            failures.append(f"size:{local_name}")
        elif sha256(path) != row.get("sha256"):
            failures.append(f"hash:{local_name}")
    detail = f"{len(files) - len(failures)}/{len(files)} files verified"
    if failures:
        detail += f"; failed: {', '.join(failures[:3])}"
    return Result("source_files", not failures, detail)


def read_safetensors_header(path: Path) -> dict[str, Any]:
    with path.open("rb") as source:
        prefix = source.read(8)
        if len(prefix) != 8:
            raise ValueError("missing 8-byte header length")
        header_size = struct.unpack("<Q", prefix)[0]
        if header_size == 0 or header_size > 128 * 1024 * 1024:
            raise ValueError(f"invalid header size {header_size}")
        header_bytes = source.read(header_size)
    if len(header_bytes) != header_size:
        raise ValueError("truncated header")
    value = json.loads(header_bytes.decode("utf-8").rstrip(" "))
    if not isinstance(value, dict):
        raise ValueError("header is not a JSON object")
    data_size = path.stat().st_size - 8 - header_size
    for name, descriptor in value.items():
        if name == "__metadata__":
            continue
        if not isinstance(descriptor, dict):
            raise ValueError(f"invalid tensor descriptor: {name}")
        offsets = descriptor.get("data_offsets")
        if (
            not isinstance(offsets, list)
            or len(offsets) != 2
            or not all(isinstance(item, int) for item in offsets)
            or offsets[0] < 0
            or offsets[0] > offsets[1]
            or offsets[1] > data_size
        ):
            raise ValueError(f"invalid tensor offsets: {name}")
    return value


def check_index_and_headers(manifest: dict[str, Any], model_root: Path) -> Result:
    try:
        index = load_json(model_root / "model.safetensors.index.json")
        weight_map = index.get("weight_map")
        if not isinstance(weight_map, dict):
            raise ValueError("weight_map is missing")
        referenced = sorted(set(weight_map.values()))
        expected_shards = manifest.get("safetensors_shards")
        if referenced != expected_shards:
            raise ValueError(f"shard set mismatch: {referenced!r}")
        if len(weight_map) != manifest.get("tensor_count"):
            raise ValueError(f"tensor count mismatch: {len(weight_map)}")
        metadata = index.get("metadata")
        if not isinstance(metadata, dict) or metadata.get("total_size") != manifest.get(
            "tensor_payload_size_bytes"
        ):
            raise ValueError("tensor payload size mismatch")
        header_tensors: set[str] = set()
        for shard in referenced:
            header = read_safetensors_header(model_root / shard)
            header_tensors.update(name for name in header if name != "__metadata__")
        indexed_tensors = set(weight_map)
        if header_tensors != indexed_tensors:
            missing = len(indexed_tensors - header_tensors)
            extra = len(header_tensors - indexed_tensors)
            raise ValueError(f"header/index mismatch: missing={missing} extra={extra}")
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        return Result("safetensors_index", False, str(exc))
    return Result(
        "safetensors_index",
        True,
        f"{len(weight_map)} tensors across {len(referenced)} valid shards",
    )


def check_config(manifest: dict[str, Any], model_root: Path) -> Result:
    try:
        config = load_json(model_root / "config.json")
        architectures = config.get("architectures")
        passed = (
            architectures == [manifest["architecture"]]
            and config.get("model_type") == "qwen3"
            and config.get("torch_dtype") == manifest["parameter_dtype"]
            and config.get("max_position_embeddings") == manifest["declared_context_length"]
        )
    except (KeyError, OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        return Result("model_config", False, str(exc))
    return Result(
        "model_config",
        passed,
        f"architecture={architectures!r} layers={config.get('num_hidden_layers')!r}",
    )


def verify(
    manifest_path: Path = MANIFEST_PATH, model_root: Path | None = None
) -> tuple[Result, ...]:
    manifest = load_json(manifest_path)
    resolved_root = model_root or ROOT / str(manifest["local_path"])
    return (
        check_manifest(manifest),
        check_files(manifest, resolved_root),
        check_config(manifest, resolved_root),
        check_index_and_headers(manifest, resolved_root),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--model-root", type=Path)
    args = parser.parse_args()
    results = verify(
        args.manifest.resolve(), args.model_root.resolve() if args.model_root else None
    )
    for result in results:
        standing = "PASS" if result.passed else "FAIL"
        print(f"{standing:4}  {result.name:22} {result.detail}")
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
