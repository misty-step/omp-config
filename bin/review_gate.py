#!/usr/bin/env python3
"""Fail-closed committed-range review and protected-push gate.

The closeout flow freezes one exact Git range before reviewers run. Reviewer
passes and the final receipt carry that frozen bundle identity. Protected-push
verification recomputes the identity from Git objects and history, never from
current worktree bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BUNDLE_SCHEMA = "omp.review-bundle.v2"
FREEZE_SCHEMA = "omp.review-freeze.v2"
PASS_SCHEMA = "omp.review-pass.v2"
PASS_DIRECTORY = Path(".omp/review-passes")
GATE_ROOT = Path(__file__).resolve().parents[1]
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
RECEIPT_SCHEMA = "omp.review-receipt.v2"
SCHEMA = RECEIPT_SCHEMA
REVIEWERS = (
    "autoreview",
    "thermo-nuclear-review",
    "thermo-nuclear-code-quality-review",
)
RECEIPT_RELATIVE = Path(".omp/review-receipt.json")
FREEZE_RELATIVE = Path(".omp/review-freeze.json")
PROTECTED_BRANCHES = {"main", "master"}
ZERO_OID = "0" * 40
TRIVIAL_EXTENSIONS = {
    ".adoc",
    ".md",
    ".mdx",
    ".rst",
    ".txt",
}
TRIVIAL_FILENAMES = {
    "CHANGELOG",
    "CHANGELOG.md",
    "LICENSE",
    "NOTICE",
    "README",
    "README.md",
}
TRIVIAL_CONFIG_FILENAMES = {".editorconfig", ".gitignore"}
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.@+-]{1,127}$")
OID_PATTERN = re.compile(r"^[0-9a-f]{40}$")
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
POLICY_ROOTS = (
    Path("global/agents"),
    Path("global/references"),
    Path("global/skills"),
)
POLICY_DIRECTORY_NAMES = frozenset({"bin", "config", "hooks", "routing", "scripts", "workflows"})
POLICY_FILENAMES = frozenset({"AGENTS.md", "RULES.md", "SKILL.md"})
POLICY_FILENAMES_CASEFOLDED = frozenset(name.casefold() for name in POLICY_FILENAMES)



class GateError(ValueError):
    pass


def _run_git(repo: Path, *args: str, input_text: str | None = None) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as error:
        raise GateError(f"git {' '.join(args)} could not run: {error}") from error
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise GateError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout

def _probe_git(repo: Path, *args: str) -> str | None:
    """Return successful Git output without turning optional metadata into an error."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError:
        return None
    if result.returncode:
        return None
    value = result.stdout.strip()
    return value or None


def repo_root(path: str | Path | None) -> Path:
    candidate = Path(path or os.environ.get("OMP_REVIEW_REPOSITORY", ".")).expanduser().resolve()
    try:
        raw_root = _run_git(candidate, "rev-parse", "--show-toplevel").strip()
    except (GateError, OSError) as error:
        raise GateError(f"not a Git worktree: {candidate}") from error
    if not raw_root:
        raise GateError(f"Git did not report a worktree root: {candidate}")
    resolved = Path(raw_root).resolve()
    if not resolved.is_dir():
        raise GateError(f"Git worktree root is not a directory: {resolved}")
    return resolved


def _confined_path(repo: Path, value: str | None, default: Path, label: str) -> Path:
    raw = value or os.environ.get("OMP_REVIEW_" + label.upper().replace("-", "_")) or str(default)
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = repo / path
    path = path.resolve(strict=False)
    if not path.is_relative_to(repo.resolve()):
        raise GateError(f"{label} must stay inside the reviewed repository")
    return path


def receipt_path(repo: Path, value: str | None = None) -> Path:
    return _confined_path(repo, value, RECEIPT_RELATIVE, "receipt")


def freeze_path(repo: Path, value: str | None = None) -> Path:
    return _confined_path(repo, value, FREEZE_RELATIVE, "freeze")


def _path_from_git(raw: str) -> Path:
    if not raw:
        raise GateError("Git reported an empty changed path")
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts or path == Path("."):
        raise GateError(f"Git reported an unsafe changed path: {raw!r}")
    return path


def _oid(value: object, label: str, *, allow_zero: bool = False) -> str:
    if value == ZERO_OID and not allow_zero:
        raise GateError(f"{label} cannot be the zero object id")
    if not isinstance(value, str) or not OID_PATTERN.fullmatch(value):
        raise GateError(f"{label} must be a 40-character lowercase Git object id")
    return value


