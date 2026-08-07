"""Public primitives shared by the committed-range review gate."""
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
RESULT_SCHEMA = "omp.review-result.v1"
PASS_SCHEMA = "omp.review-pass.v3"
RECEIPT_SCHEMA = "omp.review-receipt.v3"
PASS_DIRECTORY = Path(".omp/review-passes")
RECEIPT_RELATIVE = Path(".omp/review-receipt.json")
FREEZE_RELATIVE = Path(".omp/review-freeze.json")
PROTECTED_BRANCHES = {"main", "master"}
ZERO_OID = "0" * 40
OID_PATTERN = re.compile(r"^[0-9a-f]{40}$")
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
ACTOR_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.@+-]{1,127}$")
REVIEWERS = (
    "autoreview",
    "thermo-nuclear-review",
    "thermo-nuclear-code-quality-review",
    "ponytail",
)

REVIEW_SPECS: dict[str, dict[str, Any]] = {
    "autoreview": {
        "skill_path": Path("global/skills/autoreview/SKILL.md"),
        "vendor_path": Path("global/external/openclaw-autoreview/SKILL.md"),
        "payload_key": "SKILL.md",
    },
    "thermo-nuclear-review": {
        "skill_path": Path("global/skills/thermo-nuclear-review/SKILL.md"),
        "vendor_path": Path("global/external/cursor-thermos/thermo-nuclear-review/SKILL.md"),
        "payload_key": "thermo-nuclear-review/SKILL.md",
    },
    "thermo-nuclear-code-quality-review": {
        "skill_path": Path("global/skills/thermo-nuclear-code-quality-review/SKILL.md"),
        "vendor_path": Path("global/external/cursor-thermos/thermo-nuclear-code-quality-review/SKILL.md"),
        "payload_key": "thermo-nuclear-code-quality-review/SKILL.md",
    },
    "ponytail": {
        "skill_path": Path("global/skills/ponytail/SKILL.md"),
        "vendor_path": Path("global/external/dietrich-ponytail/SKILL.md"),
        "payload_key": "SKILL.md",
    },
}

OBSOLETE_SCHEMA_MESSAGE = (
    "obsolete review receipt/pass schema; run freeze, submit planned lanes, record, then verify"
)


class GateError(ValueError):
    """Fail-closed review protocol error."""


TRIVIAL_EXTENSIONS = {".adoc", ".md", ".mdx", ".rst", ".txt"}
TRIVIAL_FILENAMES = {"CHANGELOG", "CHANGELOG.md", "LICENSE", "NOTICE", "README", "README.md"}
TRIVIAL_CONFIG_FILENAMES = {".editorconfig"}
POLICY_ROOTS = (Path("global/agents"), Path("global/references"), Path("global/skills"))
POLICY_DIRECTORY_NAMES = frozenset({"bin", "config", "hooks", "routing", "scripts", "workflows"})
POLICY_FILENAMES_CASEFOLDED = frozenset(name.casefold() for name in {"AGENTS.md", "RULES.md", "SKILL.md"})

HIGH_STAKES_KEYWORDS = ("auth", "secret", "gate", "migration", "harness", "hook", "install")


def floor_plan(paths: list[str]) -> list[str]:
    """Compute the required minimum reviewer lanes based on changed file paths."""
    scope = review_scope(paths)
    if scope == "trivial":
        return []

    has_code = False
    has_high_stakes = False

    for raw in paths:
        path = Path(raw)
        ext = path.suffix.casefold()
        parts = [part.casefold() for part in path.parts]

        if any(kw in raw.casefold() for kw in HIGH_STAKES_KEYWORDS):
            has_high_stakes = True

        if ext in {".py", ".ts", ".js", ".sh", ".go", ".rs", ".mjs", ".cjs"} or "bin" in parts or "hooks" in parts:
            has_code = True

    lanes = ["autoreview"]
    if has_code:
        lanes.extend(["thermo-nuclear-review", "ponytail"])
        if has_high_stakes:
            lanes.append("thermo-nuclear-code-quality-review")
    else:
        lanes.append("thermo-nuclear-code-quality-review")

    seen: set[str] = set()
    result: list[str] = []
    for lane in lanes:
        if lane not in seen and lane in REVIEW_SPECS:
            seen.add(lane)
            result.append(lane)
    return result

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


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _identity_string(value: object, label: str, *, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise GateError(f"{label} must be a non-empty string of at most {maximum} characters")
    if any(ord(character) < 0x20 or ord(character) == 0x7F for character in value):
        raise GateError(f"{label} must not contain control characters")
    return value


def _review_spec(reviewer: str) -> dict[str, Any]:
    if reviewer not in REVIEW_SPECS:
        raise GateError(f"unknown canonical reviewer {reviewer!r}")
    return REVIEW_SPECS[reviewer]


def skill_identity(reviewer: str) -> dict[str, str]:
    """Resolve and attest one projected immutable leaf skill."""
    spec = _review_spec(reviewer)
    projected = (GATE_ROOT / Path(spec["skill_path"])).resolve(strict=True)
    vendor = (GATE_ROOT / Path(spec["vendor_path"])).resolve(strict=True)
    if not projected.is_file() or not vendor.is_file():
        raise GateError(f"canonical skill for {reviewer} is not a regular file")
    if projected != vendor:
        raise GateError(f"canonical skill for {reviewer} does not resolve to its declared vendor leaf")
    sync_path = next(
        (
            candidate / ".sync-meta.json"
            for candidate in (vendor.parent, vendor.parent.parent, vendor.parent.parent.parent)
            if (candidate / ".sync-meta.json").is_file()
        ),
        None,
    )
    if sync_path is None:
        raise GateError(f"{reviewer} canonical skill has no .sync-meta.json receipt")
    metadata = read_json(sync_path, f"{reviewer} skill sync metadata")
    payload_sha256 = mapping(metadata.get("payload_sha256"), f"{reviewer} skill payload_sha256")
    payload_key = str(spec["payload_key"])
    expected_hex = payload_sha256.get(payload_key)
    if not isinstance(expected_hex, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hex):
        raise GateError(f"{reviewer} skill sync metadata has no valid payload digest for {payload_key}")
    actual = hashlib.sha256(projected.read_bytes()).hexdigest()
    if actual != expected_hex:
        raise GateError(f"{reviewer} canonical skill bytes do not match its pinned payload digest")
    source_repo = _identity_string(metadata.get("repo"), f"{reviewer} skill source repo")
    source_commit = _identity_string(metadata.get("sha"), f"{reviewer} skill source commit", maximum=64)
    source_path = Path(spec["vendor_path"]).as_posix()
    return {
        "name": reviewer,
        "path": Path(spec["skill_path"]).as_posix(),
        "sha256": f"sha256:{actual}",
        "source_repo": source_repo,
        "source_commit": source_commit,
        "source_path": source_path,
    }


def worker_attribution(actor: object, harness: object, model: object, run_id: object) -> dict[str, str]:
    """Validate explicit worker identity without choosing a provider or harness."""
    if not isinstance(actor, str) or not ACTOR_PATTERN.fullmatch(actor):
        raise GateError("worker actor must match the bounded actor syntax")
    return {
        "actor": actor,
        "harness": _identity_string(harness, "worker harness"),
        "model": _identity_string(model, "worker model"),
        "run_id": _identity_string(run_id, "worker run_id"),
    }
