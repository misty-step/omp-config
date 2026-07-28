"""Pass, receipt, and worker-attestation validation for review gates."""
from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Callable

from review_bundle import (
    assert_same_identity,
    bundle_from_git,
    identity_from_document,
    load_freeze,
)
from review_common import (
    DIGEST_PATTERN,
    PASS_DIRECTORY,
    PASS_SCHEMA,
    RECEIPT_SCHEMA,
    REVIEWERS,
    GateError,
    directory_digest,
    mapping,
    nonnegative_int,
    now,
    read_json,
    sha256_bytes,
    worker_path,
    review_scope,
    write_json,
)


def gate_pass_path(repo: Path, path: Path, reviewer: str) -> Path:
    expected = (repo / PASS_DIRECTORY / f"{reviewer}.json").resolve()
    actual = path.expanduser().resolve(strict=False)
    if actual != expected:
        raise GateError(
            f"review pass {path} is not the gate-owned artifact {expected.relative_to(repo).as_posix()}"
        )
    if not actual.is_file():
        raise GateError(f"missing gate-owned review pass artifact {actual}")
    return actual


def audit_worker(
    document: dict[str, Any],
    label: str,
    repo: Path,
    reviewer: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    worker = mapping(document.get("worker"), f"{label}.worker")
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
    executable = worker_path(worker["executable"], label, reviewer, directory=False)
    payload = worker_path(worker["payload"], label, reviewer, directory=True)
    if sha256_bytes(executable.read_bytes()) != worker["executable_sha256"]:
        raise GateError(f"{label}.worker.executable_sha256 does not match the pinned executable")
    if directory_digest(payload) != worker["payload_sha256"]:
        raise GateError(f"{label}.worker.payload_sha256 does not match the pinned payload")
    raw_report = mapping(document.get("raw_report"), f"{label}.raw_report")
    return worker, raw_report


def pass_artifact(repo: Path, path: Path, reviewer: str) -> dict[str, str]:
    artifact = gate_pass_path(repo, path, reviewer)
    return {
        "path": artifact.relative_to(repo).as_posix(),
        "sha256": sha256_bytes(artifact.read_bytes()),
    }


def pass_document(
    path: Path,
    expected: str,
    identity: dict[str, Any],
    *,
    repo: Path,
    exit_code: int | None = None,
) -> dict[str, Any]:
    document = read_json(path, f"review pass {path}")
    if document.get("schema") != PASS_SCHEMA:
        raise GateError(f"review pass {path} must declare schema {PASS_SCHEMA}")
    pass_identity = identity_from_document(document, f"review pass {path}")
    assert_same_identity(pass_identity, identity, f"review pass {path}")
    if document.get("reviewer") != expected:
        raise GateError(f"review pass {path} is for {document.get('reviewer')!r}, expected {expected!r}")
    worker, raw_report = audit_worker(document, f"review pass {path}", repo, expected)
    status = document.get("status")
    if status not in {"clean", "findings", "unavailable", "failed"}:
        raise GateError(f"review pass {path} has unsupported status {status!r}")
    findings = nonnegative_int(document.get("actionable_findings"), f"{path}.actionable_findings")
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
    result["pass_artifact"] = pass_artifact(repo, path, expected)
    return result


def clean_passes(passes: list[dict[str, Any]]) -> None:
    for item in passes:
        if item["status"] == "unavailable":
            raise GateError(
                f"reviewer {item['reviewer']} is unavailable; install/authenticate the reviewer and rerun review_gate.py run"
            )
        if item["actionable_findings"] != 0:
            raise GateError(f"reviewer {item['reviewer']} reported actionable findings; fix them and rerun review_gate.py run")
        if item["status"] != "clean" or item["exit_code"] != 0:
            raise GateError(f"reviewer {item['reviewer']} did not produce a clean pass; rerun review_gate.py run")


def load_receipt(repo: Path, output: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    document = read_json(output, f"review receipt {output}")
    if document.get("schema") != RECEIPT_SCHEMA:
        raise GateError(f"review receipt must declare schema {RECEIPT_SCHEMA}")
    identity = identity_from_document(document, "review receipt")
    if identity["repository"] != str(repo):
        raise GateError("review receipt belongs to a different repository")
    return document, identity


def verify_receipt(
    repo: Path,
    document: dict[str, Any],
    identity: dict[str, Any],
    scope_for_paths: Callable[[list[str]], str],
) -> None:
    assert_same_identity(identity_from_document(document, "review receipt"), identity, "review receipt")
    scope = document.get("scope")
    if scope not in {"trivial", "substantive"}:
        raise GateError("review receipt has unsupported scope")
    kind = document.get("kind")
    actual_scope = scope_for_paths(identity["paths"])
    if kind == "waiver":
        waiver = mapping(document.get("waiver"), "review receipt waiver")
        actor = waiver.get("actor")
        reason = waiver.get("reason")
        if not isinstance(actor, str) or not re.fullmatch(r"^[A-Za-z][A-Za-z0-9_.@+-]{1,127}$", actor):
            raise GateError("review receipt waiver has no valid actor")
        if not isinstance(reason, str) or len(reason.strip()) < 12:
            raise GateError("review receipt waiver has no auditable reason")
        if actual_scope != "trivial" or scope != "trivial":
            raise GateError("trivial waiver cannot authorize substantive policy or code changes")
        return
    if kind == "review" and actual_scope == "trivial":
        raise GateError("trivial changes require an explicit, actor-attributed waiver")
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
        entry = mapping(item, "reviewer receipt")
        reviewer = entry.get("reviewer")
        if not isinstance(reviewer, str):
            raise GateError("reviewer receipt reviewer must be a string")
        names.append(reviewer)
        assert_same_identity(identity_from_document(entry, "reviewer receipt"), identity, "reviewer receipt")
        artifact = mapping(entry.get("pass_artifact"), f"reviewer receipt {reviewer}.pass_artifact")
        artifact_path = artifact.get("path")
        expected_path = (PASS_DIRECTORY / f"{reviewer}.json").as_posix()
        if artifact_path != expected_path:
            raise GateError(f"reviewer receipt {reviewer} is not bound to its gate-owned pass artifact")
        artifact_digest = artifact.get("sha256")
        if not isinstance(artifact_digest, str) or not DIGEST_PATTERN.fullmatch(artifact_digest):
            raise GateError(f"reviewer receipt {reviewer}.pass_artifact.sha256 must be a sha256 digest")
        pass_path = gate_pass_path(repo, repo / artifact_path, reviewer)
        if sha256_bytes(pass_path.read_bytes()) != artifact_digest:
            raise GateError(f"reviewer receipt {reviewer} pass artifact changed after record")
        pass_document_value = pass_document(pass_path, reviewer, identity, repo=repo)
        embedded = dict(entry)
        embedded.pop("pass_artifact", None)
        pass_document_value.pop("pass_artifact", None)
        if embedded != pass_document_value:
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


def record_receipt(
    repo: Path,
    freeze_file: Path,
    output: Path,
    requested_scope: str,
    autoreview_json: Path,
    autoreview_exit: int,
    thermo_correctness_json: Path,
    thermo_quality_json: Path,
) -> None:
    _, frozen = load_freeze(repo, freeze_file)
    current = bundle_from_git(repo, frozen["old_oid"], frozen["new_oid"], check_worktree=True)
    assert_same_identity(frozen, current, "review freeze")
    actual_scope = review_scope(frozen["paths"])
    if requested_scope != actual_scope:
        raise GateError(f"requested scope {requested_scope!r} does not match frozen changed scope {actual_scope!r}")
    passes = [
        pass_document(autoreview_json, "autoreview", frozen, repo=repo, exit_code=autoreview_exit),
        pass_document(thermo_correctness_json, "thermo-nuclear-review", frozen, repo=repo),
        pass_document(thermo_quality_json, "thermo-nuclear-code-quality-review", frozen, repo=repo),
    ]
    clean_passes(passes)
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
