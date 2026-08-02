from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from config_contract import ContractError, THINKING_LEVELS, frontmatter, load_contract
from contract_utils import load_json, mapping, sha256_digest, sha256_file, string, strict_keys, write_json
from launch_common import (
    DISABLED_PROVIDERS,
    MANIFEST_VERSION,
    SCHEMA_VERSION,
    TOOL_NAMES,
    CompiledLaunch,
    ResolvedFile,
    agent_fields,
    agent_source,
    csv,
    id_list,
    name,
    name_list,
    reject_undeclared_project_agents,
    repository_receipt,
    resolve_inside,
    skill_source,
    validate_model,
    validate_tools,
)

SEALED_EXTRA_BUILTIN_AGENTS = frozenset({"reviewer", "security-reviewer"})


def load_profile(config_root: Path, profile: object, skills: tuple[str, ...]) -> str | None:
    if profile is None:
        return None
    profile_name = name(profile, "composition.profile")
    path = config_root / "global" / "presets" / f"{profile_name}.yml"
    if not path.is_file():
        raise ContractError(f"unresolved composition profile {profile_name!r}: {path}")
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
            f"profile {profile_name!r} is denylist-based or has no explicit skills.includeSkills allowlist; "
            "sealed launch contracts refuse it"
        )
    if tuple(include) != skills:
        raise ContractError(
            f"profile {profile_name!r} skill allowlist differs from composition.skills: "
            f"profile={include}, composition={list(skills)}"
        )
    return profile_name


def load_selected_mcp(config_root: Path, repository: Path, names: tuple[str, ...]) -> dict[str, object]:
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
        document = load_json(path, f"MCP source {source}")
        servers = mapping(document.get("mcpServers", {}), f"MCP source {source}.mcpServers")
        catalogs.append((source, path, servers))

    selected: dict[str, object] = {}
    for server_name in names:
        found = [(source, path, servers[server_name]) for source, path, servers in catalogs if server_name in servers]
        if not found:
            raise ContractError(f"unresolved MCP server {server_name!r}")
        if len(found) > 1:
            details = ", ".join(f"{source}:{path}" for source, path, _ in found)
            raise ContractError(f"duplicate sources for MCP server {server_name!r}: {details}")
        value = found[0][2]
        if not isinstance(value, dict):
            raise ContractError(f"MCP server {server_name!r} must be an object")
        selected[server_name] = value
    return {"mcpServers": selected}


