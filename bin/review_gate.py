#!/usr/bin/env python3
"""Fail-closed committed-range review and protected-push gate."""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
from pathlib import Path

from review_bundle import (
    assert_same_identity,
    bundle_from_git,
    feature_base,
    freeze_path,
    load_freeze,
    oid,
    peel_commit,
    probe_git,
    protected_refs,
    receipt_path,
    repo_root,
    run_git,
)
from review_common import (
    BUNDLE_SCHEMA,
    FREEZE_SCHEMA,
    GATE_ROOT,
    PASS_DIRECTORY,
    PASS_SCHEMA,
    PINNED_WORKERS,
    RECEIPT_SCHEMA,
    REVIEWERS,
    SCHEMA,
    ZERO_OID,
    GateError,
    mapping,
    now,
    review_scope,
    write_json,
)
from review_receipt import load_receipt, verify_receipt, record_receipt
from review_runner import run_command

NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.@+-]{1,127}$")


def _scope(paths: list[str]) -> str:
    return review_scope(paths)


def freeze(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    output = freeze_path(repo, args.output)
    identity = bundle_from_git(repo, args.old_oid, args.new_oid, check_worktree=True)
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
    _, frozen = load_freeze(repo, freeze_file)
    current = bundle_from_git(repo, frozen["old_oid"], frozen["new_oid"], check_worktree=True)
    assert_same_identity(frozen, current, "review freeze")
    if args.autoreview_json is None or args.autoreview_exit is None:
        raise GateError("record requires --autoreview-json and --autoreview-exit")
    output = receipt_path(repo, args.output)
    record_receipt(
        repo,
        freeze_file,
        output,
        args.scope,
        args.autoreview_json,
        args.autoreview_exit,
        args.thermo_correctness_json,
        args.thermo_quality_json,
    )
    print(f"review receipt written: {output}")
    return 0


def waive(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    freeze_file = freeze_path(repo, args.freeze)
    _, frozen = load_freeze(repo, freeze_file)
    current = bundle_from_git(repo, frozen["old_oid"], frozen["new_oid"], check_worktree=True)
    assert_same_identity(frozen, current, "review freeze")
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
        "waiver": {"actor": actor, "reason": reason, "recorded_at": now()},
        "protocol": "explicit trivial prose/config waiver bound to a frozen committed range",
    }
    write_json(output, document)
    print(f"trivial review waiver written: {output}")
    return 0


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
                raise GateError(f"missing final review receipt {output}; run review_gate.py freeze, run, then verify")
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
        raise GateError(f"missing final review receipt {output}; run review_gate.py freeze, run, then verify")
    document, receipt_identity = load_receipt(repo, output)
    assert_same_identity(receipt_identity, identity, "review receipt")
    verify_receipt(repo, document, identity, _scope)
    if not quiet:
        if document.get("kind") == "waiver":
            actor = mapping(document.get("waiver"), "review receipt waiver").get("actor")
            print(f"review gate clean: explicit trivial waiver by {actor}")
        else:
            print("review gate clean: autoreview and both independent Thermos passes for the frozen Git range")
    return 0


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
    identity = bundle_from_git(repo, old_oid, new_oid, check_worktree=True)
    freeze_args = argparse.Namespace(repo=str(repo), output=None, old_oid=old_oid, new_oid=new_oid)
    freeze(freeze_args)
    if _scope(identity["paths"]) == "trivial":
        freeze_file = freeze_path(repo, None)
        actor = _waiver_actor(repo)
        raise GateError(
            "trivial review range requires an explicit, actor-attributed waiver; "
            f"run: {_waiver_command(repo, freeze_file, actor)}"
        )
    run_command(argparse.Namespace(repo=str(repo), freeze=None, output_dir=None, timeout=1800))
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
        return 0
    if len(unique_ranges) != 1:
        raise GateError("pre-push review requires one unique old/new object range")
    _ensure_review(args, repo, *unique_ranges[0])
    return verify(args, push_ranges=unique_ranges)


def classify_command(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    identity = bundle_from_git(repo, args.old_oid, args.new_oid, check_worktree=True)
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
