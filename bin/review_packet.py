"""Deterministic redacted evidence packets for harness-neutral review."""
from __future__ import annotations

import hashlib
import re
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterator, Mapping

from review_bundle import (
    assert_same_identity,
    bundle_from_git,
    freeze_path,
    identity_from_document,
    load_freeze,
    packet_path,
)
from review_common import (
    DIGEST_PATTERN,
    GateError,
    PACKET_SCHEMA,
    RESULT_SCHEMA,
    REVIEWERS,
    mapping,
    read_json,
    sha256_bytes,
    skill_identity,
)

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

DATASET_BYTES = 160_000
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
AUTOREVIEW_TRANSPORT_RISK_HINT = re.compile(
    r"(?i)(?:secret|password|credential|authorization|private[_ -]?key|"
    r"(?:access|refresh|oauth|bearer|session|auth)[_ -]?token|api[_ -]?key)"
)
EVIDENCE_POLICY = (
    "redacted bounded committed-range datasets; deleted file bodies and residual "
    "credential-shaped sections omitted; only packet datasets and canonical reviewer skills are in scope"
)
PACKET_MANIFEST_NAME = "manifest.json"

PacketIdentity = dict[str, Any]


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


def _omit_transport_risk_lines(unit: str) -> str:
    retained: list[str] = []
    for line in unit.splitlines(keepends=True):
        if AUTOREVIEW_TRANSPORT_RISK_HINT.search(line) or autoreview_security.secret_text_risk(line):
            prefix = "# > " if line.startswith("# > ") else "# "
            ending = "\n" if line.endswith("\n") else ""
            retained.append(f"{prefix}[source line omitted after path-dialect scan]{ending}")
        else:
            retained.append(line)
    return "".join(retained)


def _redact_secret_like_values(diff: bytes) -> bytes:
    redacted: list[str] = []
    for unit in autoreview_security.review_bundle_units(diff.decode("utf-8", errors="replace")):
        old_path, new_path = autoreview_security.diff_section_paths(unit)
        review_path = new_path or old_path
        dialect = autoreview_security.javascript_review_dialect(review_path) if review_path is not None else None
        unit = autoreview_security.redact_review_patch_metadata(unit)
        spans = autoreview_security.review_repeatable_secret_spans(unit, javascript_dialect=dialect)
        unit = autoreview_security.redact_review_spans(unit, spans)
        old_content, new_content = autoreview_security.unified_diff_contents(unit)
        if autoreview_security.secret_text_risk(old_content, javascript_dialect=dialect) or autoreview_security.secret_text_risk(
            new_content, javascript_dialect=dialect
        ):
            raise GateError(f"cannot safely redact credential-shaped review evidence in {new_path or old_path or 'diff metadata'}")
        if unit.startswith("diff --git "):
            unit = _comment_frame_diff_hunks(unit)
            unit = _omit_transport_risk_lines(unit)
        if autoreview_security.secret_text_risk(unit):
            path_label = review_path or "diff-metadata"
            unit = f"# review path: {path_label}\n# [section omitted after path-dialect scan]\n"
        redacted.append(unit)
    return "".join(redacted).encode("utf-8")


def _iter_diff_sections(diff: bytes) -> Iterator[bytes]:
    current = bytearray()
    for line in diff.splitlines(keepends=True):
        if line.startswith(b"diff --git ") and current:
            yield bytes(current)
            current.clear()
        current.extend(line)
    if current:
        yield bytes(current)


def _compact_deleted_files(diff: bytes) -> bytes:
    compacted: list[bytes] = []
    for raw_section in _iter_diff_sections(diff):
        section = raw_section.splitlines(keepends=True)
        deleted = any(line.startswith(b"deleted file mode ") for line in section) and any(
            line.startswith(b"+++ /dev/null") for line in section
        )
        if not deleted:
            compacted.extend(section)
            continue
        removed_lines = sum(1 for line in section if line.startswith(b"-") and not line.startswith(b"--- "))
        compacted.extend(
            line
            for line in section
            if line.startswith((b"diff --git ", b"deleted file mode ", b"index ", b"--- "))
        )
        compacted.append(f"# Entire file deleted; {removed_lines} removed lines omitted from model evidence.\n".encode("ascii"))
    return b"".join(compacted)