def _validate_commit_object(repo: Path, oid: str, label: str) -> tuple[str, list[str]]:
    _oid(oid, label)
    raw = _run_git(repo, "cat-file", "-p", f"{oid}^{{commit}}")
    tree_oid: str | None = None
    parents: list[str] = []
    for line in raw.splitlines():
        if line.startswith("tree "):
            tree_oid = line[5:].strip()
        elif line.startswith("parent "):
            parent = line[7:].strip()
            _oid(parent, f"{label} parent")
            parents.append(parent)
    if tree_oid is None:
        raise GateError(f"Git commit {oid} has no tree object")
    _oid(tree_oid, f"{label} tree")
    _run_git(repo, "cat-file", "-e", f"{tree_oid}^{{tree}}")
    return tree_oid, parents


def _validate_tree_contents(repo: Path, commit: str) -> None:
    raw = _run_git(repo, "ls-tree", "-r", "-t", "-z", commit, "--")
    expected_objects: list[tuple[str, str]] = []
    for record in raw.split("\0"):
        if not record:
            continue
        try:
            metadata, path_text = record.split("\t", 1)
        except ValueError as error:
            raise GateError(f"Git returned malformed tree data for {commit}") from error
        fields = metadata.split()
        if len(fields) != 3:
            raise GateError(f"Git returned malformed tree metadata for {commit}")
        mode, object_type, object_id = fields
        _oid(object_id, f"{commit} tree entry")
        _path_from_git(path_text)
        if object_type in {"blob", "tree"}:
            expected_objects.append((object_id, object_type))
        elif object_type == "commit" and mode != "160000":
            raise GateError(f"Git returned unsupported tree entry type {object_type!r}")
    if not expected_objects:
        return
    batch_input = "".join(f"{object_id}\n" for object_id, _ in expected_objects)
    checked = _run_git(
        repo,
        "cat-file",
        "--batch-check=%(objectname) %(objecttype)",
        input_text=batch_input,
    ).splitlines()
    if len(checked) != len(expected_objects):
        raise GateError(f"Git returned incomplete object metadata for {commit}")
    for line, (expected_id, expected_type) in zip(checked, expected_objects, strict=True):
        if line != f"{expected_id} {expected_type}":
            raise GateError(f"Git returned invalid {expected_type} object metadata for {expected_id}")


def _introduced_commits(repo: Path, old_oid: str, new_oid: str) -> list[str]:
    revision = new_oid if old_oid == ZERO_OID else f"{old_oid}..{new_oid}"
    raw = _run_git(repo, "rev-list", "--reverse", "--topo-order", revision)
    commits: list[str] = []
    for line in raw.splitlines():
        commit = line.strip()
        if not commit:
            continue
        _oid(commit, "introduced commit")
        commits.append(commit)
    if len(commits) != len(set(commits)):
        raise GateError("Git returned duplicate introduced commits")
    return commits


def _paths_for_commit(repo: Path, commit: str) -> set[Path]:
    raw = _run_git(
        repo,
        "diff-tree",
        "--root",
        "--name-only",
        "-z",
        "-r",
        "--no-commit-id",
        "--no-renames",
        "-m",
        commit,
    )
    paths: set[Path] = set()
    for item in raw.split("\0"):
        if item:
            paths.add(_path_from_git(item))
    return paths


def _bundle_digest(identity: dict[str, Any]) -> str:
    canonical = json.dumps(
        {"schema": BUNDLE_SCHEMA, **identity},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(canonical).hexdigest()}"


def _worktree_is_dirty_for_paths(repo: Path, new_oid: str, paths: list[Path]) -> None:
    if not paths:
        return
    path_args = [f":(literal){path.as_posix()}" for path in paths]
    changed = _run_git(repo, "diff", "--no-ext-diff", "--name-only", "-z", new_oid, "--", *path_args)
    if changed:
        raise GateError("review freeze requires a clean worktree for every frozen path")
    status = _run_git(
        repo,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
        "--ignored=matching",
        "--",
        *path_args,
    )
    if status:
        raise GateError("review freeze requires a clean worktree for every frozen path")


