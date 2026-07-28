from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from config_contract import ContractError


MappingValue = dict[str, Any]


def mapping(value: object, label: str, *, error: type[Exception] = ContractError) -> MappingValue:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise error(f"{label} must be an object")
    return value


def strict_keys(
    value: MappingValue,
    allowed: set[str],
    label: str,
    *,
    error: type[Exception] = ContractError,
) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise error(f"{label} has unsupported fields: {', '.join(unknown)}")


def string(
    value: MappingValue,
    key: str,
    label: str,
    *,
    error: type[Exception] = ContractError,
) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result:
        raise error(f"{label}.{key} must be a non-empty string")
    return result


def load_json(path: Path, label: str, *, error: type[Exception] = ContractError) -> MappingValue:
    try:
        raw = json.loads(path.read_text())
    except OSError as exc:
        raise error(f"cannot read {label}: {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise error(f"{label} must use the JSON subset of YAML: {exc}") from exc
    return mapping(raw, label, error=error)


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_digest(value: object) -> str:
    return "sha256:" + sha256_bytes(canonical_json(value))


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