def _compact_binary_files(diff: bytes) -> bytes:
    """Replace Git binary patch bodies with bounded, reviewable metadata."""
    compacted: list[bytes] = []
    for raw_section in _iter_diff_sections(diff):
        section = raw_section.splitlines(keepends=True)
        if not any(line.startswith(b"GIT binary patch") for line in section):
            compacted.extend(section)
            continue
        retained: list[bytes] = []
        literal_sizes: list[int] = []
        delta_sizes: list[int] = []
        for line in section:
            if line.startswith(
                (
                    b"diff --git ",
                    b"new file mode ",
                    b"old mode ",
                    b"new mode ",
                    b"deleted file mode ",
                    b"similarity index ",
                    b"dissimilarity index ",
                    b"index ",
                    b"--- ",
                    b"+++ ",
                    b"Binary files ",
                )
            ):
                retained.append(line)
                continue
            if line.startswith(b"GIT binary patch"):
                retained.append(line)
                continue
            for prefix, sizes in ((b"literal ", literal_sizes), (b"delta ", delta_sizes)):
                if line.startswith(prefix):
                    try:
                        sizes.append(int(line[len(prefix) :].strip()))
                    except ValueError:
                        pass
                    break
        retained.append(b"# Binary patch body omitted; file identity and Git blob metadata are retained.\n")
        if literal_sizes:
            retained.append(
                ("# Binary literal sizes: " + ", ".join(str(size) for size in literal_sizes) + "\n").encode("ascii")
            )
        if delta_sizes:
            retained.append(
                ("# Binary delta payload sizes: " + ", ".join(str(size) for size in delta_sizes) + "\n").encode("ascii")
            )
        if not any(line.startswith(b"GIT binary patch") for line in retained):
            retained.insert(1, b"GIT binary patch\n")
        compacted.extend(retained)
    return b"".join(compacted)


def _split_oversized_section(section: bytes) -> list[bytes]:
    if len(section) <= DATASET_BYTES:
        return [section]
    lines = section.splitlines(keepends=True)
    first_hunk = next((index for index, line in enumerate(lines) if line.startswith(b"@@ ")), len(lines))
    header = b"".join(lines[:first_hunk])
    if len(header) >= DATASET_BYTES:
        raise GateError("committed diff contains metadata too large for bounded review evidence")
    hunk_header = lines[first_hunk] if first_hunk < len(lines) else b"# Continued file diff.\n"
    payload = lines[first_hunk + 1 :] if first_hunk < len(lines) else []
    prefix = header + hunk_header
    if len(prefix) > DATASET_BYTES:
        raise GateError("committed diff contains metadata too large for bounded review evidence")
    continuation_prefix = header + b"# Continued hunk from prior review dataset.\n" + hunk_header
    if len(continuation_prefix) > DATASET_BYTES:
        raise GateError("committed diff contains metadata too large for bounded review evidence")
    pieces: list[bytes] = []
    current = bytearray(prefix)
    for line in payload:
        if len(prefix) + len(line) > DATASET_BYTES:
            raise GateError("committed diff contains a line too large for bounded review evidence")
        if len(current) + len(line) > DATASET_BYTES:
            pieces.append(bytes(current))
            if len(continuation_prefix) + len(line) > DATASET_BYTES:
                raise GateError("committed diff contains a line too large for bounded review evidence")
            current = bytearray(continuation_prefix)
        current.extend(line)
    if current:
        pieces.append(bytes(current))
    return pieces


def _dataset_chunks(diff: bytes) -> list[bytes]:
    compacted = _redact_secret_like_values(_compact_binary_files(_compact_deleted_files(diff)))

    chunks: list[bytes] = []
    current = bytearray()
    for section in _iter_diff_sections(compacted):
        for piece in _split_oversized_section(section):
            if len(piece) > DATASET_BYTES:
                raise GateError("committed diff contains a section too large for bounded review evidence")
            piece_text = piece.decode("utf-8", errors="replace")
            if autoreview_security.secret_text_risk(piece_text):
                raise GateError("cannot safely construct bounded review evidence")
            if current:
                candidate = bytes(current) + piece
                if len(candidate) > DATASET_BYTES or autoreview_security.secret_text_risk(
                    candidate.decode("utf-8", errors="replace")
                ):
                    chunks.append(bytes(current))
                    current = bytearray(piece)
                    continue
            current.extend(piece)
    if current:
        if len(current) > DATASET_BYTES:
            raise GateError("committed diff contains a chunk too large for bounded review evidence")
        chunks.append(bytes(current))
    return chunks or [b"# Committed range has no textual diff.\n"]


