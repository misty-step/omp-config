#!/usr/bin/env python3
"""Fail-closed committed-range review and protected-push gate."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from review_bundle import (
    assert_same_identity,
    bundle_from_git,
    feature_base,
    load_freeze,
    oid,
    peel_commit,
    probe_git,
    protected_refs,
    repo_root,
    run_git,
)
from review_common import (
    ACTOR_PATTERN,
    FREEZE_RELATIVE,
    FREEZE_SCHEMA,
    RECEIPT_RELATIVE,
    RECEIPT_SCHEMA,
    REVIEW_SPECS,
    REVIEWERS,
    GateError,
    ZERO_OID,
    mapping,
    now,
    review_scope,
    write_json,
)
from review_receipt import load_receipt, record_receipt, submit_result, verify_receipt
REVIEW_SEQUENCE = "freeze -> submit -> record -> verify"
EXIT_CLEAN = 0
EXIT_NON_CLEAN = 1
EXIT_PROTOCOL = 2


def _freeze_file(repo: Path) -> Path:
    return repo / FREEZE_RELATIVE


def _receipt_file(repo: Path) -> Path:
    return repo / RECEIPT_RELATIVE




def _scope(paths: list[str]) -> str:
    return review_scope(paths)


def freeze(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    old_oid = getattr(args, "old_oid", None) or feature_base(repo, getattr(args, "new_oid", None) or "HEAD", getattr(args, "remote", None))
    new_oid = getattr(args, "new_oid", None) or "HEAD"
    identity = bundle_from_git(repo, old_oid, new_oid, check_worktree=not getattr(args, "no_worktree_check", False))
    freeze_file = _freeze_file(repo)
    pass_dir = repo / Path(".omp/review-passes")
    if pass_dir.is_dir():
        for item in pass_dir.glob("*.json"):
            item.unlink(missing_ok=True)
    receipt = _receipt_file(repo)
    if receipt.is_file():
        receipt.unlink(missing_ok=True)
    document = {"schema": FREEZE_SCHEMA, "kind": "freeze", **identity, "created_at": now()}
    write_json(freeze_file, document)
    return EXIT_CLEAN


def prepare(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    _freeze_file(repo)
    return EXIT_CLEAN

def _read_result(args: argparse.Namespace) -> dict[str, Any]:
    source = args.result
    if source is None or source == "-":
        raw = sys.stdin.read()
        label = "review result from stdin"
    else:
        path = Path(source).expanduser()
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as error:
            raise GateError(f"cannot read review result {path}: {error}") from error
        label = f"review result {path}"
    try:
        return mapping(json.loads(raw), label)
    except json.JSONDecodeError as error:
        raise GateError(f"{label} is not JSON: {error}") from error


def submit(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    reviewer = args.reviewer
    if reviewer not in REVIEW_SPECS:
        raise GateError(f"submit accepts only canonical reviewers ({', '.join(REVIEWERS)})")
    result = _read_result(args)
    attribution = {
        "actor": args.actor,
        "harness": args.harness,
        "model": args.model,
        "run_id": args.run_id,
    }
    freeze_file = _freeze_file(repo)
    output = submit_result(repo, freeze_file, reviewer, attribution, result)
    status = result.get("status")
    print(f"review pass submitted: {output}")
    if status != "clean":
        return EXIT_NON_CLEAN
    return EXIT_CLEAN


def record(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    freeze_file = _freeze_file(repo)
    output = _receipt_file(repo)
    record_receipt(repo, freeze_file, output)
    print(f"review receipt written: {output}")
    return EXIT_CLEAN


def waive(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    freeze_file = _freeze_file(repo)
    _, frozen = load_freeze(repo, freeze_file)
    current = bundle_from_git(repo, frozen["old_oid"], frozen["new_oid"], check_worktree=True)
    assert_same_identity(frozen, current, "review freeze")
    if _scope(frozen["paths"]) != "trivial":
        raise GateError("trivial waiver is allowed only for inert prose/config-only changes")
    reason = args.reason.strip()
    actor = args.actor.strip()
    if len(reason) < 12 or not any(word in reason.lower() for word in ("prose", "config", "documentation")):
        raise GateError("waiver reason must explain why the prose/config change is trivial")
    if not ACTOR_PATTERN.fullmatch(actor):
        raise GateError("waiver actor must be a stable name or email-like identifier")
    output = _receipt_file(repo)
    document = {
        "schema": RECEIPT_SCHEMA,
        "kind": "waiver",
        **frozen,
        "scope": "trivial",
        "created_at": now(),
        "freeze_manifest": freeze_file.relative_to(repo).as_posix(),
        "waiver": {"actor": actor, "reason": reason, "recorded_at": now()},
        "protocol": "explicit trivial prose/config waiver bound to a frozen committed range",
    }
    write_json(output, document)
    print(f"trivial review waiver written: {output}")
    return EXIT_CLEAN


def verify(
    args: argparse.Namespace,
    *,
    quiet: bool = False,
    push_ranges: list[tuple[str, str]] | None = None,
) -> int:
    repo = repo_root(args.repo)
    output = _receipt_file(repo)
    if push_ranges is None:
        if (args.old_oid is None) != (args.new_oid is None):
            raise GateError("verify requires both --old-oid and --new-oid when either is supplied")
        if args.old_oid is None:
            if not output.is_file():
                raise GateError(f"missing final review receipt {output}; run {REVIEW_SEQUENCE}")
            receipt, receipt_identity = load_receipt(repo, output)
            head = run_git(repo, "rev-parse", "HEAD").strip()
            oid(head, "current HEAD")
            if receipt_identity["new_oid"] != head:
                raise GateError(f"review receipt is stale: receipt new_oid {receipt_identity['new_oid']} does not match current HEAD {head}")
            push_ranges = [(receipt_identity["old_oid"], receipt_identity["new_oid"])]
        else:
            push_ranges = [(args.old_oid, args.new_oid)]
    unique_ranges = list(dict.fromkeys(push_ranges))
    if len(unique_ranges) != 1:
        raise GateError("protected verification requires exactly one unique old/new object range")
    old_oid, new_oid = unique_ranges[0]
    identity = bundle_from_git(repo, old_oid, new_oid, check_worktree=False)
    if not output.is_file():
        raise GateError(f"missing final review receipt {output}; run {REVIEW_SEQUENCE}")
    document, receipt_identity = load_receipt(repo, output)
    assert_same_identity(receipt_identity, identity, "review receipt")
    verify_receipt(repo, document, identity, _scope)
    if not quiet:
        if document.get("kind") == "waiver":
            actor = mapping(document.get("waiver"), "review receipt waiver").get("actor")
            print(f"review gate clean: explicit trivial waiver by {actor}")
        else:
            print("review gate clean: three canonical review passes verified for the frozen Git range")
    return EXIT_CLEAN


def _waiver_actor(repo: Path) -> str:
    for key in ("user.email", "user.name"):
        actor = probe_git(repo, "config", "--get", key)
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
            "--actor",
            actor,
            "--reason",
            "<operator-supplied reason>",
        ]
    )


def _review_gap(args: argparse.Namespace, repo: Path, old_oid: str, new_oid: str) -> tuple[str, str]:
    """Probe review evidence for a range without raising.

    Returns (status, guidance) with status in {"clean", "trivial", "missing"}.
    """
    output = _receipt_file(repo)
    range_pair = [(old_oid, new_oid)]
    if output.is_file():
        try:
            verify(args, quiet=True, push_ranges=range_pair)
            return ("clean", "")
        except GateError:
            pass
    identity = bundle_from_git(repo, old_oid, new_oid, check_worktree=True)
    freeze_args = argparse.Namespace(repo=str(repo), old_oid=old_oid, new_oid=new_oid)
    freeze(freeze_args)
    if _scope(identity["paths"]) == "trivial":
        return (
            "trivial",
            "trivial review range requires an explicit, actor-attributed waiver; "
            f"run: {_waiver_command(repo, _freeze_file(repo), _waiver_actor(repo))}",
        )
    return (
        "missing",
        f"review gate has no clean receipt for this range; complete {REVIEW_SEQUENCE}",
    )


def _ensure_review(args: argparse.Namespace, repo: Path, old_oid: str, new_oid: str) -> None:
    """Enforce mode: raise when the range lacks clean review evidence."""
    status, guidance = _review_gap(args, repo, old_oid, new_oid)
    if status != "clean":
        raise GateError(guidance)


def hook(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    updates = [line.split() for line in sys.stdin.read().splitlines() if line.split()]
    if not updates:
        return EXIT_CLEAN
    if any(len(update) != 4 for update in updates):
        raise GateError("pre-push hook received a malformed ref update; reinstall the hook and retry the push")
    protected = protected_refs(repo, getattr(args, "remote", None))
    push_ranges: list[tuple[str, str]] = []
    for update in updates:
        local_ref, local_oid, remote_ref, remote_old_oid = update
        if remote_ref.startswith("refs/tags/") and local_ref.startswith("refs/tags/"):
            if local_oid == ZERO_OID:
                continue
            new_commit = peel_commit(repo, local_oid, "tag push new object id")
            if remote_old_oid == ZERO_OID:
                push_ranges.append((ZERO_OID, new_commit))
            else:
                push_ranges.append((peel_commit(repo, remote_old_oid, "tag push old object id"), new_commit))
            continue
        if not remote_ref.startswith("refs/heads/"):
            continue
        if local_oid == ZERO_OID:
            if remote_ref in protected:
                raise GateError("refusing to delete a protected default branch")
            continue
        oid(local_oid, "branch push new object id")
        oid(remote_old_oid, "branch push old object id", allow_zero=True)
        if remote_ref in protected:
            push_ranges.append((remote_old_oid, local_oid))
        elif remote_old_oid == ZERO_OID:
            push_ranges.append((feature_base(repo, local_oid, getattr(args, "remote", None)), local_oid))
        else:
            push_ranges.append((remote_old_oid, local_oid))
    unique_ranges = list(dict.fromkeys(push_ranges))
    if not unique_ranges:
        print("review gate skipped: push contains no non-deletion branch updates")
        return EXIT_CLEAN
    enforce = getattr(args, "enforce", False)
    if len(unique_ranges) != 1:
        if enforce:
            raise GateError("pre-push review requires one unique old/new object range")
        print(
            "review-gate (advisory): multiple push ranges in one push; "
            "review evidence is optional here",
            file=sys.stderr,
        )
        return EXIT_CLEAN
    status, guidance = _review_gap(args, repo, *unique_ranges[0])
    if status == "clean":
        return verify(args, push_ranges=unique_ranges)
    if enforce:
        raise GateError(guidance)
    # Encouraged, not enforced: warn with the exact commands and let the
    # push through. The freeze written by the probe is the starting point.
    print(f"review-gate (advisory): {guidance}", file=sys.stderr)
    print(
        "review-gate (advisory): push allowed without review evidence; "
        "run the sequence (freeze, prepare, submit, record, verify) to record it",
        file=sys.stderr,
    )
    return EXIT_CLEAN


def classify_command(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    identity = bundle_from_git(repo, args.old_oid, args.new_oid, check_worktree=True)
    print(json.dumps({"scope": _scope(identity["paths"]), **identity}, indent=2, sort_keys=True))
    return EXIT_CLEAN


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Manage the immutable committed-range review gate.")
    sub = root.add_subparsers(dest="command", required=True)

    classify_parser = sub.add_parser("classify", help="classify a committed range")
    classify_parser.add_argument("--repo", default=".")
    classify_parser.add_argument("--old-oid", required=True)
    classify_parser.add_argument("--new-oid", required=True)

    freeze_parser = sub.add_parser("freeze", help="freeze a committed range")
    freeze_parser.add_argument("--repo", default=".")
    freeze_parser.add_argument("--old-oid")
    freeze_parser.add_argument("--new-oid")
    freeze_parser.add_argument("--remote")
    freeze_parser.add_argument("--no-worktree-check", action="store_true")
    prepare_parser = sub.add_parser("prepare", help="prepare the gate-owned review packet")
    prepare_parser.add_argument("--repo", default=".")

    submit_parser = sub.add_parser("submit", help="submit one direct leaf review result")
    submit_parser.add_argument("--repo", default=".")
    submit_parser.add_argument("--reviewer", choices=REVIEWERS, required=True)
    submit_parser.add_argument("--actor", required=True)
    submit_parser.add_argument("--harness", required=True)
    submit_parser.add_argument("--model", required=True)
    submit_parser.add_argument("--run-id", required=True)
    submit_parser.add_argument("--result", help="JSON result file; use - or omit to read stdin")

    record_parser = sub.add_parser("record", help="record the three gate-owned review passes")
    record_parser.add_argument("--repo", default=".")

    verify_parser = sub.add_parser("verify", help="verify the final receipt for a committed range")
    verify_parser.add_argument("--repo", default=".")
    verify_parser.add_argument("--old-oid")
    verify_parser.add_argument("--new-oid")

    waive_parser = sub.add_parser("waive", help="record an explicit trivial-change waiver")
    waive_parser.add_argument("--repo", default=".")
    waive_parser.add_argument("--actor", required=True)
    waive_parser.add_argument("--reason", required=True)

    hook_parser = sub.add_parser(
        "hook",
        help="advisory pre-push review check (warn, never block); --enforce opts into blocking",
    )
    hook_parser.add_argument("--repo", default=".")
    hook_parser.add_argument("--remote")
    hook_parser.add_argument(
        "--enforce",
        action="store_true",
        help="fail the push when the range lacks a clean receipt or waiver",
    )
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "freeze":
            return freeze(args)
        if args.command == "prepare":
            return prepare(args)
        if args.command == "submit":
            return submit(args)
        if args.command == "record":
            return record(args)
        if args.command == "classify":
            return classify_command(args)
        if args.command == "waive":
            return waive(args)
        if args.command == "hook":
            return hook(args)
        if args.command == "verify":
            return verify(args)
        raise GateError(f"unsupported review-gate command {args.command!r}")
    except (GateError, OSError, ValueError) as error:
        print(f"review-gate: {error}", file=sys.stderr)
        return EXIT_PROTOCOL

if __name__ == "__main__":
    raise SystemExit(main())
