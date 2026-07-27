from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import socket
import signal
import subprocess
import tempfile
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config_contract import ContractError, THINKING_LEVELS, frontmatter, load_contract, split_selector

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


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ContractError(f"{label} must be an object")
    return value


def _strict_keys(mapping: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise ContractError(f"{label} has unsupported fields: {', '.join(unknown)}")


def _string(mapping: dict[str, Any], key: str, label: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ContractError(f"{label}.{key} must be a non-empty string")
    return value


def _name(value: object, label: str) -> str:
    if not isinstance(value, str) or not NAME_PATTERN.fullmatch(value):
        raise ContractError(f"{label} must match {NAME_PATTERN.pattern}")
    return value


def _name_list(value: object, label: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ContractError(f"{label} must be a list")
    names = tuple(_name(item, f"{label}[{index}]") for index, item in enumerate(value))
    if not allow_empty and not names:
        raise ContractError(f"{label} must not be empty")
    if len(names) != len(set(names)):
        raise ContractError(f"{label} contains duplicates")
    return names


def _id_list(value: object, label: str) -> tuple[str, ...]:
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


def _csv(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _resolve_inside(root: Path, value: str, label: str, *, file: bool | None = None) -> Path:
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


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text())
    except OSError as error:
        raise ContractError(f"cannot read {label}: {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise ContractError(f"{label} must use the JSON subset of YAML: {error}") from error
    return _mapping(raw, label)


def _resolve_named_source(name: str, candidates: list[tuple[str, Path]], label: str) -> tuple[str, Path]:
    found = [(source, path) for source, path in candidates if path.exists()]
    if not found:
        searched = ", ".join(str(path) for _, path in candidates)
        raise ContractError(f"unresolved {label} {name!r}; searched {searched}")
    if len(found) > 1:
        details = ", ".join(f"{source}:{path}" for source, path in found)
        raise ContractError(f"duplicate sources for {label} {name!r}: {details}")
    return found[0]


def _agent_source(config_root: Path, repository: Path, name: str) -> tuple[str, Path]:
    return _resolve_named_source(
        name,
        [
            ("repository", repository / ".omp" / "agents" / f"{name}.md"),
            ("global", config_root / "global" / "agents" / f"{name}.md"),
        ],
        "agent",
    )


def _skill_source(config_root: Path, repository: Path, name: str) -> tuple[str, Path]:
    return _resolve_named_source(
        name,
        [
            ("repository", repository / ".omp" / "skills" / name),
            ("global", config_root / "global" / "skills" / name),
        ],
        "skill",
    )


def _agent_fields(path: Path, expected_name: str) -> tuple[dict[str, str], str]:
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


def _validate_model(fields: dict[str, str], model: str, thinking: str, agent: str) -> None:
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


def _validate_tools(fields: dict[str, str], tools: tuple[str, ...], agent: str) -> None:
    declared = fields["tools"].strip()
    if declared == "*":
        return
    declared_tools = set(_csv(declared))
    if set(tools) != declared_tools:
        raise ContractError(
            f"composition tools for agent {agent} must exactly match its declared envelope: "
            f"expected={sorted(declared_tools)}, actual={sorted(tools)}"
        )


def _load_profile(config_root: Path, profile: object, skills: tuple[str, ...]) -> str | None:
    if profile is None:
        return None
    name = _name(profile, "composition.profile")
    path = config_root / "global" / "presets" / f"{name}.yml"
    if not path.is_file():
        raise ContractError(f"unresolved composition profile {name!r}: {path}")
    include: list[str] | None = None
    ignored = False
    current: str | None = None
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped == "skills:":
            continue
        if stripped == "includeSkills:":
            include = []
            current = "include"
            continue
        if stripped == "ignoredSkills:":
            ignored = True
            current = "ignored"
            continue
        if stripped.startswith("- ") and current:
            if current == "include":
                assert include is not None
                include.append(stripped[2:].strip().strip("'\""))
            continue
        raise ContractError(f"profile {path} has unsupported YAML at line {line_number}")
    if ignored or include is None:
        raise ContractError(
            f"profile {name!r} is denylist-based or has no explicit skills.includeSkills allowlist; "
            "sealed launch contracts refuse it"
        )
    if tuple(include) != skills:
        raise ContractError(
            f"profile {name!r} skill allowlist differs from composition.skills: "
            f"profile={include}, composition={list(skills)}"
        )
    return name


def _load_selected_mcp(config_root: Path, repository: Path, names: tuple[str, ...]) -> dict[str, object]:
    sources = [
        ("repository:.omp/mcp.json", repository / ".omp" / "mcp.json"),
        ("repository:.omp/.mcp.json", repository / ".omp" / ".mcp.json"),
        ("repository:mcp.json", repository / "mcp.json"),
        ("repository:.mcp.json", repository / ".mcp.json"),
        ("global", config_root / "global" / "mcp.json"),
    ]
    catalogs: list[tuple[str, Path, dict[str, Any]]] = []
    for source, path in sources:
        if not path.is_file():
            continue
        document = _load_json(path, f"MCP source {source}")
        servers = _mapping(document.get("mcpServers", {}), f"MCP source {source}.mcpServers")
        catalogs.append((source, path, servers))

    selected: dict[str, object] = {}
    for name in names:
        found = [(source, path, servers[name]) for source, path, servers in catalogs if name in servers]
        if not found:
            raise ContractError(f"unresolved MCP server {name!r}")
        if len(found) > 1:
            details = ", ".join(f"{source}:{path}" for source, path, _ in found)
            raise ContractError(f"duplicate sources for MCP server {name!r}: {details}")
        value = found[0][2]
        if not isinstance(value, dict):
            raise ContractError(f"MCP server {name!r} must be an object")
        selected[name] = value
    return {"mcpServers": selected}


def _project_agent_names(repository: Path) -> set[str]:
    directory = repository / ".omp" / "agents"
    return {path.stem for path in directory.glob("*.md")} if directory.is_dir() else set()


def _ancestor_project_agent_paths(repository: Path) -> list[Path]:
    for ancestor in repository.resolve().parents:
        directory = ancestor / ".omp" / "agents"
        if directory.is_dir():
            return list(directory.glob("*.md"))
    return []

def _reject_undeclared_project_agents(repository: Path, selected: set[str]) -> None:
    extras = sorted(_project_agent_names(repository) - selected)
    if extras:
        raise ContractError(f"repository has undeclared project agents that OMP would discover: {', '.join(extras)}")
    ancestor_agents = _ancestor_project_agent_paths(repository)
    if ancestor_agents:
        locations = ", ".join(str(path) for path in sorted(ancestor_agents))
        raise ContractError(f"repository has ancestor project agents outside the sealed source tree: {locations}")


def _repository_receipt(repository: Path) -> tuple[str, int]:
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
        )
        if files_result.returncode:
            raise ContractError(f"cannot enumerate repository files: {files_result.stderr.decode().strip()}")
        paths = [repository / value.decode() for value in files_result.stdout.split(b"\0") if value]
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
                "sha256": _sha256(path),
                "size": path.stat().st_size,
            }
        )
    return "sha256:" + hashlib.sha256(_canonical(receipts)).hexdigest(), len(receipts)


def _render_isolation(
    skills: tuple[str, ...],
    max_concurrency: int,
    disabled_agents: tuple[str, ...],
) -> str:
    lines = [
        "setupVersion: 1",
        "async:",
        "  enabled: false",
        "mcp:",
        "  enableProjectConfig: false",
        "task:",
        f"  maxConcurrency: {max_concurrency}",
        f"  disabledAgents: {json.dumps(list(disabled_agents), separators=(',', ':'))}",
        "skills:",
        f"  includeSkills: {json.dumps(list(skills), separators=(',', ':'))}",
    ]
    lines.append("disabledProviders:")
    lines.extend(f"  - {provider}" for provider in DISABLED_PROVIDERS)
    return "\n".join(lines) + "\n"


def _render_prompt(
    global_instructions: str,
    repository_instructions: str,
    agent: str,
    agent_body: str,
    skill_sources: list[tuple[str, Path]],
    tools: tuple[str, ...],
    mcp_servers: tuple[str, ...],
    allowed_agents: tuple[str, ...],
    subagent_tools: tuple[str, ...],
) -> str:
    sections = [
        "<global-constitution>\n" + global_instructions.strip() + "\n</global-constitution>",
        "<repository-contract>\n" + repository_instructions.strip() + "\n</repository-contract>",
        f'<agent-role name="{agent}">\n{agent_body.strip()}\n</agent-role>',
    ]
    for name, path in skill_sources:
        _, body = frontmatter(path / "SKILL.md")
        sections.append(f'<autoloaded-skill name="{name}">\n{body.strip()}\n</autoloaded-skill>')
    envelope = {
        "allowed_subagents": list(allowed_agents),
        "mcp_servers": list(mcp_servers),
        "skills": [name for name, _ in skill_sources],
        "subagent_tools": list(subagent_tools),
        "tools": list(tools),
    }
    sections.append(
        "<launch-envelope>\n"
        + json.dumps(envelope, sort_keys=True, separators=(",", ":"))
        + "\nUse only the declared envelope. Fail closed when work requires an undeclared capability.\n"
        + "</launch-envelope>"
    )
    return "\n\n".join(sections) + "\n"


def resolve_contract(config_root: Path, contract_path: Path) -> CompiledLaunch:
    config_root = config_root.resolve()
    load_contract(config_root)
    contract_path = contract_path.resolve()
    document = _load_json(contract_path, "launch contract")
    _strict_keys(document, {"schema_version", "name", "repository", "composition", "sandbox", "execution"}, "launch contract")
    if document.get("schema_version") != SCHEMA_VERSION:
        raise ContractError(f"launch contract schema_version must be {SCHEMA_VERSION}")
    name = _name(document.get("name"), "launch contract.name")

    repository_config = _mapping(document.get("repository"), "repository")
    _strict_keys(repository_config, {"root", "instructions"}, "repository")
    root_value = _string(repository_config, "root", "repository")
    repository = Path(root_value)
    if not repository.is_absolute():
        repository = contract_path.parent / repository
    repository = repository.resolve()
    if not repository.is_dir():
        raise ContractError(f"repository.root is not a directory: {repository}")
    instructions = _resolve_inside(
        repository,
        _string(repository_config, "instructions", "repository"),
        "repository.instructions",
        file=True,
    )

    composition = _mapping(document.get("composition"), "composition")
    _strict_keys(
        composition,
        {"agent", "profile", "model", "thinking", "tools", "skills", "mcp_servers", "subagents"},
        "composition",
    )
    agent = _name(composition.get("agent"), "composition.agent")
    model = _string(composition, "model", "composition")
    if "/" not in model or any(character.isspace() for character in model):
        raise ContractError("composition.model must be a provider/model selector")
    thinking = _string(composition, "thinking", "composition")
    if thinking not in THINKING_LEVELS:
        raise ContractError(f"composition.thinking must be one of {sorted(THINKING_LEVELS)}")
    tools = _name_list(composition.get("tools"), "composition.tools", allow_empty=False)
    unknown_tools = sorted(set(tools) - TOOL_NAMES)
    if unknown_tools:
        raise ContractError(f"composition.tools names unsupported OMP tools: {', '.join(unknown_tools)}")
    skills = _name_list(composition.get("skills"), "composition.skills")
    mcp_servers = _id_list(composition.get("mcp_servers"), "composition.mcp_servers")

    subagents = _mapping(composition.get("subagents"), "composition.subagents")
    _strict_keys(subagents, {"allowed", "tools", "isolation", "max_concurrency"}, "composition.subagents")
    allowed_agents = _name_list(subagents.get("allowed"), "composition.subagents.allowed")
    subagent_tools = _name_list(subagents.get("tools"), "composition.subagents.tools")
    isolation = _string(subagents, "isolation", "composition.subagents")
    if isolation != "inherit":
        raise ContractError(
            "composition.subagents.isolation is not enforceable by OMP 17.0.7; only 'inherit' is supported"
        )
    max_concurrency = subagents.get("max_concurrency")
    if not isinstance(max_concurrency, int) or isinstance(max_concurrency, bool) or not 1 <= max_concurrency <= 12:
        raise ContractError("composition.subagents.max_concurrency must be an integer from 1 through 12")
    if allowed_agents and "task" not in tools:
        raise ContractError("composition.tools must include task when composition.subagents.allowed is non-empty")
    unknown_subagent_tools = sorted(set(subagent_tools) - TOOL_NAMES)
    if unknown_subagent_tools:
        raise ContractError(
            "composition.subagents.tools names unsupported OMP tools: " + ", ".join(unknown_subagent_tools)
        )
    if allowed_agents and not subagent_tools:
        raise ContractError("composition.subagents.tools must not be empty when subagents are allowed")
    if not allowed_agents and subagent_tools:
        raise ContractError("composition.subagents.tools must be empty when no subagents are allowed")

    sandbox = _mapping(document.get("sandbox"), "sandbox")
    _strict_keys(sandbox, {"filesystem", "network", "process"}, "sandbox")
    requested_sandbox = {key: _string(sandbox, key, "sandbox") for key in ("filesystem", "network", "process")}
    unsupported = {key: value for key, value in requested_sandbox.items() if value != "host"}
    if unsupported:
        raise ContractError(
            "requested sandbox controls are not enforceable by OMP 17.0.7: "
            + ", ".join(f"{key}={value}" for key, value in sorted(unsupported.items()))
        )

    execution = _mapping(document.get("execution"), "execution")
    _strict_keys(execution, {"mode", "session", "max_time_seconds", "approval_mode"}, "execution")
    if _string(execution, "mode", "execution") != "print":
        raise ContractError("omp.launch-contract.v1 supports only execution.mode='print'")
    if _string(execution, "session", "execution") != "ephemeral":
        raise ContractError("omp.launch-contract.v1 supports only execution.session='ephemeral'")
    max_time_seconds = execution.get("max_time_seconds")
    if not isinstance(max_time_seconds, int) or isinstance(max_time_seconds, bool) or not 1 <= max_time_seconds <= 3600:
        raise ContractError("execution.max_time_seconds must be an integer from 1 through 3600")
    approval_mode = _string(execution, "approval_mode", "execution")
    if approval_mode not in {"always-ask", "write", "yolo"}:
        raise ContractError("execution.approval_mode must be always-ask, write, or yolo")

    profile = _load_profile(config_root, composition.get("profile"), skills)
    repository_digest, repository_file_count = _repository_receipt(repository)

    _, root_agent_path = _agent_source(config_root, repository, agent)
    root_fields, root_body = _agent_fields(root_agent_path, agent)
    _validate_model(root_fields, model, thinking, agent)
    _validate_tools(root_fields, tools, agent)
    root_skills = set(_csv(root_fields.get("autoloadSkills", "")))
    if not root_skills.issubset(skills):
        raise ContractError(
            f"composition.skills omits agent {agent} autoload skills: {sorted(root_skills - set(skills))}"
        )
    declared_spawns = root_fields.get("spawns", "").strip()
    if declared_spawns == "*":
        raise ContractError(f"agent {agent} uses wildcard spawns; sealed launch contracts require explicit agents")
    if set(_csv(declared_spawns)) != set(allowed_agents):
        raise ContractError(
            f"composition.subagents.allowed must exactly match agent {agent} spawns: "
            f"expected={sorted(_csv(declared_spawns))}, actual={sorted(allowed_agents)}"
        )

    _reject_undeclared_project_agents(repository, {agent, *allowed_agents})

    files: list[ResolvedFile] = [
        ResolvedFile("agent", agent, root_agent_path, Path("agent/agents") / root_agent_path.name)
    ]
    for child in allowed_agents:
        if child in load_contract(config_root).bundled_agents:
            raise ContractError(
                f"bundled subagent {child!r} has no source declaration to seal; unpack or declare it before compiling"
            )
        _, child_path = _agent_source(config_root, repository, child)
        child_fields, _ = _agent_fields(child_path, child)
        child_spawns = child_fields.get("spawns", "").strip()
        if child_spawns:
            raise ContractError(f"subagent {child} declares nested spawns; per-child composition is unsupported in v1")
        child_skills = set(_csv(child_fields.get("autoloadSkills", "")))
        if not child_skills.issubset(skills):
            raise ContractError(
                f"composition.skills omits subagent {child} autoload skills: {sorted(child_skills - set(skills))}"
            )
        declared_child_tools = child_fields["tools"].strip()
        if declared_child_tools == "*":
            raise ContractError(f"subagent {child} uses wildcard tools; launch contracts require explicit tools")
        child_tools = set(_csv(declared_child_tools))
        if not child_tools.issubset(subagent_tools):
            raise ContractError(
                f"composition.subagents.tools omits tools declared by {child}: "
                f"{sorted(child_tools - set(subagent_tools))}"
            )
        files.append(ResolvedFile("agent", child, child_path, Path("agent/agents") / child_path.name))

    skill_sources: list[tuple[str, Path]] = []
    for skill in skills:
        _, skill_path = _skill_source(config_root, repository, skill)
        skill_file = skill_path / "SKILL.md"
        if not skill_file.is_file():
            raise ContractError(f"skill {skill!r} has no SKILL.md: {skill_path}")
        skill_fields, _ = frontmatter(skill_file)
        if skill_fields.get("name", skill) != skill:
            raise ContractError(f"skill {skill_path} declares name {skill_fields.get('name')!r}")
        skill_sources.append((skill, skill_path))
        files.append(ResolvedFile("skill", skill, skill_path, Path("agent/skills") / skill))
    disabled_agents = tuple(
        sorted((set(load_contract(config_root).bundled_agents) | {agent}) - set(allowed_agents))
    )

    mcp = _load_selected_mcp(config_root, repository, mcp_servers)
    global_instructions_path = config_root / "global" / "AGENTS.md"
    if not global_instructions_path.is_file():
        raise ContractError(f"missing global constitution: {global_instructions_path}")
    prompt = _render_prompt(
        global_instructions_path.read_text(),
        instructions.read_text(),
        agent,
        root_body,
        skill_sources,
        tools,
        mcp_servers,
        allowed_agents,
        subagent_tools,
    )
    return CompiledLaunch(
        name=name,
        repository=repository,
        instructions=instructions,
        agent=agent,
        model=model,
        thinking=thinking,
        tools=tools,
        skills=skills,
        mcp_servers=mcp_servers,
        allowed_agents=allowed_agents,
        subagent_tools=subagent_tools,
        disabled_agents=disabled_agents,
        repository_digest=repository_digest,
        repository_file_count=repository_file_count,
        max_concurrency=max_concurrency,
        max_time_seconds=max_time_seconds,
        approval_mode=approval_mode,
        files=tuple(files),
        mcp=mcp,
        prompt=prompt,
        profile=profile,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _copy_resolved(source: Path, destination: Path) -> None:
    transient_names = {"__pycache__", "node_modules", "target", ".DS_Store"}
    candidates = [source, *source.rglob("*")] if source.is_dir() else [source]
    for candidate in candidates:
        if candidate.is_symlink():
            raise ContractError(f"sealed launch sources must not contain symlinks: {candidate}")
        if candidate.name in transient_names or candidate.suffix in {".pyc", ".swp", ".tmp"}:
            raise ContractError(f"sealed launch sources must not contain transient paths: {candidate}")
        if candidate.name == ".env" or candidate.name.startswith(".env."):
            raise ContractError(f"sealed launch sources must not contain environment files: {candidate}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, symlinks=False)
    else:
        shutil.copy2(source, destination)


def compile_bundle(config_root: Path, contract_path: Path, output: Path, *, force: bool = False) -> dict[str, object]:
    launch = resolve_contract(config_root, contract_path)
    output = output.resolve(strict=False)
    if output.exists() and not force:
        raise ContractError(f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{output.name}-", dir=output.parent) as temp:
        staging = Path(temp) / "bundle"
        staging.mkdir()
        for resolved in launch.files:
            _copy_resolved(resolved.source, staging / resolved.destination)
        (staging / "agent").mkdir(exist_ok=True)
        (staging / "agent" / "config.yml").write_text(
            _render_isolation(launch.skills, launch.max_concurrency, launch.disabled_agents)
        )
        _write_json(staging / "agent" / "mcp.json", launch.mcp)
        (staging / "system-prompt.txt").write_text(launch.prompt)
        shutil.copy2(contract_path.resolve(), staging / "contract.json")

        file_receipts = []
        for path in sorted(candidate for candidate in staging.rglob("*") if candidate.is_file()):
            relative = path.relative_to(staging).as_posix()
            file_receipts.append({"path": relative, "sha256": _sha256(path), "size": path.stat().st_size})
        payload: dict[str, object] = {
            "schema_version": MANIFEST_VERSION,
            "name": launch.name,
            "repository": {
                "digest": launch.repository_digest,
                "file_count": launch.repository_file_count,
            },
            "composition": {
                "agent": launch.agent,
                "profile": launch.profile,
                "model": launch.model,
                "thinking": launch.thinking,
                "tools": list(launch.tools),
                "skills": list(launch.skills),
                "mcp_servers": list(launch.mcp_servers),
                "subagents": {
                    "allowed": list(launch.allowed_agents),
                    "tools": list(launch.subagent_tools),
                    "isolation": "inherit",
                    "max_concurrency": launch.max_concurrency,
                },
            },
            "execution": {
                "mode": "print",
                "session": "ephemeral",
                "max_time_seconds": launch.max_time_seconds,
                "approval_mode": launch.approval_mode,
            },
            "enforcement": {
                "ambient_rules": "disabled-by-cli",
                "ambient_extensions": "disabled-by-cli",
                "built_in_tools": "cli-allowlist",
                "mcp_project_config": "disabled-by-config",
                "mcp_servers": "compiled-file",
                "sandbox": "host",
                "subagents": "disabled-agent-denylist-plus-repository-receipt",
            },
            "files": file_receipts,
        }
        digest = "sha256:" + hashlib.sha256(_canonical(payload)).hexdigest()
        manifest = {
            **payload,
            "runtime": {"repository_path": str(launch.repository)},
            "digest": digest,
        }
        _write_json(staging / "manifest.json", manifest)
        if output.exists():
            if output.is_dir():
                shutil.rmtree(output)
            else:
                output.unlink()
        staging.replace(output)
    return manifest


def verify_bundle(bundle: Path) -> dict[str, object]:
    bundle = bundle.resolve()
    manifest_path = bundle / "manifest.json"
    manifest = _load_json(manifest_path, "launch bundle manifest")
    if manifest.get("schema_version") != MANIFEST_VERSION:
        raise ContractError(f"launch bundle schema_version must be {MANIFEST_VERSION}")
    digest = manifest.get("digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise ContractError("launch bundle manifest has no digest")
    receipts = manifest.get("files")
    if not isinstance(receipts, list):
        raise ContractError("launch bundle manifest.files must be a list")
    expected_paths: set[str] = set()
    for index, receipt_raw in enumerate(receipts):
        receipt = _mapping(receipt_raw, f"manifest.files[{index}]")
        path_value = receipt.get("path")
        expected_hash = receipt.get("sha256")
        expected_size = receipt.get("size")
        if not isinstance(path_value, str) or not path_value:
            raise ContractError(f"manifest.files[{index}].path must be a string")
        relative = Path(path_value)
        if relative.is_absolute() or ".." in relative.parts:
            raise ContractError(f"manifest.files[{index}].path must be relative")
        path = bundle / relative
        if not path.is_file():
            raise ContractError(f"launch bundle file is missing: {path_value}")
        if _sha256(path) != expected_hash or path.stat().st_size != expected_size:
            raise ContractError(f"launch bundle file drift: {path_value}")
        expected_paths.add(relative.as_posix())
    actual_paths = {
        path.relative_to(bundle).as_posix()
        for path in bundle.rglob("*")
        if path.is_file() and path != manifest_path
    }
    if actual_paths != expected_paths:
        raise ContractError(
            f"launch bundle file set drift: missing={sorted(expected_paths - actual_paths)}, "
            f"extra={sorted(actual_paths - expected_paths)}"
        )
    payload = {key: value for key, value in manifest.items() if key not in {"digest", "runtime"}}
    actual_digest = "sha256:" + hashlib.sha256(_canonical(payload)).hexdigest()
    if actual_digest != digest:
        raise ContractError(f"launch bundle manifest digest drift: expected={digest}, actual={actual_digest}")
    return manifest


def _reserve_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("127.0.0.1", 0))
        return int(server.getsockname()[1])


def _broker_environment(omp: str) -> tuple[dict[str, str], subprocess.Popen[bytes] | None]:
    url = os.environ.get("OMP_AUTH_BROKER_URL")
    token = os.environ.get("OMP_AUTH_BROKER_TOKEN")
    if bool(url) != bool(token):
        raise ContractError("OMP_AUTH_BROKER_URL and OMP_AUTH_BROKER_TOKEN must be set together")
    if url and token:
        return {"OMP_AUTH_BROKER_URL": url, "OMP_AUTH_BROKER_TOKEN": token}, None
    broker_process_env = os.environ.copy()
    broker_process_env.pop("PI_CODING_AGENT_DIR", None)
    broker_process_env.pop("OMP_PROFILE", None)
    token_result = subprocess.run(
        [omp, "auth-broker", "token"],
        env=broker_process_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        timeout=10,
    )
    broker_token = token_result.stdout.strip()
    if token_result.returncode or not broker_token:
        raise ContractError("cannot obtain an OMP auth-broker token from the default credential store")
    port = _reserve_loopback_port()
    broker_url = f"http://127.0.0.1:{port}"
    broker = subprocess.Popen(
        [omp, "auth-broker", "serve", "--bind", f"127.0.0.1:{port}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=broker_process_env,
    )
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if broker.poll() is not None:
            raise ContractError("temporary OMP auth broker exited before becoming ready")
        try:
            with urllib.request.urlopen(f"{broker_url}/v1/healthz", timeout=0.5) as response:
                if response.status == 200:
                    return {
                        "OMP_AUTH_BROKER_URL": broker_url,
                        "OMP_AUTH_BROKER_TOKEN": broker_token,
                    }, broker
        except OSError:
            time.sleep(0.05)
    broker.terminate()
    broker.wait(timeout=5)
    raise ContractError("temporary OMP auth broker did not become ready")


def run_bundle(bundle: Path, prompt: str, *, mode: str = "text", omp: str = "omp") -> int:
    manifest = verify_bundle(bundle)
    composition = _mapping(manifest.get("composition"), "manifest.composition")
    execution = _mapping(manifest.get("execution"), "manifest.execution")
    repository_receipt = _mapping(manifest.get("repository"), "manifest.repository")
    runtime = _mapping(manifest.get("runtime"), "manifest.runtime")
    repository = Path(_string(runtime, "repository_path", "manifest.runtime"))
    if not repository.is_dir():
        raise ContractError(f"compiled repository is unavailable: {repository}")
    manifest_agent = _string(composition, "agent", "manifest.composition")
    manifest_subagents = _mapping(composition.get("subagents"), "manifest.composition.subagents")
    manifest_allowed_agents = manifest_subagents.get("allowed")
    if not isinstance(manifest_allowed_agents, list) or not all(
        isinstance(item, str) for item in manifest_allowed_agents
    ):
        raise ContractError("manifest.composition.subagents.allowed must be a string list")
    _reject_undeclared_project_agents(repository, {manifest_agent, *manifest_allowed_agents})
    repository_digest, repository_file_count = _repository_receipt(repository)
    if repository_digest != repository_receipt.get("digest"):
        raise ContractError("compiled repository drift")
    if repository_file_count != repository_receipt.get("file_count"):
        raise ContractError("compiled repository file-count drift")
    if mode not in {"text", "json"}:
        raise ContractError("run mode must be text or json")
    broker: subprocess.Popen[bytes] | None = None
    max_time_seconds = execution.get("max_time_seconds")
    if (
        not isinstance(max_time_seconds, int)
        or isinstance(max_time_seconds, bool)
        or not 1 <= max_time_seconds <= 3600
    ):
        raise ContractError("manifest.execution.max_time_seconds must be an integer from 1 through 3600")
    try:
        broker_env, broker = _broker_environment(omp)
        with tempfile.TemporaryDirectory(prefix="omp-launch-runtime-") as temp:
            runtime_agent = Path(temp) / "agent"
            shutil.copytree(bundle / "agent", runtime_agent)
            env = os.environ.copy()
            env.pop("OMP_PROFILE", None)
            env.pop("PI_CONFIG_FILES", None)
            env.update(broker_env)
            env["PI_CODING_AGENT_DIR"] = str(runtime_agent)
            skills = composition.get("skills")
            tools = composition.get("tools")
            if not isinstance(skills, list) or not all(isinstance(item, str) for item in skills):
                raise ContractError("manifest.composition.skills must be a string list")
            if not isinstance(tools, list) or not tools or not all(isinstance(item, str) for item in tools):
                raise ContractError("manifest.composition.tools must be a non-empty string list")
            args = [
                omp,
                "--cwd",
                str(repository),
                "--model",
                _string(composition, "model", "manifest.composition"),
                "--system-prompt",
                (bundle / "system-prompt.txt").read_text(),
                "--append-system-prompt",
                "",
                "--tools",
                ",".join(tools),
                "--thinking",
                _string(composition, "thinking", "manifest.composition"),
                "--approval-mode",
                _string(execution, "approval_mode", "manifest.execution"),
                "--max-time",
                str(max_time_seconds),
                "--mode",
                mode,
                "--no-rules",
                "--no-extensions",
                "--no-session",
                "--print",
            ]
            if skills:
                args.extend(["--skills", ",".join(skills)])
            else:
                args.append("--no-skills")
            args.append(prompt)
            process = subprocess.Popen(args, cwd=repository, env=env, start_new_session=True)
            try:
                return process.wait(timeout=max_time_seconds + 10)
            except subprocess.TimeoutExpired as error:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait(timeout=5)
                raise ContractError(f"OMP exceeded launch timeout ({max_time_seconds}s plus 10s grace)") from error
    finally:
        if broker is not None and broker.poll() is None:
            broker.terminate()
            try:
                broker.wait(timeout=5)
            except subprocess.TimeoutExpired:
                broker.kill()
                broker.wait(timeout=5)
