"""Public primitives shared by the committed-range review gate and runner."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GATE_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_SCHEMA = "omp.review-bundle.v2"
FREEZE_SCHEMA = "omp.review-freeze.v2"
PASS_SCHEMA = "omp.review-pass.v2"
RECEIPT_SCHEMA = "omp.review-receipt.v2"
SCHEMA = RECEIPT_SCHEMA
PASS_DIRECTORY = Path(".omp/review-passes")
RECEIPT_RELATIVE = Path(".omp/review-receipt.json")
FREEZE_RELATIVE = Path(".omp/review-freeze.json")
PROTECTED_BRANCHES = {"main", "master"}
ZERO_OID = "0" * 40
OID_PATTERN = re.compile(r"^[0-9a-f]{40}$")
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
REVIEWERS = (
    "autoreview",
    "thermo-nuclear-review",
    "thermo-nuclear-code-quality-review",
)
PINNED_WORKERS = {
    "autoreview": (
        GATE_ROOT / "global" / "skills" / "autoreview" / "scripts" / "autoreview",
        GATE_ROOT / "global" / "external" / "openclaw-autoreview",
    ),
    "thermo-nuclear-review": (
        Path.home() / ".local" / "bin" / "cursor-agent",
        GATE_ROOT / "global" / "external" / "cursor-thermos",
    ),
    "thermo-nuclear-code-quality-review": (
        Path.home() / ".local" / "bin" / "cursor-agent",
        GATE_ROOT / "global" / "external" / "cursor-thermos",
    ),
}


class GateError(ValueError):
    """Fail-closed review protocol error."""


TRIVIAL_EXTENSIONS = {".adoc", ".md", ".mdx", ".rst", ".txt"}
TRIVIAL_FILENAMES = {"CHANGELOG", "CHANGELOG.md", "LICENSE", "NOTICE", "README", "README.md"}
TRIVIAL_CONFIG_FILENAMES = {".editorconfig"}
POLICY_ROOTS = (Path("global/agents"), Path("global/references"), Path("global/skills"))
POLICY_DIRECTORY_NAMES = frozenset({"bin", "config", "hooks", "routing", "scripts", "workflows"})
POLICY_FILENAMES_CASEFOLDED = frozenset(name.casefold() for name in {"AGENTS.md", "RULES.md", "SKILL.md"})


def _is_policy_path(path: Path) -> bool:
    normalized = Path(*(part.casefold() for part in path.parts))
    return (
        normalized.name in POLICY_FILENAMES_CASEFOLDED
        or any(root == normalized or root in normalized.parents for root in POLICY_ROOTS)
        or any(part in POLICY_DIRECTORY_NAMES for part in normalized.parts)
    )


def review_scope(paths: list[str]) -> str:
    if not paths:
        return "substantive"
    for raw in paths:
        path = Path(raw)
        if _is_policy_path(path):
            return "substantive"
        if path.name in TRIVIAL_FILENAMES or path.name in TRIVIAL_CONFIG_FILENAMES or path.suffix.lower() in TRIVIAL_EXTENSIONS:
            continue
        return "substantive"
    return "trivial"


def mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise GateError(f"{label} must be an object")
    return value


def nonnegative_int(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise GateError(f"{label} must be a non-negative integer")
    return value


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        return mapping(json.loads(path.read_text(encoding="utf-8")), label)
    except OSError as error:
        raise GateError(f"cannot read {label}: {error}") from error
    except json.JSONDecodeError as error:
        raise GateError(f"{label} is not JSON: {error}") from error


def sha256_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def directory_digest(path: Path) -> str:
    digest = hashlib.sha256()
    entries = sorted(
        (entry for entry in path.rglob("*") if entry.is_file()),
        key=lambda entry: entry.relative_to(path).as_posix(),
    )
    for entry in entries:
        digest.update(entry.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(entry.read_bytes())
    return f"sha256:{digest.hexdigest()}"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(document, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def confined_path(repo: Path, value: str | None, default: Path, label: str) -> Path:
    raw = value or os.environ.get("OMP_REVIEW_" + label.upper().replace("-", "_")) or str(default)
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = repo / path
    path = path.resolve(strict=False)
    if not path.is_relative_to(repo.resolve()):
        raise GateError(f"{label} must stay inside the reviewed repository")
    return path


def worker_display_path(path: Path) -> str:
    resolved = path.resolve(strict=False)
    try:
        return resolved.relative_to(GATE_ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def worker_path(value: str, label: str, reviewer: str, *, directory: bool) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = GATE_ROOT / candidate
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise GateError(f"{label} worker path is unavailable: {candidate}") from error
    expected = PINNED_WORKERS.get(reviewer)
    if expected is None:
        raise GateError(f"{label} has no pinned worker registry entry for {reviewer}")
    expected_path = expected[1 if directory else 0].resolve(strict=True)
    if resolved != expected_path:
        raise GateError(f"{label} worker path is not the pinned registry path: {resolved}")
    if directory:
        if not resolved.is_dir():
            raise GateError(f"{label} worker payload is not a directory: {resolved}")
    elif not resolved.is_file():
        raise GateError(f"{label} worker executable is not a regular file: {resolved}")
    return resolved


def worker_identity(reviewer: str, executable: Path, model: str, payload: Path) -> dict[str, Any]:
    executable = executable.resolve(strict=True)
    payload = payload.resolve(strict=True)
    if not executable.is_file():
        raise GateError(f"{reviewer} executable is not a regular file: {executable}")
    if not payload.is_dir():
        raise GateError(f"{reviewer} payload is not a directory: {payload}")
    return {
        "principal": reviewer,
        "harness": "openclaw-autoreview" if reviewer == "autoreview" else "cursor-agent",
        "model": model,
        "executable": worker_display_path(executable),
        "executable_sha256": sha256_bytes(executable.read_bytes()),
        "payload": worker_display_path(payload),
        "payload_sha256": directory_digest(payload),
    }


def unresolved_worker(reviewer: str, model: str, executable: str, payload: Path) -> dict[str, Any]:
    marker = f"unresolved:{reviewer}:{executable}".encode("utf-8")
    return {
        "principal": reviewer,
        "harness": "openclaw-autoreview" if reviewer == "autoreview" else "cursor-agent",
        "model": model,
        "executable": executable,
        "executable_sha256": sha256_bytes(marker),
        "payload": worker_display_path(payload),
        "payload_sha256": sha256_bytes(f"unresolved:{payload}".encode("utf-8")),
    }