def _git_diff(repo: Path, identity: Mapping[str, Any]) -> bytes:
    old_oid = identity["old_oid"] if identity["old_oid"] != "0" * 40 else EMPTY_TREE
    result = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--binary", "--full-index", old_oid, identity["new_oid"], "--"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise GateError(f"cannot build immutable committed diff: {detail}")
    return result.stdout


def _framed_packet_digest(files: Mapping[str, bytes]) -> str:
    digest = hashlib.sha256()
    for name in sorted(files):
        path_bytes = name.encode("utf-8")
        content = files[name]
        digest.update(len(path_bytes).to_bytes(8, "big"))
        digest.update(path_bytes)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return f"sha256:{digest.hexdigest()}"


def packet_digest(repo: Path, manifest: Mapping[str, Any]) -> str:
    """Recompute a packet manifest digest from its listed dataset bytes."""
    packet = packet_path(repo)
    datasets = manifest.get("datasets")
    if not isinstance(datasets, list):
        raise GateError("review packet datasets must be a list")
    files: dict[str, bytes] = {}
    for item in datasets:
        entry = mapping(item, "review packet dataset")
        relative = entry.get("path")
        if not isinstance(relative, str):
            raise GateError("review packet dataset path must be a string")
        path = _dataset_path(repo, relative)
        if not path.is_file() or path.is_symlink():
            raise GateError(f"missing review packet dataset {relative}")
        files[relative] = path.read_bytes()
    return _framed_packet_digest(files)