def render_isolation(
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


def render_prompt(
    global_instructions: str,
    sticky_rules: str,
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
        "<sticky-rules>\n" + sticky_rules.strip() + "\n</sticky-rules>",
        "<global-constitution>\n" + global_instructions.strip() + "\n</global-constitution>",
        "<repository-contract>\n" + repository_instructions.strip() + "\n</repository-contract>",
        f'<agent-role name="{agent}">\n{agent_body.strip()}\n</agent-role>',
    ]
    for skill_name, path in skill_sources:
        _, body = frontmatter(path / "SKILL.md")
        sections.append(f'<autoloaded-skill name="{skill_name}">\n{body.strip()}\n</autoloaded-skill>')
    envelope = {
        "allowed_subagents": list(allowed_agents),
        "mcp_servers": list(mcp_servers),
        "skills": [skill_name for skill_name, _ in skill_sources],
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
    document = load_json(contract_path, "launch contract")
    strict_keys(document, {"schema_version", "name", "repository", "composition", "sandbox", "execution"}, "launch contract")
    if document.get("schema_version") != SCHEMA_VERSION:
        raise ContractError(f"launch contract schema_version must be {SCHEMA_VERSION}")
    launch_name = name(document.get("name"), "launch contract.name")

    repository_config = mapping(document.get("repository"), "repository")
    strict_keys(repository_config, {"root", "instructions"}, "repository")
    root_value = string(repository_config, "root", "repository")
    repository = Path(root_value)
    if not repository.is_absolute():
        repository = contract_path.parent / repository
    repository = repository.resolve()
    if not repository.is_dir():
        raise ContractError(f"repository.root is not a directory: {repository}")
    instructions = resolve_inside(
        repository,
        string(repository_config, "instructions", "repository"),
        "repository.instructions",
        file=True,
    )

    composition = mapping(document.get("composition"), "composition")
    strict_keys(
        composition,
        {"agent", "profile", "model", "thinking", "tools", "skills", "mcp_servers", "subagents"},
        "composition",
    )
    agent = name(composition.get("agent"), "composition.agent")
    model = string(composition, "model", "composition")
    if "/" not in model or any(character.isspace() for character in model):
        raise ContractError("composition.model must be a provider/model selector")
    thinking = string(composition, "thinking", "composition")
    if thinking not in THINKING_LEVELS:
        raise ContractError(f"composition.thinking must be one of {sorted(THINKING_LEVELS)}")
    tools = name_list(composition.get("tools"), "composition.tools", allow_empty=False)
    unknown_tools = sorted(set(tools) - TOOL_NAMES)
    if unknown_tools:
        raise ContractError(f"composition.tools names unsupported OMP tools: {', '.join(unknown_tools)}")
    skills = name_list(composition.get("skills"), "composition.skills")
    mcp_servers = id_list(composition.get("mcp_servers"), "composition.mcp_servers")

    subagents = mapping(composition.get("subagents"), "composition.subagents")
    strict_keys(subagents, {"allowed", "tools", "isolation", "max_concurrency"}, "composition.subagents")
    allowed_agents = name_list(subagents.get("allowed"), "composition.subagents.allowed")
    subagent_tools = name_list(subagents.get("tools"), "composition.subagents.tools")
    isolation = string(subagents, "isolation", "composition.subagents")
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

    sandbox = mapping(document.get("sandbox"), "sandbox")
    strict_keys(sandbox, {"filesystem", "network", "process"}, "sandbox")
    requested_sandbox = {key: string(sandbox, key, "sandbox") for key in ("filesystem", "network", "process")}
    unsupported = {key: value for key, value in requested_sandbox.items() if value != "host"}
    if unsupported:
        raise ContractError(
            "requested sandbox controls are not enforceable by OMP 17.0.7: "
            + ", ".join(f"{key}={value}" for key, value in sorted(unsupported.items()))
        )

    execution = mapping(document.get("execution"), "execution")
    strict_keys(execution, {"mode", "session", "max_time_seconds", "approval_mode"}, "execution")
    if string(execution, "mode", "execution") != "print":
        raise ContractError("omp.launch-contract.v1 supports only execution.mode='print'")
    if string(execution, "session", "execution") != "ephemeral":
        raise ContractError("omp.launch-contract.v1 supports only execution.session='ephemeral'")
    max_time_seconds = execution.get("max_time_seconds")
    if not isinstance(max_time_seconds, int) or isinstance(max_time_seconds, bool) or not 1 <= max_time_seconds <= 3600:
        raise ContractError("execution.max_time_seconds must be an integer from 1 through 3600")
    approval_mode = string(execution, "approval_mode", "execution")
    if approval_mode not in {"always-ask", "write", "yolo"}:
        raise ContractError("execution.approval_mode must be always-ask, write, or yolo")

    profile = load_profile(config_root, composition.get("profile"), skills)
    repository_digest, repository_file_count = repository_receipt(repository)

    _, root_agent_path = agent_source(config_root, repository, agent)
    root_fields, root_body = agent_fields(root_agent_path, agent)
    validate_model(root_fields, model, thinking, agent)
    validate_tools(root_fields, tools, agent)
    root_skills = set(csv(root_fields.get("autoloadSkills", "")))
    if not root_skills.issubset(skills):
        raise ContractError(
            f"composition.skills omits agent {agent} autoload skills: {sorted(root_skills - set(skills))}"
        )
    declared_spawns = root_fields.get("spawns", "").strip()
    if declared_spawns == "*":
        raise ContractError(f"agent {agent} uses wildcard spawns; sealed launch contracts require explicit agents")
    if set(csv(declared_spawns)) != set(allowed_agents):
        raise ContractError(
            f"composition.subagents.allowed must exactly match agent {agent} spawns: "
            f"expected={sorted(csv(declared_spawns))}, actual={sorted(allowed_agents)}"
        )

    reject_undeclared_project_agents(repository, {agent, *allowed_agents})

    files: list[ResolvedFile] = [ResolvedFile("agent", agent, root_agent_path, Path("agent/agents") / root_agent_path.name)]
    for child in allowed_agents:
        _, child_path = agent_source(config_root, repository, child)
        child_fields, _ = agent_fields(child_path, child)
        child_spawns = child_fields.get("spawns", "").strip()
        if child_spawns:
            raise ContractError(f"subagent {child} declares nested spawns; per-child composition is unsupported in v1")
        child_skills = set(csv(child_fields.get("autoloadSkills", "")))
        if not child_skills.issubset(skills):
            raise ContractError(
                f"composition.skills omits subagent {child} autoload skills: {sorted(child_skills - set(skills))}"
            )
        declared_child_tools = child_fields["tools"].strip()
        if declared_child_tools == "*":
            raise ContractError(f"subagent {child} uses wildcard tools; launch contracts require explicit tools")
        child_tools = set(csv(declared_child_tools))
        if not child_tools.issubset(subagent_tools):
            raise ContractError(
                f"composition.subagents.tools omits tools declared by {child}: "
                f"{sorted(child_tools - set(subagent_tools))}"
            )
        files.append(ResolvedFile("agent", child, child_path, Path("agent/agents") / child_path.name))

    skill_sources: list[tuple[str, Path]] = []
    for skill in skills:
        _, skill_path = skill_source(config_root, repository, skill)
        skill_file = skill_path / "SKILL.md"
        if not skill_file.is_file():
            raise ContractError(f"skill {skill!r} has no SKILL.md: {skill_path}")
        skill_fields, _ = frontmatter(skill_file)
        if skill_fields.get("name", skill) != skill:
            raise ContractError(f"skill {skill_path} declares name {skill_fields.get('name')!r}")
        skill_sources.append((skill, skill_path))
        files.append(ResolvedFile("skill", skill, skill_path, Path("agent/skills") / skill))
    disabled_agents = tuple(
        sorted(
            (
                set(load_contract(config_root).bundled_agents)
                | SEALED_EXTRA_BUILTIN_AGENTS
                | {agent}
            )
            - set(allowed_agents)
        )
    )

    mcp = load_selected_mcp(config_root, repository, mcp_servers)
    global_instructions_path = config_root / "global" / "AGENTS.md"
    sticky_rules_path = config_root / "global" / "RULES.md"
    if not sticky_rules_path.is_file():
        raise ContractError(f"missing sticky rules: {sticky_rules_path}")
    if not global_instructions_path.is_file():
        raise ContractError(f"missing global constitution: {global_instructions_path}")
    prompt = render_prompt(
        global_instructions_path.read_text(),
        sticky_rules_path.read_text(),
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
        name=launch_name,
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


def copy_resolved(source: Path, destination: Path) -> None:
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
            copy_resolved(resolved.source, staging / resolved.destination)
        (staging / "agent").mkdir(exist_ok=True)
        (staging / "agent" / "config.yml").write_text(
            render_isolation(launch.skills, launch.max_concurrency, launch.disabled_agents)
        )
        write_json(staging / "agent" / "mcp.json", launch.mcp)
        (staging / "system-prompt.txt").write_text(launch.prompt)
        shutil.copy2(contract_path.resolve(), staging / "contract.json")

        file_receipts = []
        for path in sorted(candidate for candidate in staging.rglob("*") if candidate.is_file()):
            relative = path.relative_to(staging).as_posix()
            file_receipts.append({"path": relative, "sha256": sha256_file(path), "size": path.stat().st_size})
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
        manifest = {
            **payload,
            "runtime": {"repository_path": str(launch.repository)},
            "digest": sha256_digest(payload),
        }
        write_json(staging / "manifest.json", manifest)
        if output.exists():
            if output.is_dir():
                shutil.rmtree(output)
            else:
                output.unlink()
        staging.replace(output)
    return manifest
