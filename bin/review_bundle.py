"""Canonical committed-range identity and Git evidence operations."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any
from review_common import (
    BUNDLE_SCHEMA,
    DIGEST_PATTERN,
    FREEZE_SCHEMA,
    PASS_DIRECTORY,
    FREEZE_RELATIVE,
    GateError,
    OID_PATTERN,
    PROTECTED_BRANCHES,
    RECEIPT_RELATIVE,
    ZERO_OID,
    confined_path,
    read_json,
)


def run_git(repo: Path, *args: str, input_text: str | None = None) -> str:
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


def probe_git(repo: Path, *args: str) -> str | None:
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
        raw_root = run_git(candidate, "rev-parse", "--show-toplevel").strip()
    except (GateError, OSError) as error:
        raise GateError(f"not a Git worktree: {candidate}") from error
    if not raw_root:
        raise GateError(f"Git did not report a worktree root: {candidate}")
    resolved = Path(raw_root).resolve()
    if not resolved.is_dir():
        raise GateError(f"Git worktree root is not a directory: {resolved}")
    return resolved


def freeze_path(repo: Path, value: str | None = None) -> Path:
    return confined_path(repo, value, FREEZE_RELATIVE, "freeze")


def receipt_path(repo: Path, value: str | None = None) -> Path:
    return confined_path(repo, value, RECEIPT_RELATIVE, "receipt")


def path_from_git(raw: str) -> Path:
    if not raw:
        raise GateError("Git reported an empty changed path")
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts or path == Path("."):
        raise GateError(f"Git reported an unsafe changed path: {raw!r}")
    return path


def oid(value: object, label: str, *, allow_zero: bool = False) -> str:
    if value == ZERO_OID and not allow_zero:
        raise GateError(f"{label} cannot be the zero object id")
    if not isinstance(value, str) or not OID_PATTERN.fullmatch(value):
        raise GateError(f"{label} must be a 40-character lowercase Git object id")
    return value


def validate_commit_object(repo: Path, object_id: str, label: str) -> tuple[str, list[str]]:
    oid(object_id, label)
    raw = run_git(repo, "cat-file", "-p", f"{object_id}^{{commit}}")
    tree_oid: str | None = None
    parents: list[str] = []
    for line in raw.splitlines():
        if line.startswith("tree "):
            tree_oid = line[5:].strip()
        elif line.startswith("parent "):
            parent = line[7:].strip()
            oid(parent, f"{label} parent")
            parents.append(parent)
    if tree_oid is None:
        raise GateError(f"Git commit {object_id} has no tree object")
    oid(tree_oid, f"{label} tree")
    run_git(repo, "cat-file", "-e", f"{tree_oid}^{{tree}}")
    return tree_oid, parents


def validate_tree_contents(repo: Path, commit: str) -> None:
    raw = run_git(repo, "ls-tree", "-r", "-t", "-z", commit, "--")
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
        oid(object_id, f"{commit} tree entry")
        path_from_git(path_text)
        if object_type in {"blob", "tree"}:
            expected_objects.append((object_id, object_type))
        elif object_type == "commit" and mode != "160000":
            raise GateError(f"Git returned unsupported tree entry type {object_type!r}")
    if not expected_objects:
        return
    batch_input = "".join(f"{object_id}\n" for object_id, _ in expected_objects)
    checked = run_git(
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


def introduced_commits(repo: Path, old_oid: str, new_oid: str) -> list[str]:
    revision = new_oid if old_oid == ZERO_OID else f"{old_oid}..{new_oid}"
    raw = run_git(repo, "rev-list", "--reverse", "--topo-order", revision)
    commits: list[str] = []
    for line in raw.splitlines():
        commit = line.strip()
        if not commit:
            continue
        oid(commit, "introduced commit")
        commits.append(commit)
    if len(commits) != len(set(commits)):
        raise GateError("Git returned duplicate introduced commits")
    return commits


def paths_for_commit(repo: Path, commit: str) -> set[Path]:
    raw = run_git(
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
    return {path_from_git(item) for item in raw.split("\0") if item}


def bundle_digest(identity: dict[str, Any]) -> str:
    canonical = json.dumps(
        {"schema": BUNDLE_SCHEMA, **identity},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(canonical).hexdigest()}"


def _is_gate_runtime_path(path: Path) -> bool:
    return path in {FREEZE_RELATIVE, RECEIPT_RELATIVE} or path.is_relative_to(PASS_DIRECTORY)


def worktree_is_dirty_for_paths(repo: Path, new_oid: str, paths: list[Path]) -> None:
    if not paths:
        return
    path_args = [f":(literal){path.as_posix()}" for path in paths]
    changed = run_git(repo, "diff", "--no-ext-diff", "--name-only", "-z", new_oid, "--", *path_args)
    if changed:
        raise GateError("review freeze requires a clean worktree for every frozen path")
    status_paths = [path for path in paths if not _is_gate_runtime_path(path)]
    if not status_paths:
        return
    status_args = [f":(literal){path.as_posix()}" for path in status_paths]
    status = run_git(
        repo,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
        "--ignored=matching",
        "--",
        *status_args,
    )
    if status:
        raise GateError("review freeze requires a clean worktree for every frozen path")


def bundle_from_git(repo: Path, old_oid: str, new_oid: str, *, check_worktree: bool) -> dict[str, Any]:
    old_oid = oid(old_oid, "old_oid", allow_zero=True)
    new_oid = oid(new_oid, "new_oid")
    if old_oid == new_oid:
        raise GateError("review range must introduce at least one commit")
    shallow = run_git(repo, "rev-parse", "--is-shallow-repository").strip()
    if shallow not in {"true", "false"}:
        raise GateError("Git returned an invalid shallow-repository state")
    if shallow == "true":
        raise GateError("review range cannot be frozen or verified in a shallow repository")
    validate_commit_object(repo, new_oid, "new_oid")
    if old_oid != ZERO_OID:
        validate_commit_object(repo, old_oid, "old_oid")
    commits = introduced_commits(repo, old_oid, new_oid)
    if not commits:
        raise GateError("Git range contains no introduced commits")
    paths: set[Path] = set()
    for commit in commits:
        validate_commit_object(repo, commit, f"introduced commit {commit}")
        validate_tree_contents(repo, commit)
        paths.update(paths_for_commit(repo, commit))
    path_list = sorted(paths, key=lambda item: item.as_posix())
    identity: dict[str, Any] = {
        "repository": str(repo),
        "old_oid": old_oid,
        "new_oid": new_oid,
        "commits": commits,
        "paths": [path.as_posix() for path in path_list],
    }
    identity["bundle_digest"] = bundle_digest(identity)
    if check_worktree:
        worktree_is_dirty_for_paths(repo, new_oid, path_list)
    return identity


def identity_from_document(document: dict[str, Any], label: str) -> dict[str, Any]:
    repository = document.get("repository")
    old_oid = document.get("old_oid")
    new_oid = document.get("new_oid")
    commits = document.get("commits")
    paths = document.get("paths")
    digest = document.get("bundle_digest")
    if not isinstance(repository, str) or not repository:
        raise GateError(f"{label}.repository must be a non-empty string")
    oid(old_oid, f"{label}.old_oid", allow_zero=True)
    oid(new_oid, f"{label}.new_oid")
    if not isinstance(commits, list) or not all(isinstance(item, str) and OID_PATTERN.fullmatch(item) for item in commits):
        raise GateError(f"{label}.commits must be an ordered list of Git object ids")
    if len(commits) != len(set(commits)) or not commits:
        raise GateError(f"{label}.commits must contain unique introduced commits")
    if not isinstance(paths, list) or not all(isinstance(item, str) for item in paths):
        raise GateError(f"{label}.paths must be a list of repository-relative paths")
    normalized_paths = [path_from_git(item).as_posix() for item in paths]
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
    if bundle_digest({key: identity[key] for key in ("repository", "old_oid", "new_oid", "commits", "paths")}) != digest:
        raise GateError(f"{label}.bundle_digest does not match its canonical identity")
    return identity


def assert_same_identity(expected: dict[str, Any], actual: dict[str, Any], label: str) -> None:
    if expected != actual:
        raise GateError(f"{label} does not match the recomputed committed-range bundle")


def load_freeze(repo: Path, path: Path) -> tuple[dict[str, Any], dict[str, Any]]:

    document = read_json(path, f"review freeze {path}")
    if document.get("schema") != FREEZE_SCHEMA or document.get("kind") != "freeze":
        raise GateError(f"review freeze must declare schema {FREEZE_SCHEMA}")
    identity = identity_from_document(document, "review freeze")
    if identity["repository"] != str(repo):
        raise GateError("review freeze belongs to a different repository")
    return document, identity


def peel_commit(repo: Path, object_id: str, label: str) -> str:
    oid(object_id, label)
    peeled = probe_git(repo, "rev-parse", "--verify", f"{object_id}^{{commit}}")
    if peeled is None or not OID_PATTERN.fullmatch(peeled):
        raise GateError(f"{label} does not peel to a commit")
    return peeled


def feature_base(repo: Path, new_oid: str, active_remote: str | None) -> str:
    candidates: list[str] = []
    remotes = [active_remote] if active_remote else sorted(item.strip() for item in run_git(repo, "remote").splitlines() if item.strip())
    for remote in remotes:
        if not remote:
            continue
        symbolic = probe_git(repo, "symbolic-ref", "--quiet", f"refs/remotes/{remote}/HEAD")
        if symbolic:
            candidates.append(symbolic)
    configured_names = [name.strip() for name in os.environ.get("OMP_REVIEW_PROTECTED_BRANCHES", "").split(",") if name.strip()]
    candidates.extend(f"refs/heads/{name}" for name in (*sorted(PROTECTED_BRANCHES), *configured_names))
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if probe_git(repo, "rev-parse", "--verify", f"{candidate}^{{commit}}") is None:
            continue
        merge_base = probe_git(repo, "merge-base", candidate, new_oid)
        if merge_base and OID_PATTERN.fullmatch(merge_base):
            return merge_base
    return ZERO_OID

def protected_refs(repo: Path, active_remote: str | None = None) -> set[str]:
    refs = {f"refs/heads/{name}" for name in PROTECTED_BRANCHES}
    configured = os.environ.get("OMP_REVIEW_PROTECTED_BRANCHES", "")
    refs.update(f"refs/heads/{name.strip()}" for name in configured.split(",") if name.strip())
    remotes = [active_remote] if active_remote else sorted(item.strip() for item in run_git(repo, "remote").splitlines() if item.strip())
    for remote in remotes:
        symbolic = probe_git(repo, "symbolic-ref", "--quiet", f"refs/remotes/{remote}/HEAD")
        prefix = f"refs/remotes/{remote}/"
        if symbolic and symbolic.startswith(prefix):
            branch = symbolic[len(prefix):]
            if branch:
                refs.add(f"refs/heads/{branch}")
    return refs
