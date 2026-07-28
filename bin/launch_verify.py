from __future__ import annotations

from pathlib import Path

from config_contract import ContractError
from contract_utils import load_json, mapping, sha256_digest, sha256_file
from launch_common import MANIFEST_VERSION


def verify_bundle(bundle: Path) -> dict[str, object]:
    bundle = bundle.resolve()
    manifest_path = bundle / "manifest.json"
    manifest = load_json(manifest_path, "launch bundle manifest")
    if manifest.get("schema_version") != MANIFEST_VERSION:
        raise ContractError(f"launch bundle schema_version must be {MANIFEST_VERSION}")
    digest = manifest.get("digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise ContractError("launch bundle manifest has no digest")
    receipts = manifest.get("files")
    if not isinstance(receipts, list):
        raise ContractError("launch bundle manifest.files must be a list")
    expected_paths: set[str] = set()
    for index, receipt_raw in enumerate(receipts):
        receipt = mapping(receipt_raw, f"manifest.files[{index}]")
        path_value = receipt.get("path")
        expected_hash = receipt.get("sha256")
        expected_size = receipt.get("size")
        if not isinstance(path_value, str) or not path_value:
            raise ContractError(f"manifest.files[{index}].path must be a string")
        relative = Path(path_value)
        if relative.is_absolute() or ".." in relative.parts:
            raise ContractError(f"manifest.files[{index}].path must be relative")
        path = bundle / relative
        if not path.is_file():
            raise ContractError(f"launch bundle file is missing: {path_value}")
        if sha256_file(path) != expected_hash or path.stat().st_size != expected_size:
            raise ContractError(f"launch bundle file drift: {path_value}")
        expected_paths.add(relative.as_posix())
    actual_paths = {
        path.relative_to(bundle).as_posix()
        for path in bundle.rglob("*")
        if path.is_file() and path != manifest_path
    }
    if actual_paths != expected_paths:
        raise ContractError(
            f"launch bundle file set drift: missing={sorted(expected_paths - actual_paths)}, "
            f"extra={sorted(actual_paths - expected_paths)}"
        )
    payload = {key: value for key, value in manifest.items() if key not in {"digest", "runtime"}}
    actual_digest = sha256_digest(payload)
    if actual_digest != digest:
        raise ContractError(f"launch bundle manifest digest drift: expected={digest}, actual={actual_digest}")
    return manifest