def _bundle_from_git(repo: Path, old_oid: str, new_oid: str, *, check_worktree: bool) -> dict[str, Any]:
    old_oid = _oid(old_oid, "old_oid", allow_zero=True)
    new_oid = _oid(new_oid, "new_oid")
    if old_oid == new_oid:
        raise GateError("review range must introduce at least one commit")
    shallow = _run_git(repo, "rev-parse", "--is-shallow-repository").strip()
    if shallow not in {"true", "false"}:
        raise GateError("Git returned an invalid shallow-repository state")
    if shallow == "true":
        raise GateError("review range cannot be frozen or verified in a shallow repository")
    _validate_commit_object(repo, new_oid, "new_oid")
    if old_oid != ZERO_OID:
        _validate_commit_object(repo, old_oid, "old_oid")
    commits = _introduced_commits(repo, old_oid, new_oid)
    if not commits:
        raise GateError("Git range contains no introduced commits")
    paths: set[Path] = set()
    for commit in commits:
        _validate_commit_object(repo, commit, f"introduced commit {commit}")
        _validate_tree_contents(repo, commit)
        paths.update(_paths_for_commit(repo, commit))
    path_list = sorted(paths, key=lambda item: item.as_posix())
    identity: dict[str, Any] = {
        "repository": str(repo),
        "old_oid": old_oid,
        "new_oid": new_oid,
        "commits": commits,
        "paths": [path.as_posix() for path in path_list],
    }
    identity["bundle_digest"] = _bundle_digest(identity)
    if check_worktree:
        _worktree_is_dirty_for_paths(repo, new_oid, path_list)
    return identity


def _identity_from_document(document: dict[str, Any], label: str) -> dict[str, Any]:
    repository = document.get("repository")
    old_oid = document.get("old_oid")
    new_oid = document.get("new_oid")
    commits = document.get("commits")
    paths = document.get("paths")
    digest = document.get("bundle_digest")
    if not isinstance(repository, str) or not repository:
        raise GateError(f"{label}.repository must be a non-empty string")
    _oid(old_oid, f"{label}.old_oid", allow_zero=True)
    _oid(new_oid, f"{label}.new_oid")
    if not isinstance(commits, list) or not all(isinstance(item, str) and OID_PATTERN.fullmatch(item) for item in commits):
        raise GateError(f"{label}.commits must be an ordered list of Git object ids")
    if len(commits) != len(set(commits)) or not commits:
        raise GateError(f"{label}.commits must contain unique introduced commits")
    if not isinstance(paths, list) or not all(isinstance(item, str) for item in paths):
        raise GateError(f"{label}.paths must be a list of repository-relative paths")
    normalized_paths = [_path_from_git(item).as_posix() for item in paths]
    if normalized_paths != sorted(set(normalized_paths)):
        raise GateError(f"{label}.paths must be sorted and unique")
    if not isinstance(digest, str) or not DIGEST_PATTERN.fullmatch(digest):
        raise GateError(f"{label}.bundle_digest must be a sha256 digest")
    identity = {
        "repository": repository,
        "old_oid": old_oid,
        "new_oid": new_oid,
        "commits": list(commits),
        "paths": normalized_paths,
        "bundle_digest": digest,
    }
    if _bundle_digest({key: identity[key] for key in ("repository", "old_oid", "new_oid", "commits", "paths")}) != digest:
        raise GateError(f"{label}.bundle_digest does not match its canonical identity")
    return identity


def _assert_same_identity(expected: dict[str, Any], actual: dict[str, Any], label: str) -> None:
    if expected != actual:
        raise GateError(f"{label} does not match the recomputed committed-range bundle")


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise GateError(f"{label} must be an object")
    return value


