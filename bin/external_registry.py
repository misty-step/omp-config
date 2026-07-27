"""Deterministic validation for vendored external skill payloads."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_ALLOWED_LICENSES = {
    "MIT": ("MIT License", "Permission is hereby granted"),
    "Apache-2.0": ("Apache License", "Version 2.0"),
    "BSD-2-Clause": ("Redistribution and use", "THIS SOFTWARE IS PROVIDED"),
    "BSD-3-Clause": ("Redistribution and use", "THIS SOFTWARE IS PROVIDED"),
    "ISC": ("Permission to use, copy, modify", "THE SOFTWARE IS PROVIDED"),
    "AGPL-3.0-or-later": ("GNU AFFERO GENERAL PUBLIC LICENSE", "either version 3"),
    "GPL-3.0-only": ("GNU GENERAL PUBLIC LICENSE", "either version 3"),
}


class ExternalRegistryError(ValueError):
    """A registry, receipt, license, or payload invariant failed."""


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _scalar(value: str) -> object:
    value = value.strip()
    if not value:
        return None
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [_unquote(part) for part in inner.split(",") if part.strip()]
    return _unquote(value)


def _parse_registry(path: Path) -> list[dict[str, object]]:
    """Parse the deliberately small registry YAML vocabulary without PyYAML."""
    sources: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    list_key: str | None = None
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if indent == 2 and stripped.startswith("- repo:"):
            if current is not None:
                sources.append(current)
            current = {"repo": _scalar(stripped.split(":", 1)[1])}
            list_key = None
            continue
        if current is None:
            if stripped == "sources:":
                continue
            raise ExternalRegistryError(f"{path} has unsupported YAML at line {line_number}")
        if indent >= 6 and stripped.startswith("-") and list_key is not None:
            value = _scalar(stripped[1:].strip())
            if value is None:
                raise ExternalRegistryError(f"{path} has an empty {list_key} entry at line {line_number}")
            values = current.setdefault(list_key, [])
            if not isinstance(values, list):
                raise ExternalRegistryError(f"{path} has a non-list {list_key} at line {line_number}")
            values.append(value)
            continue
        if indent != 4 or ":" not in stripped:
            raise ExternalRegistryError(f"{path} has unsupported YAML at line {line_number}")
        key, raw_value = stripped.split(":", 1)
        if not key or any(character.isspace() for character in key):
            raise ExternalRegistryError(f"{path} has an invalid key at line {line_number}")
        value = _scalar(raw_value)
        if value is None and key in {"include", "consumers"}:
            current[key] = []
            list_key = key
        else:
            current[key] = value
            list_key = None
    if current is not None:
        sources.append(current)
    if not sources:
        raise ExternalRegistryError(f"{path} declares no sources")
    return sources


def _root_from_contract(contract: Any) -> tuple[Path, Path]:
    skills = Path(contract.surface("skills").source)
    external = skills.parent / "external"
    return skills.parents[1], external


def _read_package_manifest(path: Path, label: str) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise ExternalRegistryError(f"{label} is missing or symlinked: {path}")
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ExternalRegistryError(f"{label} is invalid JSON: {path}: {error}") from error
    if not isinstance(parsed, dict):
        raise ExternalRegistryError(f"{label} must contain an object: {path}")
    return parsed


def _first_party_skill_links(root: Path, skills: Path) -> set[str]:
    manifest_path = root / "package.json"
    if not manifest_path.is_file():
        return set()
    manifest = _read_package_manifest(manifest_path, "OMP package manifest")
    omp = manifest.get("omp")
    if omp is None:
        return set()
    if not isinstance(omp, dict):
        raise ExternalRegistryError(f"{manifest_path} omp setting must be an object")
    links = omp.get("firstPartySkillLinks")
    if links is None:
        return set()
    if not isinstance(links, dict):
        raise ExternalRegistryError(f"{manifest_path} omp.firstPartySkillLinks must be an object")
    dependencies = manifest.get("dependencies")
    if not isinstance(dependencies, dict):
        raise ExternalRegistryError(f"{manifest_path} must declare dependencies for first-party skills")
    skills_relative = skills.relative_to(root)
    mapped: set[str] = set()
    for raw_consumer, raw_link in links.items():
        if not isinstance(raw_consumer, str):
            raise ExternalRegistryError(f"{manifest_path} has a non-string first-party consumer path")
        consumer_relative = _relative_path(raw_consumer, "first-party consumer")
        if consumer_relative.parent != skills_relative:
            raise ExternalRegistryError(
                f"{manifest_path} first-party consumer must be under {skills_relative}: {raw_consumer!r}"
            )
        if not isinstance(raw_link, dict):
            raise ExternalRegistryError(f"{manifest_path} first-party link {raw_consumer!r} must be an object")
        package_name = raw_link.get("package")
        target = raw_link.get("target")
        if not isinstance(package_name, str) or not package_name:
            raise ExternalRegistryError(f"{manifest_path} first-party link {raw_consumer!r} lacks package")
        target_relative = _relative_path(target, "first-party target")
        spec = dependencies.get(package_name)
        if not isinstance(spec, str) or not spec.startswith("file:"):
            raise ExternalRegistryError(
                f"{manifest_path} dependency {package_name!r} must use a file: spec for first-party skill"
            )
        package_reference = Path(spec[5:])
        if package_reference.is_absolute() or not package_reference.parts or any(
            part in {"", "."} for part in package_reference.parts
        ):
            raise ExternalRegistryError(f"{manifest_path} dependency {package_name!r} has invalid file spec {spec!r}")
        package_root = (root / package_reference).resolve(strict=False)
        package_manifest = _read_package_manifest(
            package_root / "package.json", f"first-party package {package_name!r}"
        )
        if package_manifest.get("name") != package_name:
            raise ExternalRegistryError(
                f"first-party package identity drift for {package_name!r}: "
                f"found {package_manifest.get('name')!r}"
            )
        consumer = root / consumer_relative
        if not consumer.is_symlink():
            raise ExternalRegistryError(f"first-party consumer is not a symlink: {consumer}")
        expected = (package_root / target_relative).resolve(strict=False)
        actual = consumer.resolve(strict=False)
        if actual != expected:
            raise ExternalRegistryError(
                f"first-party skill target drift for {consumer}: expected {expected}, got {actual}"
            )
        mapped.add(consumer_relative.as_posix())
    return mapped


def _relative_path(raw: object, field: str) -> Path:
    if not isinstance(raw, str) or not raw:
        raise ExternalRegistryError(f"receipt {field} must be a non-empty relative path")
    path = Path(raw)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ExternalRegistryError(f"receipt {field} escapes its vendor directory: {raw!r}")
    return path


def _vendor_dir(source: dict[str, object], external: Path) -> Path:
    explicit = source.get("vendor_dir")
    if isinstance(explicit, str) and explicit:
        path = external / explicit
    else:
        names = _aliases(source)
        candidates = [external / name for name in names if (external / name).exists()]
        if len(candidates) != 1:
            raise ExternalRegistryError(
                f"{source.get('repo')!r} needs vendor_dir or exactly one alias directory"
            )
        path = candidates[0]
    if path.parent != external or not path.name or path.name in {".", ".."}:
        raise ExternalRegistryError(f"registry vendor_dir is outside {external}: {path}")
    return path


def _skill_names(source: dict[str, object]) -> list[str]:
    skill_name = source.get("skill_name")
    include = source.get("include")
    if isinstance(skill_name, str) and skill_name:
        return [skill_name]
    if isinstance(include, list) and include and all(isinstance(name, str) and name for name in include):
        return list(include)
    raise ExternalRegistryError(f"{source.get('repo')!r} must declare skill_name or include")


def _aliases(source: dict[str, object]) -> list[str]:
    prefix = source.get("alias_prefix")
    if not isinstance(prefix, str) or not prefix:
        raise ExternalRegistryError(f"{source.get('repo')!r} lacks alias_prefix")
    return [prefix + name for name in _skill_names(source)]


def _expected_source_suffixes(source: dict[str, object]) -> set[str]:
    layout = source.get("layout")
    skills_path = source.get("skills_path")
    names = _skill_names(source)
    if layout == "multi-root" or not isinstance(skills_path, str) or not skills_path:
        return set()
    base = Path(skills_path)
    if base == Path("."):
        return {name for name in names}
    if len(names) > 1:
        return {base.as_posix()}
    return {names[0], (base / names[0]).as_posix()}


def _registry_sources(registry: Path, external: Path) -> dict[str, dict[str, object]]:
    by_vendor: dict[str, dict[str, object]] = {}
    for source in _parse_registry(registry):
        if source.get("default") is True:
            continue
        repo = source.get("repo")
        if not isinstance(repo, str) or not repo:
            raise ExternalRegistryError(f"{registry} has a source without repo")
        pin = source.get("pin")
        if not isinstance(pin, str) or not _SHA1.fullmatch(pin):
            raise ExternalRegistryError(f"{repo} must declare a 40-character immutable pin")
        ref = source.get("ref")
        if not isinstance(ref, str) or not ref:
            raise ExternalRegistryError(f"{repo} must declare ref")
        vendor = _vendor_dir(source, external)
        if vendor.name in by_vendor:
            raise ExternalRegistryError(f"duplicate registry vendor_dir {vendor.name!r}")
        by_vendor[vendor.name] = source
    return by_vendor


def _safe_vendor(vendor: Path) -> None:
    if vendor.is_symlink() or not vendor.is_dir():
        raise ExternalRegistryError(f"vendor directory must be a real directory: {vendor}")


def _read_receipt(vendor: Path) -> dict[str, object]:
    receipt = vendor / ".sync-meta.json"
    if receipt.is_symlink() or not receipt.is_file():
        raise ExternalRegistryError(f"{vendor} is missing a real .sync-meta.json receipt")
    try:
        parsed = json.loads(receipt.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ExternalRegistryError(f"{receipt} is invalid JSON: {error}") from error
    if not isinstance(parsed, dict):
        raise ExternalRegistryError(f"{receipt} must contain an object")
    return parsed


def _check_license(vendor: Path, source: dict[str, object], receipt: dict[str, object]) -> Path:
    license_name = receipt.get("license")
    if not isinstance(license_name, str) or license_name not in _ALLOWED_LICENSES:
        raise ExternalRegistryError(f"{vendor} has missing or unacceptable license {license_name!r}")
    if source.get("license") != license_name:
        raise ExternalRegistryError(f"{vendor} registry/receipt license drift")
    license_path = _relative_path(receipt.get("license_path"), "license_path")
    if source.get("license_path") != license_path.as_posix():
        raise ExternalRegistryError(f"{vendor} registry/receipt license_path drift")
    path = vendor / license_path
    if path.is_symlink() or not path.is_file() or path.resolve().parent != vendor.resolve():
        raise ExternalRegistryError(f"{vendor} has an invalid license path {license_path}")
    expected_hash = receipt.get("license_sha256")
    if not isinstance(expected_hash, str) or not _SHA256.fullmatch(expected_hash):
        raise ExternalRegistryError(f"{vendor} has no valid license_sha256")
    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual_hash != expected_hash:
        raise ExternalRegistryError(f"{vendor} license bytes do not match receipt")
    text = path.read_text(encoding="utf-8", errors="replace")
    markers = _ALLOWED_LICENSES[license_name]
    if any(marker.lower() not in text.lower() for marker in markers):
        raise ExternalRegistryError(f"{vendor} license content is not {license_name}")
    return license_path


def _check_payload(vendor: Path, receipt: dict[str, object], license_path: Path) -> None:
    payload = receipt.get("payload")
    hashes = receipt.get("payload_sha256")
    if not isinstance(payload, list) or not payload or not all(isinstance(item, str) for item in payload):
        raise ExternalRegistryError(f"{vendor} receipt payload must be a non-empty path list")
    if len(set(payload)) != len(payload):
        raise ExternalRegistryError(f"{vendor} receipt payload contains duplicates")
    payload_paths = {_relative_path(item, "payload") for item in payload}
    if license_path in payload_paths or Path(".sync-meta.json") in payload_paths:
        raise ExternalRegistryError(f"{vendor} receipt payload includes metadata")
    if not isinstance(hashes, dict) or set(hashes) != {path.as_posix() for path in payload_paths}:
        raise ExternalRegistryError(f"{vendor} payload/hash file lists drift")
    actual_files: set[str] = set()
    for path in vendor.rglob("*"):
        if path.is_symlink():
            raise ExternalRegistryError(f"{vendor} contains symlinked payload entry {path.relative_to(vendor)}")
        if path.is_file():
            actual_files.add(path.relative_to(vendor).as_posix())
    expected_files = {".sync-meta.json", license_path.as_posix()} | {path.as_posix() for path in payload_paths}
    if actual_files != expected_files:
        missing = sorted(expected_files - actual_files)
        extra = sorted(actual_files - expected_files)
        raise ExternalRegistryError(f"{vendor} payload file drift: missing={missing}, extra={extra}")
    for path in sorted(payload_paths):
        full = vendor / path
        if full.is_symlink() or not full.is_file() or full.resolve().parent != (vendor / path).resolve().parent:
            raise ExternalRegistryError(f"{vendor} has invalid payload path {path}")
        expected_hash = hashes.get(path.as_posix())
        if not isinstance(expected_hash, str) or not _SHA256.fullmatch(expected_hash):
            raise ExternalRegistryError(f"{vendor} has invalid payload hash for {path}")
        actual_hash = hashlib.sha256(full.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise ExternalRegistryError(f"{vendor} payload bytes do not match receipt: {path}")


def _validate_vendor(vendor: Path, source: dict[str, object]) -> None:
    _safe_vendor(vendor)
    receipt = _read_receipt(vendor)
    if receipt.get("repo") != source.get("repo"):
        raise ExternalRegistryError(f"{vendor} receipt repo does not match registry")
    if receipt.get("sha") != source.get("pin"):
        raise ExternalRegistryError(f"{vendor} receipt pin does not match registry")
    expected_suffixes = _expected_source_suffixes(source)
    suffix = receipt.get("src_path_suffix")
    if expected_suffixes and (not isinstance(suffix, str) or suffix not in expected_suffixes):
        raise ExternalRegistryError(f"{vendor} receipt source path does not match registry: {suffix!r}")
    license_path = _check_license(vendor, source, receipt)
    _check_payload(vendor, receipt, license_path)


def _consumer_paths(root: Path, source: dict[str, object]) -> None:
    consumers = source.get("consumers")
    if not isinstance(consumers, list) or not consumers or not all(
        isinstance(item, str) and item for item in consumers
    ):
        raise ExternalRegistryError(f"{source.get('repo')!r} has no named live consumers")
    aliases = _aliases(source)
    missing: list[str] = []
    for item in consumers:
        path = root / item
        if not path.exists():
            missing.append(item)
            continue
        if path.is_file() and not path.is_symlink():
            text = path.read_text(encoding="utf-8", errors="replace")
            if not any(alias in text for alias in aliases):
                missing.append(f"{item} (alias not referenced)")
    if missing:
        raise ExternalRegistryError(f"{source.get('repo')!r} names missing consumers: {missing}")


def check_external_skills(contract: Any) -> None:
    """Validate only external skill directories projected by this contract."""
    root, external = _root_from_contract(contract)
    registry = external / "registry.yaml"
    if registry.is_symlink() or not registry.is_file():
        raise ExternalRegistryError(f"{registry} is missing or symlinked")
    by_vendor = _registry_sources(registry, external)
    skills = Path(contract.surface("skills").source)
    skills_relative = skills.relative_to(root)
    first_party = _first_party_skill_links(root, skills)
    declared: dict[str, tuple[str, Path]] = {}
    for vendor_name, source in by_vendor.items():
        consumers = source.get("consumers")
        if not isinstance(consumers, list):
            continue
        names = _skill_names(source)
        vendor = external / vendor_name
        for item in consumers:
            if not isinstance(item, str):
                continue
            consumer = Path(item)
            if consumer.parent != skills_relative or consumer.name not in names:
                continue
            expected = vendor if len(names) == 1 else vendor / consumer.name
            declared[consumer.as_posix()] = (vendor_name, expected.resolve(strict=False))
    projected: set[str] = set()
    for entry in skills.iterdir():
        if not entry.is_symlink():
            continue
        relative = entry.relative_to(root).as_posix()
        if relative in first_party:
            continue
        declaration = declared.get(relative)
        if declaration is None:
            raise ExternalRegistryError(f"projected skill is not a declared registry consumer: {entry}")
        vendor_name, expected = declaration
        target = entry.resolve(strict=False)
        if target != expected:
            raise ExternalRegistryError(
                f"projected skill target drift for {entry}: expected {expected}, got {target}"
            )
        projected.add(vendor_name)
    for name in sorted(projected):
        _validate_vendor(external / name, by_vendor[name])


def check_external_registry_inventory(contract: Any) -> None:
    """Validate every committed vendor and every registry/consumer assertion."""
    root, external = _root_from_contract(contract)
    registry = external / "registry.yaml"
    if registry.is_symlink() or not registry.is_file():
        raise ExternalRegistryError(f"{registry} is missing or symlinked")
    by_vendor = _registry_sources(registry, external)
    expected = set(by_vendor)
    entries = {entry.name: entry for entry in external.iterdir()}
    allowed_files = {"registry.yaml", "README.md"}
    unexpected = sorted(
        name for name in entries if name not in expected and name not in allowed_files
    )
    if unexpected:
        raise ExternalRegistryError(f"{registry} has unexpected entries: {unexpected}")
    missing = sorted(
        name
        for name in expected
        if name not in entries or entries[name].is_symlink() or not entries[name].is_dir()
    )
    if missing:
        raise ExternalRegistryError(f"{registry} vendor inventory drift: missing={missing}")
    for name, source in sorted(by_vendor.items()):
        _consumer_paths(root, source)
        _validate_vendor(external / name, source)
