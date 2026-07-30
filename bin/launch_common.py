from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config_contract import ContractError, frontmatter, split_selector
from contract_utils import sha256_digest, sha256_file


SCHEMA_VERSION = "omp.launch-contract.v1"
MANIFEST_VERSION = "omp.launch-bundle.v1"
NAME_PATTERN = re.compile(r"[a-z][a-z0-9_-]*")
TOOL_NAMES = {
    "ask",
    "bash",
    "browser",
    "edit",
    "glob",
    "grep",
    "inspect_image",
    "lsp",
    "notebook",
    "python",
    "read",
    "task",
    "todo",
    "web_search",
    "write",
}
DISABLED_PROVIDERS = (
    "agents-md",
    "claude",
    "claude-plugins",
    "cline",
    "codex",
    "cursor",
    "gemini",
    "github",
    "mcp-json",
    "omp-plugins",
    "opencode",
    "ssh-json",
    "vscode",
    "windsurf",
)


@dataclass(frozen=True)
class ResolvedFile:
    kind: str
    name: str
    source: Path
    destination: Path


@dataclass(frozen=True)
class CompiledLaunch:
    name: str
    repository: Path
    instructions: Path
    agent: str
    model: str
    thinking: str
    tools: tuple[str, ...]
    skills: tuple[str, ...]
    mcp_servers: tuple[str, ...]
    allowed_agents: tuple[str, ...]
    max_concurrency: int
    subagent_tools: tuple[str, ...]
    disabled_agents: tuple[str, ...]
    repository_digest: str
    repository_file_count: int
    max_time_seconds: int
    approval_mode: str
    files: tuple[ResolvedFile, ...]
    mcp: dict[str, object]
    prompt: str
    profile: str | None


def name(value: object, label: str) -> str:
    if not isinstance(value, str) or not NAME_PATTERN.fullmatch(value):
        raise ContractError(f"{label} must match {NAME_PATTERN.pattern}")
    return value