def _dataset_path(repo: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or path == Path("."):
        raise GateError(f"review packet dataset path is unsafe: {relative!r}")
    packet = packet_path(repo)
    resolved = (repo / path).resolve(strict=False)
    if not resolved.is_relative_to(packet.resolve()):
        raise GateError("review packet dataset must stay under .omp/review-packet")
    if resolved == packet.resolve() or resolved.name == PACKET_MANIFEST_NAME:
        raise GateError("review packet manifest cannot be a dataset")
    return resolved


def _identity_fields(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value[key] for key in ("repository", "old_oid", "new_oid", "commits", "paths", "bundle_digest")}


def _assignment_manifest() -> dict[str, dict[str, Any]]:
    return {
        reviewer: {
            "reviewer": reviewer,
            "skill": skill_identity(reviewer),
            "result_schema": RESULT_SCHEMA,
        }
        for reviewer in REVIEWERS
    }


def _canonical_json_file(document: Mapping[str, Any]) -> bytes:
    return (json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def prepare_packet(repo: Path, freeze_file: Path) -> PacketIdentity:
    """Create the gate-owned redacted packet for one frozen Git range."""
    repo = repo.resolve()
    freeze_file = freeze_path(repo, str(freeze_file))
    freeze_document, frozen = load_freeze(repo, freeze_file)
    current = bundle_from_git(repo, frozen["old_oid"], frozen["new_oid"], check_worktree=True)
    assert_same_identity(frozen, current, "review freeze")
    chunks = _dataset_chunks(_git_diff(repo, frozen))
    review_names = [f"bundle.review.{index:03d}.diff" for index in range(len(chunks))]
    evidence = {
        "schema": "omp.review-evidence.v1",
        "freeze": freeze_document,
        "bundle_digest": frozen["bundle_digest"],
        "review_datasets": review_names,
        "evidence_policy": EVIDENCE_POLICY,
        "scope": "packet-only leaf review; repository files, worktree, PR discussion, host paths, and network are out of scope",
    }
    files: dict[str, bytes] = {
        "freeze.json": _canonical_json_file(freeze_document),
        "evidence.json": _canonical_json_file(evidence),
        **dict(zip(review_names, chunks, strict=True)),
    }
    datasets = [
        {"path": (Path(".omp/review-packet") / name).as_posix(), "sha256": sha256_bytes(content)}
        for name, content in sorted(files.items())
    ]
    manifest: PacketIdentity = {
        "schema": PACKET_SCHEMA,
        "kind": "packet",
        **frozen,
        "packet_digest": _framed_packet_digest(
            {(Path(".omp/review-packet") / name).as_posix(): content for name, content in files.items()}
        ),
        "datasets": datasets,
        "evidence_policy": EVIDENCE_POLICY,
        "assignments": _assignment_manifest(),
    }

    packet = packet_path(repo)
    packet.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{packet.name}.", dir=packet.parent))
    try:
        for name, content in files.items():
            path = temporary / name
            path.write_bytes(content)
            path.chmod(0o444)
        (temporary / PACKET_MANIFEST_NAME).write_bytes(_canonical_json_file(manifest))
        (temporary / PACKET_MANIFEST_NAME).chmod(0o444)
        if packet.exists() or packet.is_symlink():
            if packet.is_symlink() or not packet.is_dir():
                raise GateError("review packet path is not a gate-owned directory")
            shutil.rmtree(packet)
        os.replace(temporary, packet)
    except BaseException:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    verify_packet(repo, manifest, frozen)
    return manifest


def load_packet(repo: Path, freeze_identity: Mapping[str, Any]) -> PacketIdentity:
    """Load and revalidate the gate-owned packet for a frozen identity."""
    manifest_path = packet_path(repo) / PACKET_MANIFEST_NAME
    manifest = read_json(manifest_path, f"review packet {manifest_path}")
    verify_packet(repo, manifest, freeze_identity)
    return manifest


def verify_packet(repo: Path, packet: Mapping[str, Any], freeze_identity: Mapping[str, Any]) -> None:
    """Fail closed when the manifest, datasets, assignments, or bytes drift."""
    repo = repo.resolve()
    if packet.get("schema") == "omp.review-packet.v2":
        raise GateError("obsolete review packet schema; run freeze and prepare again")
    if packet.get("schema") != PACKET_SCHEMA or packet.get("kind") != "packet":
        raise GateError(f"review packet must declare schema {PACKET_SCHEMA}")
    if _identity_fields(packet) != _identity_fields(freeze_identity):
        raise GateError("review packet does not match the frozen committed-range bundle")
    datasets = packet.get("datasets")
    if not isinstance(datasets, list) or not datasets:
        raise GateError("review packet must list one or more datasets")
    listed: dict[str, str] = {}
    for item in datasets:
        entry = mapping(item, "review packet dataset")
        relative = entry.get("path")
        digest = entry.get("sha256")
        if not isinstance(relative, str) or not isinstance(digest, str) or not DIGEST_PATTERN.fullmatch(digest):
            raise GateError("review packet datasets require path and sha256")
        _dataset_path(repo, relative)
        if relative in listed:
            raise GateError("review packet datasets must be unique")
        listed[relative] = digest
    if list(listed) != sorted(listed):
        raise GateError("review packet datasets must be sorted")
    packet_dir = packet_path(repo)
    actual_files = sorted(
        path.relative_to(repo).as_posix()
        for path in packet_dir.rglob("*")
        if path.is_file() or path.is_symlink()
    )
    expected_files = sorted([*listed, (Path(".omp/review-packet") / PACKET_MANIFEST_NAME).as_posix()])
    if actual_files != expected_files:
        raise GateError("review packet contains an extra or missing file")
    for relative, expected_digest in listed.items():
        path = _dataset_path(repo, relative)
        if sha256_bytes(path.read_bytes()) != expected_digest:
            raise GateError(f"review packet dataset changed: {relative}")
    if packet.get("packet_digest") != packet_digest(repo, packet):
        raise GateError("review packet digest does not match its listed dataset bytes")
    assignments = packet.get("assignments")
    if not isinstance(assignments, dict) or set(assignments) != set(REVIEWERS):
        raise GateError("review packet assignments must name exactly the three canonical reviewers")
    for reviewer in REVIEWERS:
        assignment = mapping(assignments.get(reviewer), f"review packet assignment {reviewer}")
        if assignment.get("reviewer") != reviewer or assignment.get("result_schema") != RESULT_SCHEMA:
            raise GateError(f"review packet assignment {reviewer} has an invalid result schema")
        if assignment.get("skill") != skill_identity(reviewer):
            raise GateError(f"review packet assignment {reviewer} has stale canonical skill identity")
    freeze_dataset = _dataset_path(repo, ".omp/review-packet/freeze.json")
    freeze_identity_from_packet = identity_from_document(read_json(freeze_dataset, "review packet freeze dataset"), "review packet freeze")
    if _identity_fields(freeze_identity_from_packet) != _identity_fields(freeze_identity):
        raise GateError("review packet freeze dataset does not match the frozen bundle")
