#!/usr/bin/env python3
"""Run the pinned three-pass review wave over one immutable evidence packet."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from argparse import Namespace
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from review_bundle import bundle_from_git, freeze_path, load_freeze, receipt_path, repo_root
from review_common import (
    GateError,
    PASS_DIRECTORY,
    PASS_SCHEMA,
    mapping,
    nonnegative_int,
    sha256_bytes,
    unresolved_worker,
    worker_identity,
    review_scope,
    write_json,
)
from review_receipt import record_receipt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUTOREVIEW_FORK = PROJECT_ROOT / "global" / "external" / "openclaw-autoreview"
if str(AUTOREVIEW_FORK) not in sys.path:
    sys.path.insert(0, str(AUTOREVIEW_FORK))
_prior_bytecode_policy = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    import openclaw_autoreview as autoreview_security
finally:
    sys.dont_write_bytecode = _prior_bytecode_policy
AUTOREVIEW_DEFAULT = PROJECT_ROOT / "global" / "skills" / "autoreview" / "scripts" / "autoreview"
THERMO_SKILLS = {
    "thermo-nuclear-review": PROJECT_ROOT / "global" / "skills" / "thermo-nuclear-review" / "SKILL.md",
    "thermo-nuclear-code-quality-review": PROJECT_ROOT / "global" / "skills" / "thermo-nuclear-code-quality-review" / "SKILL.md",
}
# Thermos skills are public payloads. Pi carries them through the authenticated
# openai-codex subscription; neither Cursor nor Anthropic OAuth is required.
THERMO_ENGINE = "pi"
THERMO_MODEL = "openai-codex/gpt-5.6-sol"
THERMO_VENDOR = PROJECT_ROOT / "global" / "external" / "cursor-thermos"
PACKET_DIR = ".omp-review-packet"
TARGET_PREFIX = ".omp-review-target-"
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
AUTOREVIEW_DATASET_BYTES = 160_000
AUTOREVIEW_TRANSPORT_RISK_HINT = re.compile(
    r"(?i)(?:secret|password|credential|authorization|private[_ -]?key|"
    r"(?:access|refresh|oauth|bearer|session|auth)[_ -]?token|api[_ -]?key)"
)
AUTOREVIEW_REDACTED_VALUE = re.compile(r"(?i)(?:=|:\s*)[\"']?redacted\b")



def _comment_frame_diff_hunks(unit: str) -> str:
    annotated: list[str] = []
    in_hunk = False
    labels = {"+": "# > added | ", "-": "# > removed | ", " ": "# > context | "}
    for line in unit.splitlines(keepends=True):
        if line.startswith("diff --git "):
            in_hunk = False
        elif line.startswith("@@ "):
            in_hunk = True
            closing = line.find("@@", 3)
            ending = "\n" if line.endswith("\n") else ""
            annotated.append(line[: closing + 2] + ending if closing >= 0 else line)
            continue
        if in_hunk and line[:1] in labels and not line.startswith("@@ "):
            annotated.append(labels[line[0]] + line[1:])
        else:
            annotated.append(line)
    return "".join(annotated)


def _omit_transport_risk_lines(unit: str, scanner: Any) -> str:
    retained: list[str] = []
    for line in unit.splitlines(keepends=True):
        if (
            AUTOREVIEW_TRANSPORT_RISK_HINT.search(line)
            and AUTOREVIEW_REDACTED_VALUE.search(line) is None
        ) or scanner.secret_text_risk(line):
            prefix = "# > " if line.startswith("# > ") else "# "
            ending = "\n" if line.endswith("\n") else ""
            retained.append(f"{prefix}[source line omitted after path-dialect scan]{ending}")
        else:
            retained.append(line)
    return "".join(retained)


def _redact_secret_like_values(diff: bytes) -> bytes:
    scanner = autoreview_security
    redacted: list[str] = []
    for unit in scanner.review_bundle_units(diff.decode("utf-8", errors="replace")):
        old_path, new_path = scanner.diff_section_paths(unit)
        review_path = new_path or old_path
        dialect = scanner.javascript_review_dialect(review_path) if review_path is not None else None
        unit = scanner.redact_review_patch_metadata(unit)
        spans = scanner.review_repeatable_secret_spans(unit, javascript_dialect=dialect)
        unit = scanner.redact_review_spans(unit, spans)
        old_content, new_content = scanner.unified_diff_contents(unit)
        if scanner.secret_text_risk(old_content, javascript_dialect=dialect) or scanner.secret_text_risk(
            new_content,
            javascript_dialect=dialect,
        ):
            raise GateError(f"cannot safely redact credential-shaped review evidence in {new_path or old_path or 'diff metadata'}")
        if unit.startswith("diff --git "):
            unit = _comment_frame_diff_hunks(unit)
            unit = _omit_transport_risk_lines(unit, scanner)
        if scanner.secret_text_risk(unit):
            raise GateError(f"cannot safely frame credential-shaped review evidence in {review_path or 'diff metadata'}")
        redacted.append(unit)
    return "".join(redacted).encode("utf-8")

def _target_name(identity: dict[str, Any]) -> str:
    digest = str(identity["bundle_digest"]).removeprefix("sha256:")
    return f"{TARGET_PREFIX}{digest[:16]}.txt"


def _compact_deleted_files(diff: bytes) -> bytes:
    sections: list[list[bytes]] = []
    current: list[bytes] = []
    for line in diff.splitlines(keepends=True):
        if line.startswith(b"diff --git ") and current:
            sections.append(current)
            current = []
        current.append(line)
    if current:
        sections.append(current)

    compacted: list[bytes] = []
    for section in sections:
        deleted = any(line.startswith(b"deleted file mode ") for line in section)
        deleted = deleted and any(line.startswith(b"+++ /dev/null") for line in section)
        if not deleted:
            compacted.extend(section)
            continue
        removed_lines = sum(
            1
            for line in section
            if line.startswith(b"-") and not line.startswith(b"--- ")
        )
        compacted.extend(
            line
            for line in section
            if line.startswith((b"diff --git ", b"deleted file mode ", b"index ", b"--- "))
        )
        compacted.append(
            f"# Entire file deleted; {removed_lines} removed lines omitted from model evidence.\n".encode("ascii")
        )
    return b"".join(compacted)


def _split_oversized_section(section: bytes) -> list[bytes]:
    if len(section) <= AUTOREVIEW_DATASET_BYTES:
        return [section]
    lines = section.splitlines(keepends=True)
    first_hunk = next((index for index, line in enumerate(lines) if line.startswith(b"@@ ")), len(lines))
    header = b"".join(lines[:first_hunk])
    if len(header) >= AUTOREVIEW_DATASET_BYTES:
        raise GateError("committed diff contains metadata too large for bounded review evidence")
    hunk_header = lines[first_hunk] if first_hunk < len(lines) else b"# Continued file diff.\n"
    payload = lines[first_hunk + 1 :] if first_hunk < len(lines) else []
    prefix = header + hunk_header
    pieces: list[bytes] = []
    current = bytearray(prefix)
    for line in payload:
        if len(prefix) + len(line) > AUTOREVIEW_DATASET_BYTES:
            raise GateError("committed diff contains a line too large for bounded review evidence")
        if len(current) + len(line) > AUTOREVIEW_DATASET_BYTES:
            pieces.append(bytes(current))
            current = bytearray(header + b"# Continued hunk from prior review dataset.\n" + hunk_header)
        current.extend(line)
    if current:
        pieces.append(bytes(current))
    return pieces


def _dataset_chunks(diff: bytes) -> list[bytes]:
    compacted = _redact_secret_like_values(_compact_deleted_files(diff))
    sections: list[bytes] = []
    current_section = bytearray()
    for line in compacted.splitlines(keepends=True):
        if line.startswith(b"diff --git ") and current_section:
            sections.append(bytes(current_section))
            current_section.clear()
        current_section.extend(line)
    if current_section:
        sections.append(bytes(current_section))

    chunks: list[bytes] = []
    current = bytearray()
    scanner = autoreview_security
    for section in sections:
        for piece in _split_oversized_section(section):
            candidate = bytes(current) + piece
            if current and (
                len(candidate) > AUTOREVIEW_DATASET_BYTES
                or scanner.secret_text_risk(candidate.decode("utf-8", errors="replace"))
            ):
                chunks.append(bytes(current))
                current.clear()
            if scanner.secret_text_risk(piece.decode("utf-8", errors="replace")):
                raise GateError("cannot safely construct bounded autoreview evidence")
            current.extend(piece)
    if current:
        chunks.append(bytes(current))
    return chunks or [b"# Committed range has no textual diff.\n"]






def _result_envelope(
    identity: dict[str, Any],
    reviewer: str,
    status: str,
    findings: int,
    exit_code: int,
    worker: dict[str, Any],
    raw_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": PASS_SCHEMA,
        **identity,
        "reviewer": reviewer,
        "status": status,
        "actionable_findings": findings,
        "exit_code": exit_code,
        "worker": worker,
        "raw_report": raw_report,
    }


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

def _bounded_output(value: str, limit: int = 16_000) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + f"\n[truncated {len(value) - limit} characters]"


def _read_report(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise GateError(f"review worker did not produce valid JSON: {error}") from error
    return mapping(value, f"review worker report {path}")

SUMMARY_LIMIT = 4_096


def _report_finding_count(report: dict[str, Any], reviewer: str) -> int:
    raw_findings = report.get("findings")
    if raw_findings is not None and not isinstance(raw_findings, list):
        raise GateError(f"{reviewer} worker findings must be a list when present")
    listed = len(raw_findings) if isinstance(raw_findings, list) else 0
    declared_value = report.get("actionable_findings")
    if declared_value is None:
        if raw_findings is None:
            raise GateError(f"{reviewer} worker must report findings or actionable_findings")
        declared = 0
    else:
        declared = nonnegative_int(declared_value, f"{reviewer} worker actionable_findings")
    return max(declared, listed)


def _review_summary(report: dict[str, Any], reviewer: str, dataset: str) -> dict[str, Any]:
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


def _write_packet_file(packet: Path, name: str, content: bytes) -> Path:
    path = packet / name
    if path.exists():
        raise GateError(f"reserved review packet path already exists: {name}")
    packet.chmod(0o755)
    try:
        path.write_bytes(content)
        path.chmod(0o444)
    finally:
        packet.chmod(0o555)
    return path


def _load_autoreview_report(path: Path, stdout: str, label: str) -> dict[str, Any] | None:
    if path.is_file():
        try:
            return _read_report(path)
        except GateError:
            pass
    if stdout.strip():
        try:
            return mapping(json.loads(stdout), label)
        except (json.JSONDecodeError, GateError):
            pass
    return None


def run_autoreview_chunks(
    identity: dict[str, Any],
    worktree: Path,
    timeout: int,
    report_temp: Path,
    worker: dict[str, Any],
) -> dict[str, Any]:
    """Run and parse each bounded dataset; no integration or status reduction."""
    packet = worktree / PACKET_DIR
    review_names = sorted(path.name for path in packet.glob("bundle.review.*.diff"))
    executable = (
        str((PROJECT_ROOT / worker["executable"]).resolve())
        if not Path(worker["executable"]).is_absolute()
        else worker["executable"]
    )
    reports: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    findings: list[Any] = []
    exit_codes: list[int] = []
    actionable_findings = 0
    unavailable = False
    failed = False
    for index, review_name in enumerate(review_names):
        report_path = report_temp / f"autoreview.{index:03d}.raw.json"
        dataset_args = [
            argument
            for name in ("freeze.json", "evidence.json", review_name)
            for argument in ("--dataset", f"{PACKET_DIR}/{name}")
        ]
        command = [
            executable,
            "--mode",
            "local",
            "--engine",
            "codex",
            "--prompt",
            (
                f"{_target_name(identity)} only selects this review. Review immutable committed-range "
                f"dataset chunk {index + 1} of {len(review_names)}, not the marker. Report findings grounded "
                "in this chunk plus a compact change_summary string and interface_effects string array. "
                "Return actionable_findings as a non-negative integer when findings is absent or empty, and "
                "include overall_correctness. Deleted file bodies are omitted; deletion paths and counts remain."
            ),
            *dataset_args,
            "--json-output",
            str(report_path),
        ]
        exit_code, stdout, stderr = _run_process(command, worktree, timeout)
        exit_codes.append(exit_code)
        report = _load_autoreview_report(report_path, stdout, "autoreview worker report")
        if report is None:
            reports.append({"dataset": review_name, "error": stderr.strip() or "missing structured report"})
            actionable_findings += 1
            failed = True
            unavailable = unavailable or exit_code == 127
            continue
        try:
            summary = _review_summary(report, "autoreview", review_name)
            count = _report_finding_count(report, "autoreview")
        except GateError as error:
            reports.append({"dataset": review_name, "report": report, "error": str(error)})
            actionable_findings += 1
            failed = True
            continue
        reports.append({"dataset": review_name, "report": report, **summary})
        raw_findings = report.get("findings")
        if isinstance(raw_findings, list):
            findings.extend({**finding, "dataset": review_name} if isinstance(finding, dict) else finding for finding in raw_findings)
        actionable_findings += count
        entries.append(
            {
                "dataset": review_name,
                **summary,
                "findings": raw_findings if isinstance(raw_findings, list) else [],
                "actionable_findings": count,
            }
        )
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
    identity: dict[str, Any],
    worktree: Path,
    timeout: int,
    report_temp: Path,
    executable: str,
    chunks: dict[str, Any],
) -> dict[str, Any]:
    """Optionally run the cross-chunk pass and return only integration data."""
    packet = worktree / PACKET_DIR
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
    integration_name = "autoreview.integration.json"
    integration_bytes = (
        json.dumps(
            {"schema": "omp.review-integration.v1", "bundle_digest": identity["bundle_digest"], "chunks": entries},
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    if len(integration_bytes) > AUTOREVIEW_DATASET_BYTES:
        return {
            "integration": {"error": "cross-chunk integration evidence exceeded the bounded dataset size"},
            "findings": [],
            "actionable_findings": 1,
            "exit_codes": [],
            "failed": True,
        }
    integration_path = _write_packet_file(packet, integration_name, integration_bytes)
    report_path = report_temp / "autoreview.integration.raw.json"
    command = [
        executable,
        "--mode",
        "local",
        "--engine",
        "codex",
        "--prompt",
        (
            f"{_target_name(identity)} only selects this final integration review. Read the immutable "
            "packet freeze/evidence and all bounded chunk summaries/findings. Review cross-file, "
            "cross-config, and interface interactions. Return only findings, actionable_findings, "
            "and overall_correctness; do not return an omp.review-pass.v2 envelope."
        ),
        "--dataset",
        f"{PACKET_DIR}/freeze.json",
        "--dataset",
        f"{PACKET_DIR}/evidence.json",
        "--dataset",
        f"{PACKET_DIR}/{integration_path.name}",
        "--json-output",
        str(report_path),
    ]
    exit_code, stdout, stderr = _run_process(command, worktree, timeout)
    report = _load_autoreview_report(report_path, stdout, "autoreview integration report")
    if report is None:
        return {
            "integration": {"error": stderr.strip() or "missing structured integration report"},
            "findings": [],
            "actionable_findings": 1,
            "exit_codes": [exit_code],
            "failed": True,
        }
    try:
        count = _report_finding_count(report, "autoreview integration")
    except GateError as error:
        return {
            "integration": {"report": report, "error": str(error)},
            "findings": [],
            "actionable_findings": 1,
            "exit_codes": [exit_code],
            "failed": True,
        }
    raw_findings = report.get("findings")
    findings = (
        [{**finding, "dataset": "integration"} if isinstance(finding, dict) else finding for finding in raw_findings]
        if isinstance(raw_findings, list)
        else []
    )
    failed = (exit_code != 0 and count == 0) or report.get("overall_correctness") not in {"patch is correct", "patch is incorrect"}
    return {
        "integration": {"dataset": integration_path.name, "report": report},
        "findings": findings,
        "actionable_findings": count,
        "exit_codes": [exit_code],
        "failed": failed,
    }


def reduce_autoreview_results(
    identity: dict[str, Any],
    worker: dict[str, Any],
    chunks: dict[str, Any],
    integration: dict[str, Any],
) -> dict[str, Any]:
    """Purely reduce parsed chunk/integration results into the pass envelope."""
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
    elif actionable_findings > 0:
        status = "findings"
    elif failed:
        status = "failed"
    else:
        status = "clean"
    return _result_envelope(identity, "autoreview", status, actionable_findings, exit_code, worker, raw_report)


def _autoreview_pass(
    identity: dict[str, Any],
    worktree: Path,
    timeout: int,
    report_temp: Path,
    worker: dict[str, Any],
) -> dict[str, Any]:
    executable = (
        str((PROJECT_ROOT / worker["executable"]).resolve())
        if not Path(worker["executable"]).is_absolute()
        else worker["executable"]
    )
    chunks = run_autoreview_chunks(identity, worktree, timeout, report_temp, worker)
    integration = run_autoreview_integration(identity, worktree, timeout, report_temp, executable, chunks)
    return reduce_autoreview_results(identity, worker, chunks, integration)


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        first_newline = stripped.find("\n")
        if first_newline != -1:
            return stripped[first_newline + 1 : -3].strip()
    return stripped


def _worker_report(output: str, reviewer: str) -> dict[str, Any]:
    if not output.strip():
        raise GateError(f"{reviewer} worker returned no structured result")
    try:
        value = json.loads(_strip_code_fence(output))
    except json.JSONDecodeError as error:
        raise GateError(f"{reviewer} worker result is not JSON: {error}") from error
    report = mapping(value, f"{reviewer} worker result")
    if report.get("schema") == PASS_SCHEMA:
        raise GateError(f"{reviewer} worker attempted to hand-author an {PASS_SCHEMA} envelope")
    if isinstance(report.get("findings"), list):
        return report
    report["actionable_findings"] = nonnegative_int(report.get("actionable_findings"), f"{reviewer} worker actionable_findings")
    return report


def _initialize_packet_repo(packet_root: Path) -> None:
    commands = (
        ["git", "init", "--quiet"],
        ["git", "add", "--force", PACKET_DIR],
        [
            "git",
            "-c",
            "user.name=OMP Review Gate",
            "-c",
            "user.email=review-gate@localhost",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--no-verify",
            "--quiet",
            "-m",
            "immutable review packet",
        ],
    )
    for command in commands:
        result = subprocess.run(
            command,
            cwd=packet_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode:
            detail = result.stderr.strip() or result.stdout.strip()
            raise GateError(f"cannot initialize isolated review packet repository: {detail}")


def _run_thermo_dataset(
    reviewer: str,
    executable: Path,
    worktree: Path,
    dataset: Path,
    timeout: int,
) -> tuple[int, dict[str, Any] | None, str, str]:
    with (
        tempfile.TemporaryDirectory(prefix="omp-thermo-packet-") as packet_temp,
        tempfile.TemporaryDirectory(prefix="omp-thermo-report-") as report_temp,
    ):
        packet_root = Path(packet_temp)
        packet = packet_root / PACKET_DIR
        shutil.copytree(
            worktree / PACKET_DIR,
            packet,
            ignore=shutil.ignore_patterns("bundle.diff", "bundle.review.*.diff"),
        )
        packet.chmod(0o755)
        shutil.copy2(dataset, packet / dataset.name)
        shutil.copy2(THERMO_SKILLS[reviewer], packet / "review-skill.md")
        _initialize_packet_repo(packet_root)
        for item in packet.rglob("*"):
            if item.is_file():
                item.chmod(0o444)
        packet.chmod(0o555)
        prompt = (
            f"Read only the immutable packet datasets. Apply the public review skill in {PACKET_DIR}/review-skill.md "
            f"to the change chunk in {PACKET_DIR}/{dataset.name}. Do not access files outside this packet workspace, "
            "do not modify packet files, and return only JSON with a findings array or actionable_findings integer. "
            "Do not return an omp.review-pass.v2 envelope."
        )
        report_path = Path(report_temp) / f"{reviewer}.{dataset.stem}.json"
        dataset_names = ("freeze.json", "evidence.json", "review-skill.md", dataset.name)
        dataset_args = [
            argument
            for name in dataset_names
            for argument in ("--dataset", f"{PACKET_DIR}/{name}")
        ]
        command = [
            str(executable),
            "--mode",
            "local",
            "--engine",
            THERMO_ENGINE,
            "--model",
            THERMO_MODEL,
            "--prompt",
            prompt,
            *dataset_args,
            "--json-output",
            str(report_path),
        ]
        exit_code, stdout, stderr = _run_process(command, packet_root, timeout)
        report = _load_autoreview_report(report_path, stdout, f"{reviewer} worker report for {dataset.name}")
        return exit_code, report, stdout, stderr


def _thermo_pass(
    identity: dict[str, Any],
    reviewer: str,
    executable: Path | None,
    worktree: Path,
    timeout: int,
    worker: dict[str, Any],
) -> dict[str, Any]:
    if executable is None:
        return _result_envelope(
            identity,
            reviewer,
            "unavailable",
            1,
            127,
            worker,
            {"error": f"review harness was not found at {AUTOREVIEW_DEFAULT}"},
        )
    datasets = sorted((worktree / PACKET_DIR).glob("bundle.review.*.diff"))
    if not datasets:
        return _result_envelope(
            identity,
            reviewer,
            "failed",
            1,
            2,
            worker,
            {"error": "immutable review packet contains no change chunks"},
        )

    chunk_reports: list[dict[str, Any]] = []
    findings: list[Any] = []
    count_without_details = 0
    for dataset in datasets:
        exit_code, report, stdout, stderr = _run_thermo_dataset(
            reviewer,
            executable,
            worktree,
            dataset,
            timeout,
        )
        try:
            if report is None:
                raise GateError(stderr.strip() or f"{reviewer} worker returned no structured result for {dataset.name}")
            finding_count = _report_finding_count(report, f"{reviewer} worker report for {dataset.name}")
        except GateError as error:
            return _result_envelope(
                identity,
                reviewer,
                "unavailable" if exit_code == 127 else "findings",
                1,
                exit_code if exit_code != 0 else 2,
                worker,
                {
                    "error": str(error),
                    "dataset": dataset.name,
                    "stdout": _bounded_output(stdout),
                    "stderr": _bounded_output(stderr),
                    "chunk_reports": chunk_reports,
                },
            )

        detailed = report.get("findings")
        if isinstance(detailed, list):
            for finding in detailed:
                if isinstance(finding, dict):
                    findings.append({"evidence_dataset": dataset.name, **finding})
                else:
                    findings.append(finding)
            count_without_details += max(0, finding_count - len(detailed))
        else:
            count_without_details += finding_count
        chunk_reports.append(
            {
                "dataset": dataset.name,
                "actionable_findings": finding_count,
                "report": report,
            }
        )
        if exit_code != 0:
            total = len(findings) + count_without_details
            return _result_envelope(
                identity,
                reviewer,
                "findings" if total else "failed",
                total,
                exit_code,
                worker,
                {
                    "findings": findings,
                    "actionable_findings": total,
                    "chunk_reports": chunk_reports,
                    "stderr": _bounded_output(stderr),
                },
            )

    total = len(findings) + count_without_details
    report = {
        "findings": findings,
        "actionable_findings": total,
        "chunk_reports": chunk_reports,
    }
    return _result_envelope(
        identity,
        reviewer,
        "clean" if total == 0 else "findings",
        total,
        0,
        worker,
        report,
    )


def _output_root(repo: Path, raw: str | None) -> Path:
    path = Path(raw or PASS_DIRECTORY).expanduser()
    if not path.is_absolute():
        path = repo / path
    path = path.resolve(strict=False)
    expected = (repo / PASS_DIRECTORY).resolve()
    if path != expected:
        raise GateError(f"review pass output directory must be the gate-owned {PASS_DIRECTORY.as_posix()} directory")
    path.mkdir(parents=True, exist_ok=True)
    return path

def _packet(
    repo: Path,
    worktree: Path,
    freeze_document: dict[str, Any],
    identity: dict[str, Any],
) -> dict[str, bytes]:
    packet = worktree / PACKET_DIR
    packet.mkdir()
    freeze_bytes = (json.dumps(freeze_document, indent=2, sort_keys=True) + "\n").encode("utf-8")
    old_oid = identity["old_oid"] if identity["old_oid"] != "0" * 40 else EMPTY_TREE
    diff_result = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--binary", "--full-index", old_oid, identity["new_oid"], "--"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if diff_result.returncode:
        detail = diff_result.stderr.decode("utf-8", errors="replace").strip()
        raise GateError(f"cannot build immutable committed diff: {detail}")
    diff_bytes = diff_result.stdout
    review_chunks = _dataset_chunks(diff_bytes)
    review_names = [f"bundle.review.{index:03d}.diff" for index in range(len(review_chunks))]
    evidence = {
        "schema": "omp.review-evidence.v1",
        "freeze": freeze_document,
        "bundle_digest": identity["bundle_digest"],
        "committed_diff": "bundle.diff",
        "committed_diff_sha256": sha256_bytes(diff_bytes),
        "autoreview_datasets": review_names,
        "autoreview_evidence_policy": "non-deleted diff with credential values redacted; deletion metadata without removed file bodies",
    }
    evidence_bytes = (json.dumps(evidence, indent=2, sort_keys=True) + "\n").encode("utf-8")
    files = {
        ".gitignore": b"*\n",
        "freeze.json": freeze_bytes,
        "evidence.json": evidence_bytes,
        "bundle.diff": diff_bytes,
        **dict(zip(review_names, review_chunks, strict=True)),
    }
    for name, content in files.items():
        (packet / name).write_bytes(content)
        (packet / name).chmod(0o444)
    target = worktree / _target_name(identity)
    if target.exists():
        raise GateError(f"reserved review selector path already exists: {target.name}")
    target_bytes = f"Review the immutable committed range {identity['bundle_digest']} from {PACKET_DIR}/.\n".encode("utf-8")
    target.write_bytes(target_bytes)
    target.chmod(0o444)
    packet.chmod(0o555)
    return {
        **{str(packet / name): content for name, content in files.items()},
        str(target): target_bytes,
    }


def _worktree_status(worktree: Path) -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all", "--ignored=matching"],
        cwd=worktree,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        raise GateError(f"cannot inspect frozen review worktree: {result.stderr.strip()}")
    return result.stdout


def _assert_packet_unchanged(snapshot: dict[str, bytes], status: str, worktree: Path) -> None:
    if _worktree_status(worktree) != status:
        raise GateError("review worker changed the frozen review worktree")
    for raw_path, expected in snapshot.items():
        path = Path(raw_path)
        if not path.is_file() or path.read_bytes() != expected:
            raise GateError("review worker changed the immutable evidence packet")


def run_command(args: Namespace) -> int:
    repo = repo_root(args.repo)
    freeze_file = freeze_path(repo, args.freeze)
    freeze_document, frozen = load_freeze(repo, freeze_file)
    current = bundle_from_git(repo, frozen["old_oid"], frozen["new_oid"], check_worktree=True)
    if current != frozen:
        raise GateError("review freeze does not match the recomputed committed range")
    if review_scope(frozen["paths"]) == "trivial":
        raise GateError(
            "trivial review range requires an explicit, actor-attributed waiver; run review_gate.py waive"
        )
    output_root = _output_root(repo, getattr(args, "output_dir", None))
    timeout = getattr(args, "timeout", 1800)
    autoreview_path = AUTOREVIEW_DEFAULT
    autoreview_worker = (
        worker_identity("autoreview", autoreview_path, "codex", PROJECT_ROOT / "global" / "external" / "openclaw-autoreview")
        if autoreview_path.is_file()
        else unresolved_worker("autoreview", "codex", str(autoreview_path), PROJECT_ROOT / "global" / "external" / "openclaw-autoreview")
    )
    thermo_path = autoreview_path if autoreview_path.is_file() else None
    thermo_workers = {
        reviewer: (
            worker_identity(reviewer, thermo_path, THERMO_MODEL, THERMO_VENDOR)
            if thermo_path is not None
            else unresolved_worker(reviewer, THERMO_MODEL, str(AUTOREVIEW_DEFAULT), THERMO_VENDOR)
        )
        for reviewer in THERMO_SKILLS
    }
    temp_parent = Path(tempfile.mkdtemp(prefix="omp-review-run-"))
    worktree = temp_parent / "worktree"
    try:
        worktree_result = subprocess.run(
            ["git", "worktree", "add", "--quiet", "--detach", str(worktree), frozen["new_oid"]],
            cwd=repo,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if worktree_result.returncode:
            detail = worktree_result.stderr.strip() or worktree_result.stdout.strip()
            raise GateError(f"cannot create frozen review worktree: {detail}")
        packet_snapshot = _packet(repo, worktree, freeze_document, frozen)
        packet_status = _worktree_status(worktree)
        with tempfile.TemporaryDirectory(prefix="omp-review-reports-") as report_temp:
            report_dir = Path(report_temp)
            jobs = {
                "autoreview": lambda: _autoreview_pass(frozen, worktree, timeout, report_dir, autoreview_worker),
                "thermo-nuclear-review": lambda: _thermo_pass(
                    frozen, "thermo-nuclear-review", thermo_path, worktree, timeout, thermo_workers["thermo-nuclear-review"]
                ),
                "thermo-nuclear-code-quality-review": lambda: _thermo_pass(
                    frozen,
                    "thermo-nuclear-code-quality-review",
                    thermo_path,
                    worktree,
                    timeout,
                    thermo_workers["thermo-nuclear-code-quality-review"],
                ),
            }
            with ThreadPoolExecutor(max_workers=3, thread_name_prefix="omp-review") as pool:
                futures = {reviewer: pool.submit(job) for reviewer, job in jobs.items()}
                passes = [futures[reviewer].result() for reviewer in ("autoreview", *THERMO_SKILLS)]
            integration_path = worktree / PACKET_DIR / "autoreview.integration.json"
            if integration_path.is_file():
                packet_snapshot[str(integration_path)] = integration_path.read_bytes()
                packet_status = _worktree_status(worktree)
            _assert_packet_unchanged(packet_snapshot, packet_status, worktree)
            if bundle_from_git(repo, frozen["old_oid"], frozen["new_oid"], check_worktree=True) != frozen:
                raise GateError("reviewed committed range changed while reviewers ran")
        pass_paths: dict[str, Path] = {}
        for envelope in passes:
            reviewer = envelope["reviewer"]
            raw_path = output_root / f"{reviewer}.raw.json"
            write_json(raw_path, envelope["raw_report"])
            envelope["raw_report_path"] = raw_path.relative_to(repo).as_posix()
            pass_path = output_root / f"{reviewer}.json"
            write_json(pass_path, envelope)
            pass_paths[reviewer] = pass_path
        output = receipt_path(repo)
        record_receipt(
            repo,
            freeze_file,
            output,
            "substantive",
            pass_paths["autoreview"],
            passes[0]["exit_code"],
            pass_paths["thermo-nuclear-review"],
            pass_paths["thermo-nuclear-code-quality-review"],
        )
        print(f"review receipt written: {output}")
        return 0
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree)],
            cwd=repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        shutil.rmtree(temp_parent, ignore_errors=True)