def _nonnegative_int(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise GateError(f"{label} must be a non-negative integer")
    return value


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        return _mapping(json.loads(path.read_text(encoding="utf-8")), label)
    except OSError as error:
        raise GateError(f"cannot read {label}: {error}") from error
    except json.JSONDecodeError as error:
        raise GateError(f"{label} is not JSON: {error}") from error


def _load_freeze(repo: Path, path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    document = _read_json(path, f"review freeze {path}")
    if document.get("schema") != FREEZE_SCHEMA or document.get("kind") != "freeze":
        raise GateError(f"review freeze must declare schema {FREEZE_SCHEMA}")
    identity = _identity_from_document(document, "review freeze")
    if identity["repository"] != str(repo):
        raise GateError("review freeze belongs to a different repository")
    return document, identity


def _sha256_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _directory_digest(path: Path) -> str:
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


def _gate_pass_path(repo: Path, path: Path, reviewer: str) -> Path:
    expected = (repo / PASS_DIRECTORY / f"{reviewer}.json").resolve()
    actual = path.expanduser().resolve(strict=False)
    if actual != expected:
        raise GateError(
            f"review pass {path} is not the gate-owned artifact {expected.relative_to(repo).as_posix()}"
        )
    if not actual.is_file():
        raise GateError(f"missing gate-owned review pass artifact {actual}")
    return actual


def _worker_path(value: str, label: str, reviewer: str, *, directory: bool) -> Path:
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


def _audit_worker(
    document: dict[str, Any],
    label: str,
    repo: Path,
    reviewer: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    worker = _mapping(document.get("worker"), f"{label}.worker")
    for field in ("principal", "harness", "model", "executable", "payload"):
        value = worker.get(field)
        if not isinstance(value, str) or not value:
            raise GateError(f"{label}.worker.{field} must be a non-empty string")
    for field in ("executable_sha256", "payload_sha256"):
        value = worker.get(field)
        if not isinstance(value, str) or not DIGEST_PATTERN.fullmatch(value):
            raise GateError(f"{label}.worker.{field} must be a sha256 digest")
    if "resolved" in worker:
        raise GateError(f"{label}.worker.resolved is not a supported attestation field")
    if worker["principal"] != reviewer:
        raise GateError(f"{label}.worker.principal must identify {reviewer}")
    executable = _worker_path(worker["executable"], label, reviewer, directory=False)
    payload = _worker_path(worker["payload"], label, reviewer, directory=True)
    executable_digest = _sha256_bytes(executable.read_bytes())
    if executable_digest != worker["executable_sha256"]:
        raise GateError(f"{label}.worker.executable_sha256 does not match the pinned executable")
    payload_digest = _directory_digest(payload)
    if payload_digest != worker["payload_sha256"]:
        raise GateError(f"{label}.worker.payload_sha256 does not match the pinned payload")
    raw_report = _mapping(document.get("raw_report"), f"{label}.raw_report")
    return worker, raw_report


def _pass_artifact(repo: Path, path: Path, reviewer: str) -> dict[str, str]:
    artifact = _gate_pass_path(repo, path, reviewer)
    return {
        "path": artifact.relative_to(repo).as_posix(),
        "sha256": _sha256_bytes(artifact.read_bytes()),
    }


def _pass_document(
    path: Path,
    expected: str,
    identity: dict[str, Any],
    *,
    repo: Path,
    exit_code: int | None = None,
) -> dict[str, Any]:
    document = _read_json(path, f"review pass {path}")
    if document.get("schema") != PASS_SCHEMA:
        raise GateError(f"review pass {path} must declare schema {PASS_SCHEMA}")
    pass_identity = _identity_from_document(document, f"review pass {path}")
    _assert_same_identity(pass_identity, identity, f"review pass {path}")
    if document.get("reviewer") != expected:
        raise GateError(f"review pass {path} is for {document.get('reviewer')!r}, expected {expected!r}")
    worker, raw_report = _audit_worker(document, f"review pass {path}", repo, expected)
    status = document.get("status")
    if status not in {"clean", "findings", "unavailable", "failed"}:
        raise GateError(f"review pass {path} has unsupported status {status!r}")
    findings = _nonnegative_int(document.get("actionable_findings"), f"{path}.actionable_findings")
    actual_exit = document.get("exit_code")
    if not isinstance(actual_exit, int) or isinstance(actual_exit, bool):
        raise GateError(f"{path}.exit_code must be an integer")
    if exit_code is not None and actual_exit != exit_code:
        raise GateError(f"{path}.exit_code does not match --autoreview-exit")
    result = {
        **identity,
        "schema": PASS_SCHEMA,
        "reviewer": expected,
        "status": status,
        "actionable_findings": findings,
        "exit_code": actual_exit,
        "worker": worker,
        "raw_report": raw_report,
    }
    if isinstance(document.get("raw_report_path"), str):
        result["raw_report_path"] = document["raw_report_path"]
    result["pass_artifact"] = _pass_artifact(repo, path, expected)
    return result




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


def _is_policy_path(path: Path) -> bool:
    normalized = Path(*(part.casefold() for part in path.parts))
    return (
        normalized.name in POLICY_FILENAMES_CASEFOLDED
        or any(root == normalized or root in normalized.parents for root in POLICY_ROOTS)
        or any(part in POLICY_DIRECTORY_NAMES for part in normalized.parts)
    )


def _scope(paths: list[str]) -> str:
    if not paths:
        return "substantive"
    for raw in paths:
        path = Path(raw)
        if _is_policy_path(path):
            return "substantive"
        name = path.name
        suffix = path.suffix.lower()
        if name in TRIVIAL_FILENAMES or name in TRIVIAL_CONFIG_FILENAMES or suffix in TRIVIAL_EXTENSIONS:
            continue
        return "substantive"
    return "trivial"


def classify(paths: list[Path]) -> str:
    return _scope([path.as_posix() for path in paths])


def _clean_passes(passes: list[dict[str, Any]]) -> None:
    for item in passes:
        if item["status"] == "unavailable":
            raise GateError(
                f"reviewer {item['reviewer']} is unavailable; install/authenticate the reviewer and rerun review_gate.py run"
            )
        if item["actionable_findings"] != 0:
            raise GateError(f"reviewer {item['reviewer']} reported actionable findings; fix them and rerun review_gate.py run")
        if item["status"] != "clean" or item["exit_code"] != 0:
            raise GateError(f"reviewer {item['reviewer']} did not produce a clean pass; rerun review_gate.py run")


def freeze(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    output = freeze_path(repo, args.output)
    identity = _bundle_from_git(repo, args.old_oid, args.new_oid, check_worktree=True)
    document = {
        "schema": FREEZE_SCHEMA,
        "kind": "freeze",
        **identity,
        "created_at": now(),
        "freeze_path": output.relative_to(repo).as_posix(),
    }
    write_json(output, document)
    print(f"review freeze written: {output}")
    return 0


def record(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    freeze_file = freeze_path(repo, args.freeze)
    _, frozen = _load_freeze(repo, freeze_file)
    current = _bundle_from_git(repo, frozen["old_oid"], frozen["new_oid"], check_worktree=True)
    _assert_same_identity(frozen, current, "review freeze")
    if args.autoreview_json is None or args.autoreview_exit is None:
        raise GateError("record requires --autoreview-json and --autoreview-exit")
    passes = [
        _pass_document(args.autoreview_json, "autoreview", frozen, repo=repo, exit_code=args.autoreview_exit),
        _pass_document(args.thermo_correctness_json, "thermo-nuclear-review", frozen, repo=repo),
        _pass_document(args.thermo_quality_json, "thermo-nuclear-code-quality-review", frozen, repo=repo),
    ]
    _clean_passes(passes)
    actual_scope = _scope(frozen["paths"])
    if args.scope != actual_scope and not (args.scope == "substantive" and actual_scope == "trivial"):
        raise GateError(f"requested scope {args.scope!r} does not match frozen changed scope {actual_scope!r}")
    output = receipt_path(repo, args.output)
    document = {
        "schema": RECEIPT_SCHEMA,
        "kind": "review",
        **frozen,
        "scope": "substantive",
        "created_at": now(),
        "freeze_manifest": freeze_file.relative_to(repo).as_posix(),
        "reviewers": passes,
        "actionable_findings": sum(item["actionable_findings"] for item in passes),
        "protocol": {
            "freeze": "committed Git range and complete introduced history",
            "autoreview": "structured helper pass bound to the frozen bundle",
            "thermos": "independent Thermos passes bound to the frozen bundle",
            "pass_artifacts": "gate-owned JSON files under .omp/review-passes, digest-bound and re-read at verification",
            "worker_attestation": "live SHA-256 hashes of each pinned executable and recursive payload are checked at record and verify",
            "local_boundary": "pre-push integrity proof, not signer identity or host/root compromise proof",
        },
    }
    write_json(output, document)
    print(f"review receipt written: {output}")
    return 0


def waive(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    freeze_file = freeze_path(repo, args.freeze)
    _, frozen = _load_freeze(repo, freeze_file)
    current = _bundle_from_git(repo, frozen["old_oid"], frozen["new_oid"], check_worktree=True)
    _assert_same_identity(frozen, current, "review freeze")
    if _scope(frozen["paths"]) != "trivial":
        raise GateError("trivial waiver is allowed only for inert prose/config-only changes")
    reason = args.reason.strip()
    actor = args.actor.strip()
    if len(reason) < 12 or not any(word in reason.lower() for word in ("prose", "config", "documentation")):
        raise GateError("waiver reason must explain why the prose/config change is trivial")
    if not NAME_PATTERN.fullmatch(actor):
        raise GateError("waiver actor must be a stable name or email-like identifier")
    output = receipt_path(repo, args.output)
    document = {
        "schema": RECEIPT_SCHEMA,
        "kind": "waiver",
        **frozen,
        "scope": "trivial",
        "created_at": now(),
        "freeze_manifest": freeze_file.relative_to(repo).as_posix(),
        "waiver": {
            "actor": actor,
            "reason": reason,
            "recorded_at": now(),
        },
        "protocol": "explicit trivial prose/config waiver bound to a frozen committed range",
    }
    write_json(output, document)
    print(f"trivial review waiver written: {output}")
    return 0


def _load_receipt(repo: Path, output: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    document = _read_json(output, f"review receipt {output}")
    if document.get("schema") != RECEIPT_SCHEMA:
        raise GateError(f"review receipt must declare schema {RECEIPT_SCHEMA}")
    identity = _identity_from_document(document, "review receipt")
    if identity["repository"] != str(repo):
        raise GateError("review receipt belongs to a different repository")
    return document, identity


def _verify_receipt(repo: Path, document: dict[str, Any], identity: dict[str, Any]) -> None:
    _assert_same_identity(_identity_from_document(document, "review receipt"), identity, "review receipt")
    scope = document.get("scope")
    if scope not in {"trivial", "substantive"}:
        raise GateError("review receipt has unsupported scope")
    kind = document.get("kind")
    actual_scope = _scope(identity["paths"])
    if kind == "waiver":
        waiver = _mapping(document.get("waiver"), "review receipt waiver")
        actor = waiver.get("actor")
        reason = waiver.get("reason")
        if not isinstance(actor, str) or not NAME_PATTERN.fullmatch(actor):
            raise GateError("review receipt waiver has no valid actor")
        if not isinstance(reason, str) or len(reason.strip()) < 12:
            raise GateError("review receipt waiver has no auditable reason")
        if actual_scope != "trivial" or scope != "trivial":
            raise GateError("trivial waiver cannot authorize substantive policy or code changes")
        return
    if kind != "review":
        raise GateError("review receipt kind must be review or waiver")
    if actual_scope == "substantive" and scope != "substantive":
        raise GateError("substantive changes require a substantive review receipt")
    reviewers = document.get("reviewers")
    if not isinstance(reviewers, list) or len(reviewers) != len(REVIEWERS):
        raise GateError(
            "final receipt must contain autoreview plus both independent Thermos passes; "
            "rerun review_gate.py run to record all three structured pass receipts"
        )
    names: list[str] = []
    for item in reviewers:
        entry = _mapping(item, "reviewer receipt")
        reviewer = entry.get("reviewer")
        if not isinstance(reviewer, str):
            raise GateError("reviewer receipt reviewer must be a string")
        names.append(reviewer)
        _assert_same_identity(_identity_from_document(entry, "reviewer receipt"), identity, "reviewer receipt")
        artifact = _mapping(entry.get("pass_artifact"), f"reviewer receipt {reviewer}.pass_artifact")
        artifact_path = artifact.get("path")
        expected_path = (PASS_DIRECTORY / f"{reviewer}.json").as_posix()
        if artifact_path != expected_path:
            raise GateError(f"reviewer receipt {reviewer} is not bound to its gate-owned pass artifact")
        artifact_digest = artifact.get("sha256")
        if not isinstance(artifact_digest, str) or not DIGEST_PATTERN.fullmatch(artifact_digest):
            raise GateError(f"reviewer receipt {reviewer}.pass_artifact.sha256 must be a sha256 digest")
        pass_path = _gate_pass_path(repo, repo / artifact_path, reviewer)
        actual_digest = _sha256_bytes(pass_path.read_bytes())
        if actual_digest != artifact_digest:
            raise GateError(f"reviewer receipt {reviewer} pass artifact changed after record")
        pass_document = _pass_document(pass_path, reviewer, identity, repo=repo)
        embedded = dict(entry)
        embedded.pop("pass_artifact", None)
        pass_document.pop("pass_artifact", None)
        if embedded != pass_document:
            raise GateError(f"reviewer receipt {reviewer} does not match its gate-owned pass artifact")
        status = entry.get("status")
        findings = entry.get("actionable_findings")
        if status != "clean" or findings != 0 or entry.get("exit_code") != 0:
            if status == "unavailable":
                raise GateError(
                    f"reviewer {reviewer} is unavailable; install/authenticate the reviewer and rerun review_gate.py run"
                )
            if findings != 0:
                raise GateError(f"reviewer {reviewer} reported accepted actionable findings; fix them and rerun review_gate.py run")
            raise GateError(f"reviewer {reviewer} did not produce a clean pass; rerun review_gate.py run")
    if set(names) != set(REVIEWERS):
        raise GateError(
            "final receipt must contain autoreview plus both independent Thermos passes; "
            "rerun review_gate.py run to record all three structured pass receipts"
        )


def verify(
    args: argparse.Namespace,
    *,
    quiet: bool = False,
    push_ranges: list[tuple[str, str]] | None = None,
) -> int:
    repo = repo_root(args.repo)
    output = receipt_path(repo, getattr(args, "receipt", None))
    if push_ranges is None:
        if (args.old_oid is None) != (args.new_oid is None):
            raise GateError("verify requires both --old-oid and --new-oid when either is supplied")
        if args.old_oid is None:
            if not output.is_file():
                raise GateError(
                    f"missing final review receipt {output}; run review_gate.py freeze, run, then verify"
                )
            receipt, receipt_identity = _load_receipt(repo, output)
            head = _run_git(repo, "rev-parse", "HEAD").strip()
            _oid(head, "current HEAD")
            if receipt_identity["new_oid"] != head:
                raise GateError(
                    f"review receipt is stale: receipt new_oid {receipt_identity['new_oid']} does not match current HEAD {head}"
                )
            push_ranges = [(receipt_identity["old_oid"], receipt_identity["new_oid"])]
        else:
            push_ranges = [(args.old_oid, args.new_oid)]
    unique_ranges = list(dict.fromkeys(push_ranges))
    if len(unique_ranges) != 1:
        raise GateError("protected verification requires exactly one unique old/new object range")
    old_oid, new_oid = unique_ranges[0]
    identity = _bundle_from_git(repo, old_oid, new_oid, check_worktree=False)
    if not output.is_file():
        raise GateError(
            f"missing final review receipt {output}; run review_gate.py freeze, run, then verify"
        )
    document, receipt_identity = _load_receipt(repo, output)
    _assert_same_identity(receipt_identity, identity, "review receipt")
    _verify_receipt(repo, document, identity)
    if not quiet:
        if document.get("kind") == "waiver":
            actor = _mapping(document.get("waiver"), "review receipt waiver").get("actor")
            print(f"review gate clean: explicit trivial waiver by {actor}")
        else:
            print("review gate clean: autoreview and both independent Thermos passes for the frozen Git range")
    return 0


def protected_refs(repo: Path, active_remote: str | None = None) -> set[str]:
    refs = {f"refs/heads/{name}" for name in PROTECTED_BRANCHES}
    configured = os.environ.get("OMP_REVIEW_PROTECTED_BRANCHES", "")
    refs.update(f"refs/heads/{name.strip()}" for name in configured.split(",") if name.strip())
    if active_remote:
        remotes = [active_remote]
    else:
        remotes = sorted(item.strip() for item in _run_git(repo, "remote").splitlines() if item.strip())
    for remote in remotes:
        symbolic = _probe_git(repo, "symbolic-ref", "--quiet", f"refs/remotes/{remote}/HEAD")
        prefix = f"refs/remotes/{remote}/"
        if symbolic and symbolic.startswith(prefix):
            branch = symbolic[len(prefix):]
            if branch:
                refs.add(f"refs/heads/{branch}")
    return refs


def _feature_base(repo: Path, new_oid: str, active_remote: str | None) -> str:
    candidates: list[str] = []
    remotes = [active_remote] if active_remote else sorted(
        item.strip() for item in _run_git(repo, "remote").splitlines() if item.strip()
    )
    for remote in remotes:
        if not remote:
            continue
        symbolic = _probe_git(repo, "symbolic-ref", "--quiet", f"refs/remotes/{remote}/HEAD")
        if symbolic:
            candidates.append(symbolic)
    configured_names = [
        name.strip()
        for name in os.environ.get("OMP_REVIEW_PROTECTED_BRANCHES", "").split(",")
        if name.strip()
    ]
    candidates.extend(f"refs/heads/{name}" for name in (*sorted(PROTECTED_BRANCHES), *configured_names))
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if _probe_git(repo, "rev-parse", "--verify", f"{candidate}^{{commit}}") is None:
            continue
        merge_base = _probe_git(repo, "merge-base", candidate, new_oid)
        if merge_base and OID_PATTERN.fullmatch(merge_base):
            return merge_base
    return ZERO_OID


def _waiver_actor(repo: Path) -> str:
    for key in ("user.email", "user.name"):
        actor = _probe_git(repo, "config", "--get", key)
        if actor:
            return actor
    return "<actor>"


def _waiver_command(repo: Path, freeze_file: Path, actor: str) -> str:
    return shlex.join(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            "waive",
            "--repo",
            str(repo),
            "--freeze",
            str(freeze_file),
            "--actor",
            actor,
            "--reason",
            "<operator-supplied reason>",
        ]
    )

def _ensure_review(args: argparse.Namespace, repo: Path, old_oid: str, new_oid: str) -> None:
    output = receipt_path(repo)
    range_pair = [(old_oid, new_oid)]
    if output.is_file():
        try:
            verify(args, quiet=True, push_ranges=range_pair)
            return
        except GateError:
            pass
    identity = _bundle_from_git(repo, old_oid, new_oid, check_worktree=True)
    if _scope(identity["paths"]) == "trivial":
        freeze_args = argparse.Namespace(repo=str(repo), output=None, old_oid=old_oid, new_oid=new_oid)
        freeze(freeze_args)
        freeze_file = freeze_path(repo, None)
        actor = _waiver_actor(repo)
        raise GateError(
            "trivial review range requires an explicit, actor-attributed waiver; "
            f"run: {_waiver_command(repo, freeze_file, actor)}"
        )
    freeze_args = argparse.Namespace(repo=str(repo), output=None, old_oid=old_oid, new_oid=new_oid)
    freeze(freeze_args)
    from review_runner import run_command

    run_command(
        argparse.Namespace(
            repo=str(repo),
            freeze=None,
            output_dir=None,
            timeout=1800,
        )
    )
    verify(args, quiet=True, push_ranges=range_pair)


def hook(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    updates = [line.split() for line in sys.stdin.read().splitlines() if line.split()]
    if not updates:
        return 0
    if any(len(update) != 4 for update in updates):
        raise GateError("pre-push hook received a malformed ref update; reinstall the hook and retry the push")
    protected = protected_refs(repo, getattr(args, "remote", None))
    push_ranges: list[tuple[str, str]] = []
    for update in updates:
        remote_ref = update[2]
        if not remote_ref.startswith("refs/heads/"):
            continue
        local_oid, remote_old_oid = update[1], update[3]
        if local_oid == ZERO_OID:
            if remote_ref in protected:
                raise GateError("refusing to delete a protected default branch")
            continue
        _oid(local_oid, "branch push new object id")
        _oid(remote_old_oid, "branch push old object id", allow_zero=True)
        if remote_ref in protected:
            push_ranges.append((remote_old_oid, local_oid))
        elif remote_old_oid == ZERO_OID:
            push_ranges.append((_feature_base(repo, local_oid, getattr(args, "remote", None)), local_oid))
        else:
            push_ranges.append((remote_old_oid, local_oid))
    unique_ranges = list(dict.fromkeys(push_ranges))
    if not unique_ranges:
        print("review gate skipped: push contains no non-deletion branch updates")
        return 0
    if len(unique_ranges) != 1:
        raise GateError("pre-push review requires one unique old/new object range")
    old_oid, new_oid = unique_ranges[0]
    _ensure_review(args, repo, old_oid, new_oid)
    return verify(args, push_ranges=unique_ranges)


def classify_command(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    if args.old_oid is None or args.new_oid is None:
        raise GateError("classify requires --old-oid and --new-oid for a committed range")
    identity = _bundle_from_git(repo, args.old_oid, args.new_oid, check_worktree=True)
    print(json.dumps({"scope": _scope(identity["paths"]), **identity}, indent=2, sort_keys=True))
    return 0



def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Verify immutable committed-range review receipts before protected pushes.")
    sub = root.add_subparsers(dest="command", required=True)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--repo", default=".")
    verify_parser.add_argument("--receipt")
    verify_parser.add_argument("--old-oid")
    verify_parser.add_argument("--new-oid")
    hook_parser = sub.add_parser("hook")
    hook_parser.add_argument("--repo", default=".")
    hook_parser.add_argument("--remote")
    classify_parser = sub.add_parser("classify")
    classify_parser.add_argument("--repo", default=".")
    classify_parser.add_argument("--old-oid", required=True)
    classify_parser.add_argument("--new-oid", required=True)
    freeze_parser = sub.add_parser("freeze")
    freeze_parser.add_argument("--repo", default=".")
    freeze_parser.add_argument("--output")
    freeze_parser.add_argument("--old-oid", required=True)
    freeze_parser.add_argument("--new-oid", required=True)
    run_parser = sub.add_parser("run", help="run all reviewers for a frozen range and record gate-owned pass envelopes")
    run_parser.add_argument("--repo", default=".")
    run_parser.add_argument("--freeze")
    run_parser.add_argument("--output-dir")
    run_parser.add_argument("--timeout", type=int, default=1800)
    waive_parser = sub.add_parser("waive")
    waive_parser.add_argument("--repo", default=".")
    waive_parser.add_argument("--output")
    waive_parser.add_argument("--freeze")
    waive_parser.add_argument("--actor", required=True)
    waive_parser.add_argument("--reason", required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "freeze":
            return freeze(args)
        if args.command == "classify":
            return classify_command(args)
        if args.command == "run":
            from review_runner import run_command

            return run_command(args)
        if args.command == "waive":
            return waive(args)
        if args.command == "hook":
            return hook(args)
        return verify(args)
    except (GateError, OSError, ValueError) as error:
        print(f"review-gate: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
