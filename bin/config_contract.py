from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROVENANCE_SCHEMA = "omp-config.provenance.v3"
THINKING_LEVELS = {"off", "minimal", "low", "medium", "high", "xhigh", "max", "auto"}


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class Surface:
    name: str
    source_rel: Path
    source: Path
    target_rel: Path
    target: Path
    kind: str
    origin: str


@dataclass(frozen=True)
class RuntimeCotenant:
    path_rel: Path
    owner: str


@dataclass(frozen=True)
class Contract:
    root: Path
    provenance: Path
    source_root: Path
    projection_root: Path
    projection_env: str
    projection_default: str
    install_mode: str
    surfaces: tuple[Surface, ...]
    excluded_runtime_state: tuple[Path, ...]
    runtime_cotenants: tuple[RuntimeCotenant, ...]
    bundled_agents: frozenset[str]
    upstream: dict[str, str]

    def surface(self, name: str) -> Surface:
        for surface in self.surfaces:
            if surface.name == name:
                return surface
        raise ContractError(f"provenance omits authority surface {name!r}")


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ContractError(f"{label} must be a mapping")
    return value


def _string(mapping: dict[str, Any], key: str, label: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ContractError(f"{label}.{key} must be a non-empty string")
    return value


def _relative_path(
    value: str,
    label: str,
    *,
    single_child: bool = False,
    max_parts: int | None = None,
    allow_root: bool = False,
) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or (path == Path(".") and not allow_root):
        raise ContractError(f"{label} must be a non-empty relative path")
    if single_child and len(path.parts) != 1:
        raise ContractError(f"{label} must be one direct child of the projection root")
    if max_parts is not None and len(path.parts) > max_parts:
        raise ContractError(f"{label} must have at most {max_parts} path segments")
    return path


def load_contract(root: Path, projection_root: Path | None = None) -> Contract:
    root = root.resolve()
    provenance = root / "provenance.yaml"
    if not provenance.is_file():
        raise ContractError("missing provenance.yaml")
    try:
        raw = json.loads(provenance.read_text())
    except json.JSONDecodeError as error:
        raise ContractError(f"provenance.yaml must use the JSON subset of YAML: {error}") from error
    document = _mapping(raw, "provenance")
    if document.get("schema_version") != PROVENANCE_SCHEMA:
        raise ContractError(f"provenance schema must be {PROVENANCE_SCHEMA}")

    authority = _mapping(document.get("authority"), "authority")
    repository = (root / _string(authority, "repository", "authority")).resolve()
    if repository != root:
        raise ContractError("authority.repository must resolve to this repository")
    source_root_rel = _relative_path(
        _string(authority, "source_root", "authority"),
        "authority.source_root",
        allow_root=True,
    )
    source_root = (root / source_root_rel).resolve()
    if not source_root.is_relative_to(root):
        raise ContractError("authority.source_root escapes the repository")

    projection = _mapping(document.get("projection"), "projection")
    projection_env = _string(projection, "environment", "projection")
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*", projection_env):
        raise ContractError("projection.environment must be an environment variable name")
    projection_default = _string(projection, "default", "projection")
    selected_projection = projection_root or Path(os.environ.get(projection_env, projection_default)).expanduser()
    selected_projection = selected_projection.resolve(strict=False)
    if selected_projection.is_relative_to(root) or root.is_relative_to(selected_projection):
        raise ContractError("projection root must not overlap the authority repository")
    install_mode = _string(projection, "mode", "projection")
    if install_mode != "symlink":
        raise ContractError(f"unsupported projection mode {install_mode!r}")

    declared_surfaces = _mapping(authority.get("surfaces"), "authority.surfaces")
    if not declared_surfaces:
        raise ContractError("authority.surfaces must not be empty")
    surfaces: list[Surface] = []
    target_paths: set[Path] = set()
    for name, value in declared_surfaces.items():
        if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ContractError(f"invalid authority surface name {name!r}")
        declaration = _mapping(value, f"authority.surfaces.{name}")
        source_rel = _relative_path(
            _string(declaration, "source", f"authority.surfaces.{name}"),
            f"authority.surfaces.{name}.source",
        )
        source = (root / source_rel).resolve(strict=False)
        if not source.is_relative_to(source_root):
            raise ContractError(f"authority surface {name!r} is outside authority.source_root")
        kind = _string(declaration, "kind", f"authority.surfaces.{name}")
        if kind not in {"file", "directory"}:
            raise ContractError(f"authority surface {name!r} has unsupported kind {kind!r}")
        target_rel = _relative_path(
            _string(declaration, "target", f"authority.surfaces.{name}"),
            f"authority.surfaces.{name}.target",
            single_child=kind == "directory",
            max_parts=2 if kind == "file" else None,
        )
        if target_rel in target_paths:
            raise ContractError(f"duplicate projection target {target_rel}")
        target_paths.add(target_rel)
        if not source.exists():
            raise ContractError(f"authority surface {name!r} is missing: {source_rel}")
        if kind == "file" and not source.is_file():
            raise ContractError(f"authority surface {name!r} must be a file")
        if kind == "directory" and not source.is_dir():
            raise ContractError(f"authority surface {name!r} must be a directory")
        surfaces.append(
            Surface(
                name=name,
                source_rel=source_rel,
                source=source,
                target_rel=target_rel,
                target=selected_projection / target_rel,
                kind=kind,
                origin=_string(declaration, "origin", f"authority.surfaces.{name}"),
            )
        )

    excluded_raw = document.get("excluded_runtime_state")
    if not isinstance(excluded_raw, list) or not all(isinstance(value, str) for value in excluded_raw):
        raise ContractError("excluded_runtime_state must be a string list")
    excluded = tuple(
        _relative_path(value, "excluded_runtime_state", single_child=True)
        for value in excluded_raw
    )
    if len(excluded) != len(set(excluded)):
        raise ContractError("excluded_runtime_state contains duplicates")
    for surface in surfaces:
        if any(surface.target_rel == excluded_path for excluded_path in excluded):
            raise ContractError(
                f"mutable runtime state selected for projection: {surface.target_rel}"
            )
        nested = any(
            len(surface.target_rel.parts) > len(excluded_path.parts)
            and surface.target_rel.parts[: len(excluded_path.parts)] == excluded_path.parts
            for excluded_path in excluded
        )
        if nested and surface.kind != "file":
            raise ContractError(
                f"only file surfaces may co-tenant excluded runtime state: {surface.target_rel}"
            )
        if surface.kind == "file" and len(surface.target_rel.parts) > 1 and not nested:
            raise ContractError(
                f"nested file surface must co-tenant excluded runtime state: {surface.target_rel}"
            )

    cotenants_raw = document.get("runtime_cotenants")
    if not isinstance(cotenants_raw, list):
        raise ContractError("runtime_cotenants must be a list")
    cotenants: list[RuntimeCotenant] = []
    cotenant_paths: set[Path] = set()
    excluded_names = {path.name for path in excluded}
    for index, value in enumerate(cotenants_raw):
        tenant = _mapping(value, f"runtime_cotenants[{index}]")
        path_rel = _relative_path(
            _string(tenant, "path", f"runtime_cotenants[{index}]"),
            f"runtime_cotenants[{index}].path",
            max_parts=2,
        )
        if len(path_rel.parts) < 2 or path_rel.parts[0] not in excluded_names:
            raise ContractError(
                f"runtime_cotenants[{index}].path must be inside excluded runtime state"
            )
        if path_rel in cotenant_paths:
            raise ContractError(f"duplicate runtime cotenant path {path_rel}")
        if path_rel in target_paths:
            raise ContractError(f"runtime cotenant overlaps authority surface {path_rel}")
        owner = _string(tenant, "owner", f"runtime_cotenants[{index}]")
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", owner):
            raise ContractError(f"runtime_cotenants[{index}].owner has invalid name {owner!r}")
        cotenant_paths.add(path_rel)
        cotenants.append(
            RuntimeCotenant(
                path_rel=path_rel,
                owner=owner,
            )
        )

    dependencies = _mapping(document.get("runtime_dependencies"), "runtime_dependencies")
    bundled_raw = dependencies.get("bundled_agents")
    if not isinstance(bundled_raw, list) or not all(
        isinstance(name, str) and re.fullmatch(r"[a-z][a-z0-9_-]*", name) for name in bundled_raw
    ):
        raise ContractError("runtime_dependencies.bundled_agents must be an agent-name list")
    if len(bundled_raw) != len(set(bundled_raw)):
        raise ContractError("runtime_dependencies.bundled_agents contains duplicates")

    upstream_raw = _mapping(document.get("upstream"), "upstream")
    upstream = {
        key: value
        for key, value in upstream_raw.items()
        if isinstance(key, str) and isinstance(value, str)
    }
    revision = upstream.get("revision", "")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ContractError("upstream.revision must be a 40-character lowercase Git revision")

    return Contract(
        root=root,
        provenance=provenance,
        source_root=source_root,
        projection_root=selected_projection,
        projection_env=projection_env,
        projection_default=projection_default,
        install_mode=install_mode,
        surfaces=tuple(surfaces),
        excluded_runtime_state=excluded,
        runtime_cotenants=tuple(cotenants),
        bundled_agents=frozenset(bundled_raw),
        upstream=upstream,
    )


def _frame(hasher: Any, value: bytes) -> None:
    hasher.update(len(value).to_bytes(8, "big"))
    hasher.update(value)


def digest_path(path: Path) -> str:
    if path.is_symlink():
        path = path.resolve(strict=True)
    if not path.exists():
        raise ContractError(f"cannot digest missing path {path}")
    if path.is_file():
        return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"
    if not path.is_dir():
        raise ContractError(f"cannot digest unsupported path type {path}")

    hasher = hashlib.sha256()
    _frame(hasher, b"directory")
    for entry in sorted(path.rglob("*"), key=lambda candidate: candidate.relative_to(path).as_posix()):
        _frame(hasher, entry.relative_to(path).as_posix().encode())
        if entry.is_symlink():
            _frame(hasher, b"symlink")
            _frame(hasher, os.readlink(entry).encode())
        elif entry.is_dir():
            _frame(hasher, b"directory")
        elif entry.is_file():
            _frame(hasher, b"file")
            _frame(hasher, hashlib.sha256(entry.read_bytes()).digest())
        else:
            raise ContractError(f"cannot digest unsupported path type {entry}")
    return f"sha256:{hasher.hexdigest()}"


def projection_receipts(contract: Contract) -> list[dict[str, object]]:
    digest_cache: dict[Path, str] = {}

    def cached_digest(path: Path) -> str:
        resolved = path.resolve(strict=True) if path.is_symlink() else path.resolve()
        if resolved not in digest_cache:
            digest_cache[resolved] = digest_path(path)
        return digest_cache[resolved]

    receipts: list[dict[str, object]] = []
    for surface in contract.surfaces:
        errors: list[str] = []
        source_digest = cached_digest(surface.source)
        target_digest: str | None = None
        link_target: str | None = None
        if not surface.target.is_symlink():
            errors.append("projection_mode_drift")
        else:
            try:
                resolved_target = surface.target.resolve(strict=True)
                link_target = str(resolved_target)
                if resolved_target != surface.source.resolve(strict=True):
                    errors.append("link_drift")
            except FileNotFoundError:
                errors.append("link_drift")
        if surface.target.exists():
            target_digest = cached_digest(surface.target)
        elif not surface.target.is_symlink():
            errors.append("projection_missing")
        if target_digest is not None and source_digest != target_digest:
            errors.append("digest_drift")
        receipts.append(
            {
                "name": surface.name,
                "source": str(surface.source),
                "target": str(surface.target),
                "kind": surface.kind,
                "origin": surface.origin,
                "link_target": link_target,
                "source_sha256": source_digest,
                "target_sha256": target_digest,
                "status": "ok" if not errors else "drift",
                "errors": errors,
            }
        )
    return receipts


def require_projection(contract: Contract) -> list[dict[str, object]]:
    receipts = projection_receipts(contract)
    failures = [
        f"{receipt['name']}: {', '.join(receipt['errors'])}"
        for receipt in receipts
        if receipt["errors"]
    ]
    if failures:
        raise ContractError("; ".join(failures))
    for path in contract.excluded_runtime_state:
        target = contract.projection_root / path
        if target.is_symlink():
            raise ContractError(f"mutable OMP state must not be symlinked: {target}")
    return receipts


def effective_config(contract: Contract) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="omp-config-source-") as temp:
        temp_root = Path(temp)
        for surface in contract.surfaces:
            target = temp_root / surface.target_rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(surface.source, target_is_directory=surface.kind == "directory")
        env = os.environ.copy()
        env.pop("PI_CONFIG_FILES", None)
        env[contract.projection_env] = str(temp_root)
        try:
            result = subprocess.run(
                ["omp", "config", "list", "--json"],
                cwd=contract.root,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
            )
        except FileNotFoundError as error:
            raise ContractError("OMP executable is not available on PATH") from error
        except subprocess.TimeoutExpired as error:
            raise ContractError("OMP config validation timed out") from error
        if result.returncode:
            detail = result.stderr.strip() or result.stdout.strip()
            raise ContractError(f"OMP rejected source configuration: {detail}")
        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise ContractError(f"OMP returned invalid config JSON: {error}") from error
        if not isinstance(parsed, dict):
            raise ContractError("OMP config output must be a mapping")
        return parsed


def config_value(config: dict[str, object], key: str) -> object:
    entry = config.get(key)
    if not isinstance(entry, dict) or "value" not in entry:
        raise ContractError(f"OMP config omitted {key}")
    return entry["value"]


def frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ContractError(f"{path} has no YAML frontmatter")
    try:
        raw, body = text[4:].split("\n---\n", 1)
    except ValueError as error:
        raise ContractError(f"{path} has unterminated frontmatter") from error
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        if not line or line[0].isspace() or line.startswith("#"):
            continue
        if ":" not in line:
            raise ContractError(f"{path} has malformed frontmatter line: {line}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip("'\"")
    return fields, body.strip()


def split_selector(selector: str, default_effort: str = "auto") -> tuple[str, str]:
    model, separator, suffix = selector.rpartition(":")
    if separator and suffix in THINKING_LEVELS:
        return model, suffix
    return selector, default_effort
