"""Gate-owned review result, pass, receipt, and verification authority."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping

from review_bundle import (
    assert_same_identity,
    bundle_from_git,
    identity_from_document,
    load_freeze,
    receipt_path,
)
from review_common import (
    ACTOR_PATTERN,
    DIGEST_PATTERN,
    FREEZE_RELATIVE,
    OBSOLETE_SCHEMA_MESSAGE,
    PACKET_RELATIVE,
    PASS_DIRECTORY,
    PASS_SCHEMA,
    RECEIPT_SCHEMA,
    RESULT_SCHEMA,
    REVIEWERS,
    GateError,
    canonical_json,
    mapping,
    nonnegative_int,
    now,
    read_json,
    sha256_bytes,
    skill_identity,
    worker_attribution,
    write_json,
)
from review_common import floor_plan
FINDING_SEVERITIES = {"blocking", "high", "medium", "low"}
FORBIDDEN_RESULT_FIELDS = {"worker", "adapter", "pass_artifact", "raw_result", "raw_result_sha256"}



def _reject_obsolete(document: Mapping[str, Any], label: str) -> None:
    if document.get("schema") in {"omp.review-pass.v2", "omp.review-receipt.v2", "omp.review-result.v2"}:
        raise GateError(f"{label}: {OBSOLETE_SCHEMA_MESSAGE}")


def gate_pass_path(repo: Path, path: Path, reviewer: str) -> Path:
    repo = repo.resolve()
    if reviewer not in REVIEWERS:
        raise GateError(f"unknown canonical reviewer {reviewer!r}")
    expected = (repo / PASS_DIRECTORY / f"{reviewer}.json").resolve()
    actual = path.expanduser().resolve(strict=False)
    if actual != expected:
        raise GateError(f"review pass {path} is not the gate-owned artifact {expected.relative_to(repo).as_posix()}")
    if not actual.is_file():
        raise GateError(f"missing gate-owned review pass artifact {actual}")
    return actual

def pass_artifact(repo: Path, path: Path, reviewer: str) -> dict[str, str]:
    root = repo.resolve()
    artifact = gate_pass_path(root, path, reviewer)
    return {"path": artifact.relative_to(root).as_posix(), "sha256": sha256_bytes(artifact.read_bytes())}


def _bounded_text(value: object, label: str, maximum: int = 4096) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise GateError(f"{label} must be a non-empty string of at most {maximum} characters")
    if any(ord(character) < 0x20 and character not in "\n\t" for character in value):
        raise GateError(f"{label} must not contain control characters")
    return value


def _validate_location(location: object, label: str) -> dict[str, Any]:
    value = mapping(location, label)
    path = value.get("path")
    if not isinstance(path, str) or not path or Path(path).is_absolute() or ".." in Path(path).parts:
        raise GateError(f"{label}.path must be a repository-relative path")
    normalized = Path(path).as_posix()
    if normalized != path or normalized == ".":
        raise GateError(f"{label}.path must be normalized")
    result: dict[str, Any] = {"path": path}
    for field in ("line_start", "line_end"):
        if field in value:
            line = value[field]
            if not isinstance(line, int) or isinstance(line, bool) or line < 1:
                raise GateError(f"{label}.{field} must be a positive integer")
            result[field] = line
    if "line_start" in result and "line_end" in result and result["line_end"] < result["line_start"]:
        raise GateError(f"{label}.line_end must not precede line_start")
    return result


def _validate_findings(value: object, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > 256:
        raise GateError(f"{label} must be a bounded array of finding objects")
    findings: list[dict[str, Any]] = []
    for index, raw in enumerate(value):
        finding = mapping(raw, f"{label}[{index}]")
        severity = finding.get("severity")
        if severity not in FINDING_SEVERITIES:
            raise GateError(f"{label}[{index}].severity is unsupported")
        title = _bounded_text(finding.get("title"), f"{label}[{index}].title")
        evidence = _bounded_text(finding.get("evidence"), f"{label}[{index}].evidence")
        locations = finding.get("locations")
        if not isinstance(locations, list) or len(locations) > 64:
            raise GateError(f"{label}[{index}].locations must be a bounded array")
        findings.append(
            {
                "severity": severity,
                "title": title,
                "evidence": evidence,
                "locations": [_validate_location(item, f"{label}[{index}].locations[{loc_index}]") for loc_index, item in enumerate(locations)],
            }
        )
    return findings


def _validate_result(
    result: Mapping[str, Any],
    reviewer: str,
    identity: Mapping[str, Any],
) -> dict[str, Any]:
    _reject_obsolete(result, "review result")
    if result.get("schema") != RESULT_SCHEMA:
        raise GateError(f"review result must declare schema {RESULT_SCHEMA}")
    forbidden = FORBIDDEN_RESULT_FIELDS.intersection(result)
    if forbidden:
        raise GateError(f"review result must not contain gate-owned fields: {', '.join(sorted(forbidden))}")
    if result.get("reviewer") != reviewer:
        raise GateError(f"review result reviewer must identify {reviewer}")
    for field in ("old_oid", "new_oid", "bundle_digest", "skill_sha256"):
        expected = skill_identity(reviewer)["sha256"] if field == "skill_sha256" else identity.get(field)
        if field in result and result.get(field) != expected:
            raise GateError(f"review result {field} does not match the frozen identity")
    if result.get("old_oid") != identity.get("old_oid") or result.get("new_oid") != identity.get("new_oid") or result.get("bundle_digest") != identity.get("bundle_digest"):
        raise GateError("review result does not match the frozen committed-range bundle")
    status = result.get("status")
    if status not in {"clean", "findings", "failed", "unavailable"}:
        raise GateError(f"review result has unsupported status {status!r}")
    actionable = nonnegative_int(result.get("actionable_findings"), "review result actionable_findings")
    findings = _validate_findings(result.get("findings"), "review result findings")
    if status == "clean" and (findings or actionable != 0):
        raise GateError("clean review result must contain no findings and actionable_findings=0")
    if status == "findings" and (not findings or actionable != len(findings)):
        raise GateError("findings review result must have one actionable count per finding")
    if status in {"failed", "unavailable"}:
        _bounded_text(result.get("error"), "review result error")
    normalized = dict(result)
    normalized["findings"] = findings
    normalized["actionable_findings"] = actionable
    return normalized


def _adapter_attestation(repo: Path, adapter: object) -> dict[str, str]:
    value = mapping(adapter, "review pass adapter")
    fields = {field: value.get(field) for field in ("name", "executable", "executable_sha256", "engine")}
    for field, item in fields.items():
        if not isinstance(item, str) or not item or len(item) > 256 or any(ord(char) < 0x20 or ord(char) == 0x7F for char in item):
            raise GateError(f"review pass adapter.{field} is invalid")
    if not DIGEST_PATTERN.fullmatch(fields["executable_sha256"]):
        raise GateError("review pass adapter.executable_sha256 must be a sha256 digest")
    executable = Path(fields["executable"]).expanduser()
    if not executable.is_absolute():
        executable = Path(__file__).resolve().parents[1] / executable
    try:
        executable = executable.resolve(strict=True)
    except OSError as error:
        raise GateError(f"review pass adapter executable is unavailable: {fields['executable']}") from error
    if not executable.is_file() or sha256_bytes(executable.read_bytes()) != fields["executable_sha256"]:
        raise GateError("review pass adapter executable digest does not match")
    return fields


def _validate_pass_document(repo: Path, path: Path, reviewer: str, identity: Mapping[str, Any]) -> dict[str, Any]:
    artifact = gate_pass_path(repo, path, reviewer)
    document = read_json(artifact, f"review pass {artifact}")
    _reject_obsolete(document, f"review pass {artifact}")
    if document.get("schema") != PASS_SCHEMA or document.get("kind") != "review-pass":
        raise GateError(f"review pass {artifact} must declare schema {PASS_SCHEMA}")
    assert_same_identity(identity_from_document(document, f"review pass {artifact}"), dict(identity), f"review pass {artifact}")
    if document.get("reviewer") != reviewer:
        raise GateError(f"review pass {artifact} is for {document.get('reviewer')!r}, expected {reviewer!r}")
    skill = skill_identity(reviewer)
    if document.get("skill") != skill:
        raise GateError(f"review pass {artifact} is not bound to the canonical skill bytes")
    worker = mapping(document.get("worker"), f"review pass {artifact}.worker")
    if set(worker) != {"actor", "harness", "model", "run_id"}:
        raise GateError(f"review pass {artifact}.worker must contain explicit actor, harness, model, and run_id")
    if worker_attribution(worker.get("actor"), worker.get("harness"), worker.get("model"), worker.get("run_id")) != worker:
        raise GateError(f"review pass {artifact}.worker attribution is invalid")
    raw_result = mapping(document.get("raw_result"), f"review pass {artifact}.raw_result")
    normalized = _validate_result(raw_result, reviewer, identity)
    if document.get("raw_result_sha256") != sha256_bytes(canonical_json(raw_result)):
        raise GateError(f"review pass {artifact}.raw_result_sha256 does not match raw_result")
    if document.get("status") != normalized["status"] or document.get("actionable_findings") != normalized["actionable_findings"] or document.get("findings") != normalized["findings"]:
        raise GateError(f"review pass {artifact} status/findings do not match raw_result")
    if not isinstance(document.get("submitted_at"), str) or not document["submitted_at"]:
        raise GateError(f"review pass {artifact}.submitted_at must be a timestamp")
    if "adapter" in document:
        _adapter_attestation(repo, document["adapter"])
    return document


def pass_document(path: Path, expected: str, identity: Mapping[str, Any], *, repo: Path) -> dict[str, Any]:
    """Read and validate one gate-owned v3 pass artifact."""
    return _validate_pass_document(repo, path, expected, identity)

def submit_result(
    repo: Path,
    freeze_file: Path,
    reviewer: str,
    attribution: Mapping[str, Any],
    result: Mapping[str, Any],
    adapter: Mapping[str, Any] | None = None,
) -> Path:
    """Validate one v1 result and atomically create its gate-owned v3 pass."""
    repo = repo.resolve()
    if reviewer not in REVIEWERS:
        raise GateError(f"unknown canonical reviewer {reviewer!r}")
    _, frozen = load_freeze(repo, freeze_file)
    current = bundle_from_git(repo, frozen["old_oid"], frozen["new_oid"], check_worktree=True)
    assert_same_identity(frozen, current, "review freeze")
    planned_lanes = frozen.get("planned_lanes", floor_plan(frozen["paths"]))
    if reviewer not in planned_lanes:
        raise GateError(f"reviewer {reviewer!r} is not in the frozen planned lanes {planned_lanes}")
    worker = worker_attribution(attribution.get("actor"), attribution.get("harness"), attribution.get("model"), attribution.get("run_id"))
    if set(attribution) != {"actor", "harness", "model", "run_id"}:
        raise GateError("worker attribution must contain only actor, harness, model, and run_id")
    if reviewer == "autoreview" and adapter is None:
        raise GateError("autoreview requires an explicit adapter attestation")
    normalized = _validate_result(result, reviewer, frozen)
    document: dict[str, Any] = {
        "schema": PASS_SCHEMA,
        "kind": "review-pass",
        **frozen,
        "reviewer": reviewer,
        "skill": skill_identity(reviewer),
        "worker": worker,
        "status": normalized["status"],
        "actionable_findings": normalized["actionable_findings"],
        "findings": normalized["findings"],
        "submitted_at": now(),
        "raw_result": dict(result),
        "raw_result_sha256": sha256_bytes(canonical_json(result)),
    }
    if adapter is not None:
        document["adapter"] = _adapter_attestation(repo, adapter)
    output = repo / PASS_DIRECTORY / f"{reviewer}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        existing = _validate_pass_document(repo, output, reviewer, frozen)
        existing.pop("submitted_at")
        candidate = document.copy()
        candidate.pop("submitted_at")
        if existing != candidate:
            raise GateError("review pass already exists with different bytes; refreeze before resubmitting")
        return output
    write_json(output, document)
    return output

def clean_passes(passes: list[dict[str, Any]]) -> None:
    for item in passes:
        if item.get("status") != "clean" or item.get("actionable_findings") != 0 or item.get("findings") != []:
            raise GateError(f"reviewer {item.get('reviewer')} did not produce a clean pass; rerun freeze, prepare, submit, and record")


def load_receipt(repo: Path, output: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    repo = repo.resolve()
    document = read_json(output, f"review receipt {output}")
    _reject_obsolete(document, f"review receipt {output}")
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
    """Recompute the range and verify every digest-bound receipt artifact."""
    repo = repo.resolve()
    _reject_obsolete(document, "review receipt")
    assert_same_identity(identity_from_document(document, "review receipt"), identity, "review receipt")
    current = bundle_from_git(repo, identity["old_oid"], identity["new_oid"], check_worktree=True)
    assert_same_identity(current, identity, "review receipt")
    scope = document.get("scope")
    if scope not in {"trivial", "substantive"}:
        raise GateError("review receipt has unsupported scope")
    actual_scope = scope_for_paths(identity["paths"])
    kind = document.get("kind")
    if kind == "waiver":
        waiver = mapping(document.get("waiver"), "review receipt waiver")
        actor = waiver.get("actor")
        reason = waiver.get("reason")
        if not isinstance(actor, str) or not ACTOR_PATTERN.fullmatch(actor):
            raise GateError("review receipt waiver has no valid actor")
        if not isinstance(reason, str) or len(reason.strip()) < 12:
            raise GateError("review receipt waiver has no auditable reason")
        if actual_scope != "trivial" or scope != "trivial":
            raise GateError("trivial waiver cannot authorize substantive policy or code changes")
        return
    if kind != "review":
        raise GateError("review receipt kind must be review or waiver")
    if actual_scope == "trivial" or scope != "substantive":
        raise GateError("substantive review receipt is required for non-trivial changes")
    if document.get("actionable_findings") != 0:
        raise GateError("review receipt cannot authorize actionable findings")
    if document.get("freeze_manifest") != FREEZE_RELATIVE.as_posix():
        raise GateError("review receipt must identify the gate-owned freeze manifest")

    planned_lanes = identity.get("planned_lanes", floor_plan(identity["paths"]))
    required_floor = floor_plan(identity["paths"])
    if not set(required_floor).issubset(set(planned_lanes)):
        raise GateError(f"frozen planned lanes {planned_lanes} do not cover required floor {required_floor}")

    reviewers = document.get("reviewers")
    if not isinstance(reviewers, list) or len(reviewers) != len(planned_lanes):
        raise GateError(f"final receipt must contain exactly the planned passes ({', '.join(planned_lanes)}); rerun freeze, submit all passes, record, then verify")
    seen_runs: set[tuple[str, str]] = set()
    names: list[str] = []
    validated: list[dict[str, Any]] = []
    for index, raw in enumerate(reviewers):
        entry = mapping(raw, f"reviewer receipt {index}")
        reviewer = entry.get("reviewer")
        if reviewer != planned_lanes[index]:
            raise GateError(f"final receipt reviewers must match planned lane order: {', '.join(planned_lanes)}")
        names.append(reviewer)
        artifact = mapping(entry.get("pass_artifact"), f"reviewer receipt {reviewer}.pass_artifact")
        expected_path = (PASS_DIRECTORY / f"{reviewer}.json").as_posix()
        if artifact.get("path") != expected_path or not isinstance(artifact.get("sha256"), str) or not DIGEST_PATTERN.fullmatch(artifact["sha256"]):
            raise GateError(f"reviewer receipt {reviewer} is not bound to its gate-owned pass artifact")
        pass_path = gate_pass_path(repo, repo / expected_path, reviewer)
        if sha256_bytes(pass_path.read_bytes()) != artifact["sha256"]:
            raise GateError(f"reviewer receipt {reviewer} pass artifact changed after record")
        pass_value = _validate_pass_document(repo, pass_path, reviewer, identity)
        embedded = dict(entry)
        embedded.pop("pass_artifact", None)
        if embedded != pass_value:
            raise GateError(f"reviewer receipt {reviewer} does not match its gate-owned pass artifact")
        worker = mapping(pass_value["worker"], f"reviewer receipt {reviewer}.worker")
        run_key = (worker["harness"], worker["run_id"])
        if run_key in seen_runs:
            raise GateError("required passes must use distinct harness and run identities")
        seen_runs.add(run_key)
        validated.append(pass_value)
    if names != list(planned_lanes):
        raise GateError(f"final receipt must contain exactly the planned pass artifacts ({', '.join(planned_lanes)})")
    clean_passes(validated)


def record_receipt(repo: Path, freeze_file: Path, output: Path | None = None) -> Path:
    """Discover, revalidate, and record all required planned reviewer pass files."""
    repo = repo.resolve()
    _, frozen = load_freeze(repo, freeze_file)
    current = bundle_from_git(repo, frozen["old_oid"], frozen["new_oid"], check_worktree=True)
    assert_same_identity(frozen, current, "review freeze")
    planned_lanes = frozen.get("planned_lanes", floor_plan(frozen["paths"]))
    required_floor = floor_plan(frozen["paths"])
    if not set(required_floor).issubset(set(planned_lanes)):
        raise GateError(f"frozen planned lanes {planned_lanes} do not cover required floor {required_floor}")
    passes = [
        _validate_pass_document(repo, repo / PASS_DIRECTORY / f"{reviewer}.json", reviewer, frozen)
        for reviewer in planned_lanes
    ]
    clean_passes(passes)
    run_keys = {(item["worker"]["harness"], item["worker"]["run_id"]) for item in passes}
    if len(run_keys) != len(planned_lanes):
        raise GateError("required passes must use distinct harness and run identities")
    destination = receipt_path(repo, str(output) if output is not None else None)
    document: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "kind": "review",
        **frozen,
        "scope": "substantive",
        "freeze_manifest": FREEZE_RELATIVE.as_posix(),
        "planned_lanes": planned_lanes,
        "reviewers": [
            {**item, "pass_artifact": pass_artifact(repo, repo / PASS_DIRECTORY / f"{reviewer}.json", reviewer)}
            for reviewer, item in zip(planned_lanes, passes, strict=True)
        ],
        "actionable_findings": 0,
        "created_at": now(),
        "protocol": {
            "freeze": "committed Git range and complete introduced history",
            "leaf_reviews": f"dynamic reviewer lanes: {', '.join(planned_lanes)}",
            "pass_artifacts": "gate-authored v3 JSON files under .omp/review-passes, digest-bound and re-read at verification",
            "local_boundary": "local integrity proof, not signer identity or host/root compromise proof",
        },
    }
    write_json(destination, document)
    return destination
