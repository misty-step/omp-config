#!/usr/bin/env python3
"""Optional one-review adapter for the harness-neutral review protocol."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping

from review_bundle import freeze_path, load_freeze, repo_root
from review_common import (
    GateError,
    REVIEW_SPECS,
    RESULT_SCHEMA,
    mapping,
    nonnegative_int,
    sha256_bytes,
    skill_identity,
    worker_attribution,
)
from review_packet import DATASET_BYTES, load_packet
from review_receipt import submit_result

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUTOREVIEW_DEFAULT = PROJECT_ROOT / "global" / "skills" / "autoreview" / "scripts" / "autoreview"
PACKET_DIR = Path(".omp/review-packet")
SUMMARY_LIMIT = 4_096


def _bounded_output(value: str, limit: int = 16_000) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + f"\n[truncated {len(value) - limit} characters]"


def _run_process(command: list[str], cwd: Path, timeout: int) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout,
        )
    except FileNotFoundError:
        return 127, "", f"executable not found: {command[0]}"
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout if isinstance(error.stdout, str) else ""
        stderr = error.stderr if isinstance(error.stderr, str) else ""
        return 124, stdout, f"review timed out after {timeout}s\n{stderr}"
    except OSError as error:
        return 126, "", f"review command failed to start: {error}"
    return result.returncode, result.stdout, result.stderr


def _read_report(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise GateError(f"review worker did not produce valid JSON: {error}") from error
    return mapping(value, f"review worker report {path}")


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        first_newline = stripped.find("\n")
        if first_newline != -1:
            return stripped[first_newline + 1 : -3].strip()
    return stripped


def _load_report(path: Path, stdout: str, label: str) -> dict[str, Any] | None:
    if path.is_file():
        try:
            return _read_report(path)
        except GateError:
            pass
    if stdout.strip():
        try:
            return mapping(json.loads(_strip_code_fence(stdout)), label)
        except (json.JSONDecodeError, GateError):
            pass
    return None




def _report_finding_count(report: Mapping[str, Any], reviewer: str) -> int:
    raw_findings = report.get("findings")
    if raw_findings is not None and not isinstance(raw_findings, list):
        raise GateError(f"{reviewer} worker findings must be a list when present")
    listed = len(raw_findings) if isinstance(raw_findings, list) else 0
    declared_value = report.get("actionable_findings")
    if declared_value is None:
        if raw_findings is None:
            raise GateError(f"{reviewer} worker must report findings or actionable_findings")
        return listed
    return nonnegative_int(declared_value, f"{reviewer} worker actionable_findings")


def _review_summary(report: Mapping[str, Any], reviewer: str, dataset: str) -> dict[str, Any]:
    change_summary = report.get("change_summary")
    if not isinstance(change_summary, str) or not change_summary.strip():
        change_summary = report.get("overall_explanation")
    interface_effects = report.get("interface_effects", [])
    if not isinstance(change_summary, str) or not change_summary.strip() or len(change_summary) > SUMMARY_LIMIT:
        raise GateError(f"{reviewer} dataset {dataset} must provide a compact change_summary")
    if (
        not isinstance(interface_effects, list)
        or len(interface_effects) > 64
        or not all(isinstance(item, str) and item.strip() and len(item) <= SUMMARY_LIMIT for item in interface_effects)
    ):
        raise GateError(f"{reviewer} dataset {dataset} must provide compact interface_effects")
    return {"change_summary": change_summary, "interface_effects": interface_effects}


def _packet_dataset_names(packet: Mapping[str, Any]) -> list[str]:
    datasets = packet.get("datasets")
    if not isinstance(datasets, list):
        raise GateError("review packet datasets must be a list")
    names: list[str] = []
    for raw in datasets:
        entry = mapping(raw, "review packet dataset")
        relative = entry.get("path")
        if not isinstance(relative, str):
            raise GateError("review packet dataset path must be a string")
        path = Path(relative)
        if path.parent != PACKET_DIR:
            raise GateError(f"review packet dataset is outside {PACKET_DIR.as_posix()}")
        names.append(path.name)
    return sorted(names)


def _review_dataset_args(packet: Mapping[str, Any], names: list[str], *, skill_path: str | None = None) -> list[str]:
    allowed = set(_packet_dataset_names(packet))
    if not set(names).issubset(allowed):
        raise GateError("review adapter selected a dataset not listed by the frozen packet")
    args = [argument for name in names for argument in ("--dataset", (PACKET_DIR / name).as_posix())]
    if skill_path is not None:
        args.extend(("--dataset", skill_path))
    return args

def _initialize_packet_repository(workspace: Path) -> None:
    """Give local-mode adapters a clean Git root containing only packet evidence."""
    commands = [
        ["git", "init", "--quiet"],
        ["git", "add", "--force", "."],
        [
            "git",
            "-c",
            "user.name=OMP Review Gate",
            "-c",
            "user.email=review-gate@localhost",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--quiet",
            "--no-verify",
            "-m",
            "immutable review packet",
        ],
    ]
    for command in commands:
        exit_code, _stdout, stderr = _run_process(command, workspace, 30)
        if exit_code != 0:
            raise GateError(stderr.strip() or f"cannot initialize packet repository: {command[1]}")


@contextmanager
def _packet_workspace(
    repo: Path,
    packet: Mapping[str, Any],
    reviewer: str,
    extra_files: Mapping[str, bytes] | None = None,
) -> Iterator[tuple[Path, Path]]:
    """Expose only immutable packet datasets and the canonical skill to one worker."""
    with tempfile.TemporaryDirectory(prefix="omp-review-packet-") as temporary:
        workspace = Path(temporary)
        packet_root = workspace / PACKET_DIR
        packet_root.mkdir(parents=True)
        for name in _packet_dataset_names(packet):
            source = (repo / PACKET_DIR / name).resolve(strict=True)
            if not source.is_file():
                raise GateError(f"review packet dataset is not a regular file: {name}")
            destination = packet_root / name
            shutil.copyfile(source, destination)
            destination.chmod(0o444)
        for name, content in (extra_files or {}).items():
            if Path(name).name != name:
                raise GateError(f"review worker extra file has an unsafe name: {name}")
            destination = packet_root / name
            destination.write_bytes(content)
            destination.chmod(0o444)
        skill_source = (PROJECT_ROOT / Path(skill_identity(reviewer)["path"])).resolve(strict=True)
        skill_destination = packet_root / "review-skill.md"
        shutil.copyfile(skill_source, skill_destination)
        skill_destination.chmod(0o444)
        _initialize_packet_repository(workspace)
        packet_root.chmod(0o555)
        yield workspace, skill_destination

def _run_packet_command(
    repo: Path,
    packet: Mapping[str, Any],
    reviewer: str,
    command: list[str],
    timeout: int,
    extra_files: Mapping[str, bytes] | None = None,
) -> tuple[int, str, str]:
    with _packet_workspace(repo, packet, reviewer, extra_files) as (workspace, _skill_path):
        return _run_process(command, workspace, timeout)

def _adapter_command(
    executable: Path,
    engine: str,
    model: str,
    thinking: str | None,
    prompt: str,
    datasets: list[str],
    report_path: Path,
) -> list[str]:
    """Build the one explicit worker invocation shared by every reviewer."""
    command = [
        str(executable),
        "--mode",
        "local",
    ]
    if engine != "codex":
        command.append("--no-tools")
    command.extend(
        [
            "--engine",
            engine,
            "--model",
            model,
        ]
    )
    if thinking is not None:
        command.extend(("--thinking", thinking))
    command.extend(("--prompt", prompt, *datasets, "--json-output", str(report_path)))
    return command


def run_autoreview_chunks(
    identity: Mapping[str, Any],
    repo: Path,
    packet: Mapping[str, Any],
    timeout: int,
    report_temp: Path,
    executable: Path,
    engine: str,
    model: str,
    thinking: str | None,
) -> dict[str, Any]:
    """Run bounded autoreview datasets; status and receipt ownership stay in core."""
    review_names = [name for name in _packet_dataset_names(packet) if name.startswith("bundle.review.") and name.endswith(".diff")]
    if not review_names:
        raise GateError("review packet has no autoreview datasets")
    reports: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    exit_codes: list[int] = []
    actionable_findings = 0
    unavailable = False
    failed = False
    for index, review_name in enumerate(review_names):
        report_path = report_temp / f"autoreview.{index:03d}.raw.json"
        report_path.unlink(missing_ok=True)
        prompt = (
            f"Review immutable committed-range dataset chunk {index + 1} of {len(review_names)}. "
            "Report findings grounded in this chunk plus a compact change_summary string and "
            "interface_effects string array. Return actionable_findings as a non-negative integer "
            "when findings is absent or empty, and include overall_correctness. Do not return a "
            f"{RESULT_SCHEMA} envelope."
        )
        command = _adapter_command(
            executable,
            engine,
            model,
            thinking,
            prompt,
            [
                *_review_dataset_args(
                    packet,
                    ["freeze.json", "evidence.json", review_name],
                    skill_path=(PACKET_DIR / "review-skill.md").as_posix(),
                )
            ],
            report_path,
        )
        exit_code, stdout, stderr = _run_packet_command(command=command, repo=repo, packet=packet, reviewer="autoreview", timeout=timeout)
        exit_codes.append(exit_code)
        report = _load_report(report_path, stdout, "autoreview worker report")
        if report is None:
            reports.append({"dataset": review_name, "error": stderr.strip() or "missing structured report"})
            actionable_findings += 1
            failed = True
            unavailable = unavailable or exit_code == 127
            continue
        try:
            summary = _review_summary(report, "autoreview", review_name)
            finding_entries = _validated_findings(report, "autoreview")
            count = len(finding_entries)
        except GateError as error:
            reports.append({"dataset": review_name, "report": report, "error": str(error)})
            actionable_findings += 1
            failed = True
            continue
        findings.extend(finding_entries)
        reports.append({"dataset": review_name, "report": report, **summary})
        entries.append(
            {
                "dataset": review_name,
                **summary,
                "findings": finding_entries,
                "actionable_findings": count,
            }
        )
        actionable_findings += count
        if (exit_code != 0 and count == 0) or report.get("overall_correctness") not in {"patch is correct", "patch is incorrect"}:
            failed = True
    return {
        "review_names": review_names,
        "reports": reports,
        "entries": entries,
        "findings": findings,
        "actionable_findings": actionable_findings,
        "exit_codes": exit_codes,
        "unavailable": unavailable,
        "failed": failed,
    }


def run_autoreview_integration(
    identity: Mapping[str, Any],
    repo: Path,
    packet: Mapping[str, Any],
    timeout: int,
    report_temp: Path,
    executable: Path,
    engine: str,
    model: str,
    thinking: str | None,
    chunks: Mapping[str, Any],
) -> dict[str, Any]:
    """Run the bounded cross-chunk reducer as adapter-only evidence."""
    review_names = chunks["review_names"]
    entries = chunks["entries"]
    if len(entries) != len(review_names) or chunks["unavailable"]:
        return {
            "integration": {"error": "cross-chunk integration skipped because a dataset pass was unavailable or invalid"},
            "findings": [],
            "actionable_findings": 0,
            "exit_codes": [],
            "failed": True,
        }
    integration_bytes = (
        json.dumps(
            {"schema": "omp.review-integration.v1", "bundle_digest": identity["bundle_digest"], "chunks": entries},
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    if len(integration_bytes) > DATASET_BYTES:
        return {
            "integration": {"error": "cross-chunk integration evidence exceeded the bounded dataset size"},
            "findings": [],
            "actionable_findings": 1,
            "exit_codes": [],
            "failed": True,
        }
    integration_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=".omp-review-integration-", suffix=".json", dir=report_temp, delete=False
        ) as handle:
            integration_path = Path(handle.name)
            handle.write(integration_bytes)
        integration_path.chmod(0o444)
        report_path = report_temp / "autoreview.integration.raw.json"
        report_path.unlink(missing_ok=True)
        prompt = (
            "Review cross-file, cross-config, and interface interactions using the immutable packet "
            "and bounded chunk summaries. Return only findings, actionable_findings, and "
            f"overall_correctness; do not return a {RESULT_SCHEMA} envelope."
        )
        command = _adapter_command(
            executable,
            engine,
            model,
            thinking,
            prompt,
            [
                *_review_dataset_args(
                    packet,
                    ["freeze.json", "evidence.json"],
                    skill_path=(PACKET_DIR / "review-skill.md").as_posix(),
                ),
                "--dataset",
                (PACKET_DIR / "autoreview.integration.json").as_posix(),
            ],
            report_path,
        )
        exit_code, stdout, stderr = _run_packet_command(
            command=command,
            repo=repo,
            packet=packet,
            reviewer="autoreview",
            timeout=timeout,
            extra_files={"autoreview.integration.json": integration_bytes},
        )
        report = _load_report(report_path, stdout, "autoreview integration report")
        if report is None:
            return {
                "integration": {"error": stderr.strip() or "missing structured integration report"},
                "findings": [],
                "actionable_findings": 1,
                "exit_codes": [exit_code],
                "failed": True,
            }
        try:
            finding_entries = _validated_findings(report, "autoreview")
            count = len(finding_entries)
        except GateError as error:
            return {
                "integration": {"report": report, "error": str(error)},
                "findings": [],
                "actionable_findings": 1,
                "exit_codes": [exit_code],
                "failed": True,
            }
        findings = finding_entries
        failed = (exit_code != 0 and count == 0) or report.get("overall_correctness") not in {"patch is correct", "patch is incorrect"}
        return {
            "integration": {"dataset": (PACKET_DIR / "autoreview.integration.json").as_posix(), "report": report},
            "findings": findings,
            "actionable_findings": count,
            "exit_codes": [exit_code],
            "failed": failed,
        }
    finally:
        if integration_path is not None:
            integration_path.unlink(missing_ok=True)


def reduce_autoreview_results(
    chunks: Mapping[str, Any],
    integration: Mapping[str, Any],
) -> dict[str, Any]:
    """Reduce bounded adapter reports without creating a pass or receipt."""
    actionable_findings = chunks["actionable_findings"] + integration["actionable_findings"]
    failed = chunks["failed"] or integration["failed"]
    findings = [*chunks["findings"], *integration["findings"]]
    raw_report = {
        "findings": findings,
        "overall_correctness": "patch is correct" if actionable_findings == 0 and not failed else "patch is incorrect",
        "chunks": chunks["reports"],
        "integration": integration["integration"],
    }
    exit_code = next((code for code in [*chunks["exit_codes"], *integration["exit_codes"]] if code != 0), 0)
    if chunks["unavailable"]:
        status = "unavailable"
    elif actionable_findings != len(findings):
        status = "failed"
    elif actionable_findings > 0:
        status = "findings"
    elif failed:
        status = "failed"
    else:
        status = "clean"
    return {
        "status": status,
        "actionable_findings": actionable_findings,
        "findings": findings,
        "exit_code": exit_code,
        "report": raw_report,
    }


def _normalize_findings(report: Mapping[str, Any], reviewer: str) -> list[dict[str, Any]]:
    raw_findings = report.get("findings", [])
    if not isinstance(raw_findings, list):
        raise GateError(f"{reviewer} worker findings must be a list when present")
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_findings):
        finding = mapping(raw, f"{reviewer} finding {index}")
        severity = finding.get("severity")
        if severity is None:
            severity = {"P0": "blocking", "P1": "high", "P2": "medium", "P3": "low"}.get(finding.get("priority"))
        title = finding.get("title") or finding.get("summary")
        evidence = finding.get("evidence") or finding.get("body") or finding.get("description") or finding.get("why")
        if severity not in {"blocking", "high", "medium", "low"}:
            raise GateError(f"{reviewer} finding {index} must declare a v1 severity or priority")
        if not isinstance(title, str) or not title.strip():
            raise GateError(f"{reviewer} finding {index} must declare a v1 title")
        if not isinstance(evidence, str) or not evidence.strip():
            raise GateError(f"{reviewer} finding {index} must declare v1 evidence")
        locations = finding.get("locations")
        if locations is None and isinstance(finding.get("code_location"), dict):
            location = mapping(finding["code_location"], f"{reviewer} finding {index}.code_location")
            locations = [
                {
                    "path": location.get("file_path"),
                    "line_start": location.get("line"),
                    "line_end": location.get("line"),
                }
            ]
        if locations is None:
            locations = []
        if not isinstance(locations, list):
            raise GateError(f"{reviewer} finding {index} locations must be a list")
        normalized.append({"severity": severity, "title": title, "evidence": evidence, "locations": locations})
    return normalized


def _validated_findings(
    report: Mapping[str, Any], reviewer: str, *, require_count_match: bool = True
) -> list[dict[str, Any]]:
    findings = _normalize_findings(report, reviewer)
    if require_count_match and _report_finding_count(report, reviewer) != len(findings):
        raise GateError(f"{reviewer} worker actionable_findings does not match normalized v1 findings")
    return findings


def _result_document(
    identity: Mapping[str, Any],
    packet: Mapping[str, Any],
    reviewer: str,
    report: Mapping[str, Any],
    *,
    exit_code: int,
    status: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    findings = _validated_findings(report, reviewer, require_count_match=error is None)
    result_status = status or ("findings" if findings else "clean")
    if error is not None:
        result_status = "unavailable" if exit_code == 127 else "failed"
    result: dict[str, Any] = {
        "schema": RESULT_SCHEMA,
        "reviewer": reviewer,
        "old_oid": identity["old_oid"],
        "new_oid": identity["new_oid"],
        "bundle_digest": identity["bundle_digest"],
        "packet_digest": packet["packet_digest"],
        "skill_sha256": skill_identity(reviewer)["sha256"],
        "status": result_status,
        "actionable_findings": len(findings),
        "findings": findings,
    }
    if error is not None:
        result["error"] = _bounded_output(error, 4_096)
    return result


def _run_autoreview(
    identity: Mapping[str, Any],
    repo: Path,
    packet: Mapping[str, Any],
    executable: Path,
    engine: str,
    model: str,
    thinking: str | None,
    timeout: int,
    report_temp: Path,
) -> dict[str, Any]:
    chunks = run_autoreview_chunks(identity, repo, packet, timeout, report_temp, executable, engine, model, thinking)
    integration = run_autoreview_integration(
        identity, repo, packet, timeout, report_temp, executable, engine, model, thinking, chunks
    )
    reduced = reduce_autoreview_results(chunks, integration)
    return _result_document(
        identity,
        packet,
        "autoreview",
        reduced["report"],
        exit_code=reduced["exit_code"],
        status=reduced["status"],
        error=("autoreview worker invocation failed" if reduced["status"] in {"failed", "unavailable"} else None),
    )


def _run_direct_leaf(
    identity: Mapping[str, Any],
    repo: Path,
    packet: Mapping[str, Any],
    reviewer: str,
    executable: Path,
    engine: str,
    model: str,
    thinking: str | None,
    timeout: int,
    report_temp: Path,
) -> dict[str, Any]:
    skill_identity(reviewer)
    skill_path = PACKET_DIR / "review-skill.md"
    dataset_names = [name for name in _packet_dataset_names(packet) if name not in {"freeze.json", "evidence.json"}]
    report_path = report_temp / f"{reviewer}.raw.json"
    prompt = (
        f"Apply the canonical {reviewer} review skill from {skill_path.as_posix()} without rewriting or "
        "summarizing its bytes. Review only the immutable packet datasets and return a JSON object with "
        "findings, actionable_findings, and any supporting explanation. Do not return a review pass or "
        f"{RESULT_SCHEMA} envelope."
    )
    command = _adapter_command(
        executable,
        engine,
        model,
        thinking,
        prompt,
        [
            *_review_dataset_args(
                packet,
                ["freeze.json", "evidence.json", *dataset_names],
                skill_path=skill_path.as_posix(),
            )
        ],
        report_path,
    )
    exit_code, stdout, stderr = _run_packet_command(
        command=command,
        repo=repo,
        packet=packet,
        reviewer=reviewer,
        timeout=timeout,
    )
    report = _load_report(report_path, stdout, f"{reviewer} worker report")
    if report is None:
        return _result_document(
            identity,
            packet,
            reviewer,
            {"findings": [], "actionable_findings": 0},
            exit_code=exit_code,
            error=stderr.strip() or "missing structured report",
        )
    findings = _validated_findings(report, reviewer)
    error = None if exit_code == 0 or findings else (stderr.strip() or "worker exited without actionable findings")
    status = "findings" if findings else None
    return _result_document(identity, packet, reviewer, report, exit_code=exit_code, status=status, error=error)


def _executable(raw: str | None) -> Path:
    path = Path(raw or AUTOREVIEW_DEFAULT).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    try:
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise GateError(f"review adapter executable is unavailable: {path}") from error
    if not resolved.is_file():
        raise GateError(f"review adapter executable is not a regular file: {resolved}")
    return resolved


def _adapter_attestation(executable: Path, engine: str) -> dict[str, str]:
    try:
        executable_value = executable.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        executable_value = str(executable)
    return {
        "name": "review_runner",
        "executable": executable_value,
        "executable_sha256": sha256_bytes(executable.read_bytes()),
        "engine": engine,
    }


def run_one(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    freeze_file = freeze_path(repo, args.freeze)
    _, identity = load_freeze(repo, freeze_file)
    reviewer = args.reviewer
    if reviewer not in REVIEW_SPECS:
        raise GateError(f"unknown canonical reviewer {reviewer!r}")
    packet = load_packet(repo, identity)
    attribution = worker_attribution(args.actor, args.harness, args.model, args.run_id)
    executable = _executable(getattr(args, "executable", None))
    adapter = _adapter_attestation(executable, args.engine) if reviewer == "autoreview" else None
    timeout = getattr(args, "timeout", 1800)
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout < 1:
        raise GateError("review timeout must be a positive integer")
    thinking = getattr(args, "thinking", None)
    with tempfile.TemporaryDirectory(prefix="omp-review-runner-") as report_dir:
        if reviewer == "autoreview":
            result = _run_autoreview(identity, repo, packet, executable, args.engine, args.model, thinking, timeout, Path(report_dir))
        else:
            result = _run_direct_leaf(
                identity,
                repo,
                packet,
                reviewer,
                executable,
                args.engine,
                args.model,
                thinking,
                timeout,
                Path(report_dir),
            )
    load_packet(repo, identity)
    output = submit_result(repo, freeze_file, reviewer, attribution, result, adapter)
    print(f"review pass submitted: {output}")
    return 0 if result["status"] == "clean" else 1


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Submit one explicit review result through the canonical protocol seam.")
    sub = root.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run-one", help="run exactly one configured reviewer and submit its v1 result")
    run_parser.add_argument("--repo", default=".")
    run_parser.add_argument("--freeze")
    run_parser.add_argument("--reviewer", choices=tuple(REVIEW_SPECS), required=True)
    run_parser.add_argument("--actor", required=True)
    run_parser.add_argument("--harness", required=True)
    run_parser.add_argument("--engine", required=True)
    run_parser.add_argument("--model", required=True)
    run_parser.add_argument("--run-id", required=True)
    run_parser.add_argument("--thinking")
    run_parser.add_argument("--timeout", type=int, default=1800)
    run_parser.add_argument("--executable", default=str(AUTOREVIEW_DEFAULT))
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "run-one":
            return run_one(args)
        raise GateError(f"unsupported review runner command {args.command!r}")
    except (GateError, OSError, ValueError) as error:
        print(f"review-runner: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