def name_list(value: object, label: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ContractError(f"{label} must be a list")
    names = tuple(name(item, f"{label}[{index}]") for index, item in enumerate(value))
    if not allow_empty and not names:
        raise ContractError(f"{label} must not be empty")
    if len(names) != len(set(names)):
        raise ContractError(f"{label} contains duplicates")
    return names


def id_list(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ContractError(f"{label} must be a list")
    pattern = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")
    identifiers: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not pattern.fullmatch(item):
            raise ContractError(f"{label}[{index}] must match {pattern.pattern}")
        identifiers.append(item)
    if len(identifiers) != len(set(identifiers)):
        raise ContractError(f"{label} contains duplicates")
    return tuple(identifiers)


def csv(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def resolve_inside(root: Path, value: str, label: str, *, file: bool | None = None) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve(strict=False)
    if not candidate.is_relative_to(root.resolve()):
        raise ContractError(f"{label} escapes repository root")
    if file is True and not candidate.is_file():
        raise ContractError(f"{label} is not a file: {candidate}")
    if file is False and not candidate.is_dir():
        raise ContractError(f"{label} is not a directory: {candidate}")
    return candidate


def resolve_named_source(name_value: str, candidates: list[tuple[str, Path]], label: str) -> tuple[str, Path]:
    found = [(source, path) for source, path in candidates if path.exists()]
    if not found:
        searched = ", ".join(str(path) for _, path in candidates)
        raise ContractError(f"unresolved {label} {name_value!r}; searched {searched}")
    if len(found) > 1:
        details = ", ".join(f"{source}:{path}" for source, path in found)
        raise ContractError(f"duplicate sources for {label} {name_value!r}: {details}")
    return found[0]


def agent_source(config_root: Path, repository: Path, name_value: str) -> tuple[str, Path]:
    return resolve_named_source(
        name_value,
        [
            ("repository", repository / ".omp" / "agents" / f"{name_value}.md"),
            ("global", config_root / "global" / "agents" / f"{name_value}.md"),
        ],
        "agent",
    )


def skill_source(config_root: Path, repository: Path, name_value: str) -> tuple[str, Path]:
    return resolve_named_source(
        name_value,
        [
            ("repository", repository / ".omp" / "skills" / name_value),
            ("global", config_root / "global" / "skills" / name_value),
        ],
        "skill",
    )


def agent_fields(path: Path, expected_name: str) -> tuple[dict[str, str], str]:
    fields, body = frontmatter(path)
    if fields.get("name") != expected_name:
        raise ContractError(f"agent {path} declares name {fields.get('name')!r}, expected {expected_name!r}")
    if not body:
        raise ContractError(f"agent {path} has no prompt body")
    if not fields.get("model"):
        raise ContractError(f"agent {path} has no model policy")
    if not fields.get("tools"):
        raise ContractError(f"agent {path} has no tool policy")
    return fields, body


def validate_model(fields: dict[str, str], model: str, thinking: str, agent: str) -> None:
    bindings = [split_selector(selector.strip()) for selector in fields["model"].split(",") if selector.strip()]
    matches = [(selector, effort) for selector, effort in bindings if selector == model]
    if not matches:
        allowed = ", ".join(selector for selector, _ in bindings)
        raise ContractError(f"composition model {model!r} is not allowed by agent {agent}; allowed: {allowed}")
    declared_thinking = fields.get("thinkingLevel")
    allowed_efforts = {effort for _, effort in matches if effort != "auto"}
    if allowed_efforts and thinking not in allowed_efforts:
        raise ContractError(
            f"composition thinking {thinking!r} conflicts with model binding for agent {agent}: "
            f"{sorted(allowed_efforts)}"
        )
    if not allowed_efforts and declared_thinking and thinking != declared_thinking:
        raise ContractError(
            f"composition thinking {thinking!r} conflicts with agent {agent} thinkingLevel {declared_thinking!r}"
        )


def validate_tools(fields: dict[str, str], tools: tuple[str, ...], agent: str) -> None:
    declared = fields["tools"].strip()
    if declared == "*":
        return
    declared_tools = set(csv(declared))
    if set(tools) != declared_tools:
        raise ContractError(
            f"composition tools for agent {agent} must exactly match its declared envelope: "
            f"expected={sorted(declared_tools)}, actual={sorted(tools)}"
        )


def project_agent_names(repository: Path) -> set[str]:
    directory = repository / ".omp" / "agents"
    return {path.stem for path in directory.glob("*.md")} if directory.is_dir() else set()


def ancestor_project_agent_paths(repository: Path) -> list[Path]:
    for ancestor in repository.resolve().parents:
        directory = ancestor / ".omp" / "agents"
        if directory.is_dir():
            return list(directory.glob("*.md"))
    return []


def reject_undeclared_project_agents(repository: Path, selected: set[str]) -> None:
    extras = sorted(project_agent_names(repository) - selected)
    if extras:
        raise ContractError(f"repository has undeclared project agents that OMP would discover: {', '.join(extras)}")
    ancestor_agents = ancestor_project_agent_paths(repository)
    if ancestor_agents:
        locations = ", ".join(str(path) for path in sorted(ancestor_agents))
        raise ContractError(f"repository has ancestor project agents outside the sealed source tree: {locations}")


def repository_receipt(repository: Path) -> tuple[str, int]:
    paths: list[Path]
    root_result = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if root_result.returncode == 0 and Path(root_result.stdout.strip()).resolve() == repository:
        files_result = subprocess.run(
            ["git", "-C", str(repository), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if files_result.returncode:
            raise ContractError(f"cannot enumerate repository files: {files_result.stderr.strip()}")
        paths = [repository / value for value in files_result.stdout.split("\0") if value]
    else:
        excluded = {".git", "__pycache__", "node_modules", "target"}
        paths = [
            path
            for path in repository.rglob("*")
            if path.is_file() and not any(part in excluded for part in path.relative_to(repository).parts)
        ]
    paths = list({*paths, *(repository / ".omp" / "agents").glob("*.md")})
    receipts: list[dict[str, object]] = []
    for path in sorted(paths):
        if path.is_symlink():
            raise ContractError(f"repository receipt refuses symlink: {path}")
        if not path.is_file():
            raise ContractError(f"repository receipt path is not a regular file: {path}")
        receipts.append(
            {
                "path": path.relative_to(repository).as_posix(),
                "sha256": sha256_file(path),
                "size": path.stat().st_size,
            }
        )
    return sha256_digest(receipts), len(receipts)
