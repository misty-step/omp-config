#!/usr/bin/env python3
from __future__ import annotations
import json, os, re, shutil, subprocess, sys, threading
from pathlib import Path
from typing import Any

SCHEMA = "buzz-omp.bundle.v1"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
REASONING_LEVELS = {"off", "minimal", "low", "medium", "high", "xhigh", "max", "auto"}
SESSION_METHODS = {"session/new", "session/load", "session/resume", "session/fork"}
OPENROUTER_BASE_URL = "http://100.108.0.89:4949/proxy/https/openrouter.ai/api/v1"
OPENROUTER_API_KEY = "__mint.openrouter.default__"


class BundleError(ValueError):
    pass


def _obj(v: Any, label: str) -> dict[str, Any]:
    if type(v) is not dict:
        raise BundleError(f"{label} must be an object")
    return v


def _str(v: Any, label: str) -> str:
    if type(v) is not str or not v:
        raise BundleError(f"{label} must be a non-empty string")
    return v


def _name(v: Any, label: str) -> str:
    value = _str(v, label)
    if not NAME_RE.fullmatch(value):
        raise BundleError(f"{label} must match {NAME_RE.pattern}")
    return value


def _rel(v: Any, label: str) -> Path:
    s = _str(v, label)
    p = Path(s)
    if p.is_absolute() or p == Path(".") or ".." in p.parts:
        raise BundleError(f"{label} must be a safe relative path")
    return p


def _validate_mcp(v: Any, label: str) -> None:
    e = _obj(v, label)
    if "name" not in e:
        raise BundleError(f"{label} requires name")
    _str(e["name"], f"{label}.name")
    if ("command" in e) == ("url" in e):
        raise BundleError(f"{label} requires exactly one of command or url")
    if "command" in e:
        if set(e) - {"name", "command", "args", "env"}:
            raise BundleError(f"{label} has unknown fields")
        _str(e["command"], f"{label}.command")
        if "args" in e and (
            type(e["args"]) is not list or not all(type(x) is str for x in e["args"])
        ):
            raise BundleError(f"{label}.args must be a string list")
        if "env" in e and (
            type(e["env"]) is not dict
            or not all(type(k) is str and type(x) is str for k, x in e["env"].items())
        ):
            raise BundleError(f"{label}.env must be a string mapping")
    else:
        if set(e) - {"name", "url", "headers"}:
            raise BundleError(f"{label} has unknown fields")
        _str(e["url"], f"{label}.url")
        if "headers" in e and (
            type(e["headers"]) is not dict
            or not all(
                type(k) is str and type(x) is str for k, x in e["headers"].items()
            )
        ):
            raise BundleError(f"{label}.headers must be a string mapping")


def validate_manifest(raw: Any) -> dict[str, Any]:
    m = _obj(raw, "manifest")
    required = {"schemaVersion", "agent", "models", "agentsMd", "skills", "mcpServers"}
    if set(m) != required:
        raise BundleError(f"manifest keys must be exactly {sorted(required)}")
    if m["schemaVersion"] != SCHEMA:
        raise BundleError(f"schemaVersion must be {SCHEMA}")

    agent = _obj(m["agent"], "agent")
    if set(agent) != {"name", "displayName"}:
        raise BundleError("agent keys must be name and displayName")
    _name(agent["name"], "agent.name")
    _str(agent["displayName"], "agent.displayName")

    models = m["models"]
    if type(models) is not list or not models:
        raise BundleError("models must be a non-empty list")
    seen_models: set[tuple[str, str]] = set()
    for i, entry in enumerate(models):
        entry = _obj(entry, f"models[{i}]")
        if set(entry) != {"provider", "model", "reasoning"}:
            raise BundleError(f"models[{i}] keys invalid")
        provider = _name(entry["provider"], f"models[{i}].provider")
        model = _str(entry["model"], f"models[{i}].model")
        if provider != "openrouter":
            raise BundleError(
                "buzz-omp bundle v1 supports only the openrouter provider"
            )
        reasoning = entry["reasoning"]
        if reasoning not in REASONING_LEVELS:
            raise BundleError(
                f"models[{i}].reasoning must be one of {sorted(REASONING_LEVELS)}"
            )
        identity = (provider, model)
        if identity in seen_models:
            raise BundleError("duplicate model entry")
        seen_models.add(identity)

    _rel(m["agentsMd"], "agentsMd")
    skills = m["skills"]
    if type(skills) is not list:
        raise BundleError("skills must be a list")
    skill_names: set[str] = set()
    skill_paths: set[Path] = set()
    for i, entry in enumerate(skills):
        entry = _obj(entry, f"skills[{i}]")
        if set(entry) != {"name", "path"}:
            raise BundleError(f"skills[{i}] keys invalid")
        name = _name(entry["name"], f"skills[{i}].name")
        path = _rel(entry["path"], f"skills[{i}].path")
        if name in skill_names:
            raise BundleError("duplicate skill entry")
        if path in skill_paths:
            raise BundleError("duplicate skill source path")
        skill_names.add(name)
        skill_paths.add(path)
        if path.parts[0] != "skills":
            raise BundleError("skill path must be under skills/")

    if type(m["mcpServers"]) is not list:
        raise BundleError("mcpServers must be a list")
    mcp_names: set[str] = set()
    for i, entry in enumerate(m["mcpServers"]):
        _validate_mcp(entry, f"mcpServers[{i}]")
        name = _name(entry["name"], f"mcpServers[{i}].name")
        if name in mcp_names:
            raise BundleError("duplicate MCP server entry")
        mcp_names.add(name)
    return m


def _copy_checked(src: Path, dest: Path) -> None:
    if not src.is_file():
        raise BundleError(f"missing file: {src}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _source_file(base: Path, relative: Path, label: str) -> Path:
    root = base.resolve(strict=True)
    candidate = base
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise BundleError(f"{label} must not contain symlinks")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as error:
        raise BundleError(f"{label} escapes the source root") from error
    if not resolved.is_file():
        raise BundleError(f"missing file: {resolved}")
    return resolved


def _bundle_file(root: Path, relative: Path, label: str) -> Path:
    candidate = root
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise BundleError(f"{label} must not contain symlinks")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as error:
        raise BundleError(f"{label} escapes the bundle root") from error
    if not resolved.is_file():
        raise BundleError(f"missing file: {resolved}")
    return resolved


def _reject_runtime_links(runtime: Path) -> None:
    directories = (
        runtime,
        runtime / "agent",
        runtime / "agent" / "skills",
        runtime / "home",
        runtime / "cwd",
    )
    files = (
        runtime / "agent" / "AGENTS.md",
        runtime / "agent" / "config.yml",
        runtime / "agent" / "models.yml",
    )
    for path in directories:
        if path.is_symlink():
            raise BundleError(f"runtime path must not be a symlink: {path}")
        if path.exists() and not path.is_dir():
            raise BundleError(f"runtime path must be a directory: {path}")
    for path in files:
        if path.is_symlink():
            raise BundleError(f"runtime file must not be a symlink: {path}")
        if path.exists() and not path.is_file():
            raise BundleError(f"runtime file must be a regular file: {path}")


def _selector(model: dict[str, Any]) -> str:
    return f"{model['provider']}/{model['model']}:{model['reasoning']}"


def _acp_selector(model: dict[str, Any]) -> str:
    return f"{model['provider']}/{model['model']}"


def _render_config(m: dict[str, Any], skill_root: Path) -> str:
    primary = _selector(m["models"][0])
    fallbacks = [_selector(model) for model in m["models"][1:]]
    providers = list(dict.fromkeys(model["provider"] for model in m["models"]))
    skill_names = [skill["name"] for skill in m["skills"]]
    lines = [
        "modelRoles:",
        f"  default: {json.dumps(primary)}",
        f"defaultThinkingLevel: {json.dumps(m['models'][0]['reasoning'])}",
        "disabledProviders: []",
        "modelProviderOrder:",
        *[f"  - {json.dumps(provider)}" for provider in providers],
        "retry:",
        "  enabled: true",
        "  maxRetries: 0",
        "  modelFallback: true",
        "  fallbackRevertPolicy: never",
        "  fallbackChains:",
        "    default:",
        *([f"      - {json.dumps(model)}" for model in fallbacks] or ["      []"]),
        "skills:",
        f"  enabled: {'true' if skill_names else 'false'}",
        "  enableSkillCommands: true",
        "  includeSkills:",
        *([f"    - {json.dumps(name)}" for name in skill_names] or ["    []"]),
        "  customDirectories:",
        f"    - {json.dumps(str(skill_root))}",
        "  enableCodexUser: false",
        "  enableClaudeUser: false",
        "  enableClaudeProject: false",
        "  enablePiUser: false",
        "  enablePiProject: false",
        "  enableAgentsUser: false",
        "  enableAgentsProject: false",
        "commands:",
        "  enableClaudeUser: false",
        "  enableClaudeProject: false",
        "  enableOpencodeUser: false",
        "  enableOpencodeProject: false",
        "mcp:",
        "  enableProjectConfig: false",
    ]
    return "\n".join(lines) + "\n"


def _render_models() -> str:
    return "\n".join(
        [
            "providers:",
            "  openrouter:",
            f"    baseUrl: {json.dumps(OPENROUTER_BASE_URL)}",
            f"    apiKey: {json.dumps(OPENROUTER_API_KEY)}",
            "",
        ]
    )


def _acp_mcp_servers(m: dict[str, Any]) -> list[dict[str, Any]]:
    servers: list[dict[str, Any]] = []
    for entry in m["mcpServers"]:
        if "command" in entry:
            server = {
                "name": entry["name"],
                "command": entry["command"],
                "args": entry.get("args", []),
                "env": [
                    {"name": name, "value": value}
                    for name, value in sorted(entry.get("env", {}).items())
                ],
            }
        else:
            server = {
                "name": entry["name"],
                "type": "http",
                "url": entry["url"],
                "headers": [
                    {"name": name, "value": value}
                    for name, value in sorted(entry.get("headers", {}).items())
                ],
            }
        servers.append(server)
    return servers


def compile_bundle(spec_path: Path, out: Path) -> dict[str, Any]:
    if spec_path.is_symlink():
        raise BundleError("manifest source must not be a symlink")
    try:
        raw = json.loads(spec_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise BundleError(f"invalid spec: {error}") from error
    m = validate_manifest(raw)
    base = spec_path.parent
    if out.is_symlink():
        raise BundleError("bundle output must not be a symlink")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    _copy_checked(
        _source_file(base, _rel(m["agentsMd"], "agentsMd"), "agentsMd"),
        out / "agent" / "AGENTS.md",
    )
    for skill in m["skills"]:
        source = _source_file(
            base, _rel(skill["path"], "skill.path"), f"skill {skill['name']}"
        )
        _copy_checked(source, out / "agent" / "skills" / skill["name"] / "SKILL.md")
    (out / "runtime").mkdir(parents=True)
    (out / "manifest.json").write_text(json.dumps(m, indent=2) + "\n")
    return m


def _load_bundle(root: Path) -> dict[str, Any]:
    if root.is_symlink():
        raise BundleError("bundle root must not be a symlink")
    try:
        root = root.resolve(strict=True)
        manifest = _bundle_file(root, Path("manifest.json"), "bundle manifest")
        m = validate_manifest(json.loads(manifest.read_text()))
        _bundle_file(root, Path("agent/AGENTS.md"), "bundle AGENTS.md")
        for skill in m["skills"]:
            _bundle_file(
                root,
                Path("agent/skills") / skill["name"] / "SKILL.md",
                f"bundle skill {skill['name']}",
            )
        runtime = root / "runtime"
        _reject_runtime_links(runtime)
        if not runtime.is_dir():
            raise BundleError("bundle runtime directory missing")
    except (OSError, json.JSONDecodeError, BundleError) as error:
        raise BundleError(str(error)) from error
    return m


def run_proxy(bundle: Path) -> int:
    if bundle.is_symlink():
        raise BundleError("bundle root must not be a symlink")
    try:
        bundle = bundle.resolve(strict=True)
    except OSError as error:
        raise BundleError(f"bundle root is unavailable: {error}") from error
    m = _load_bundle(bundle)
    omp = os.environ.get("BUZZ_OMP_OMP", "/Users/phaedrus/.bun/bin/omp")
    runtime = bundle / "runtime"
    agent_dir = runtime / "agent"
    home = runtime / "home"
    cwd = runtime / "cwd"
    skills_dir = agent_dir / "skills"
    _reject_runtime_links(runtime)

    if home.exists():
        shutil.rmtree(home)
    if cwd.exists():
        shutil.rmtree(cwd)
    if skills_dir.exists():
        shutil.rmtree(skills_dir)
    _reject_runtime_links(runtime)
    for path in (agent_dir, home, cwd, skills_dir):
        path.mkdir(parents=True, exist_ok=True)

    source_agents = _bundle_file(bundle, Path("agent/AGENTS.md"), "bundle AGENTS.md")
    shutil.copy2(source_agents, cwd / "AGENTS.md")
    shutil.copy2(source_agents, agent_dir / "AGENTS.md")
    for skill in m["skills"]:
        source = _bundle_file(
            bundle,
            Path("agent/skills") / skill["name"] / "SKILL.md",
            f"bundle skill {skill['name']}",
        )
        destination = skills_dir / skill["name"] / "SKILL.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    (agent_dir / "config.yml").write_text(_render_config(m, skills_dir))
    (agent_dir / "models.yml").write_text(_render_models())

    inherited_keys = (
        "PATH",
        "TMPDIR",
        "LANG",
        "LC_ALL",
        "TERM",
        "SSL_CERT_FILE",
        "SSL_CERT_DIR",
        "NO_PROXY",
    )
    env = {key: os.environ[key] for key in inherited_keys if key in os.environ}
    env.update(
        {
            "HOME": str(home),
            "XDG_CONFIG_HOME": str(home / ".config"),
            "CODEX_HOME": str(home / ".codex"),
            "CLAUDE_CONFIG_DIR": str(home / ".claude"),
            "PI_CODING_AGENT_DIR": str(agent_dir),
            "PI_CONFIG_FILES": "",
            "PI_CONFIG_FILE": "/dev/null",
            "PI_SKIP_CWD_CONFIG": "1",
        }
    )

    try:
        child = subprocess.Popen(
            [omp, "--no-extensions", "acp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=cwd,
            text=True,
            bufsize=1,
        )
    except OSError as error:
        print(f"buzz-omp: {error}", file=sys.stderr)
        return 1
    assert child.stdin and child.stdout and child.stderr
    mcp_servers = _acp_mcp_servers(m)
    allowed_models = [_acp_selector(m["models"][0])]
    allowed_model_set = set(allowed_models)
    allowed_thinking = [m["models"][0]["reasoning"]]
    allowed_thinking_set = set(allowed_thinking)
    creation_ids: set[Any] = set()
    creation_lock = threading.Lock()
    stdout_lock = threading.Lock()

    def write_parent(payload: str) -> None:
        with stdout_lock:
            sys.stdout.write(payload)
            sys.stdout.flush()

    def reject_config_request(message: dict[str, Any], config_id: str) -> None:
        response = {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {
                "code": -32602,
                "message": f"{config_id} is not allowed by the Buzz OMP bundle",
            },
        }
        write_parent(json.dumps(response, separators=(",", ":")) + "\n")

    def filter_config_options(message: dict[str, Any]) -> None:
        result = message.get("result")
        if type(result) is not dict or type(result.get("configOptions")) is not list:
            return
        allowed_by_id = {
            "model": (allowed_models, allowed_model_set),
            "thinking": (allowed_thinking, allowed_thinking_set),
        }
        for option in result["configOptions"]:
            if type(option) is not dict or option.get("id") not in allowed_by_id:
                continue
            allowed, allowed_set = allowed_by_id[option["id"]]
            available = option.get("options")
            if type(available) is list:
                by_value = {
                    item.get("value"): item
                    for item in available
                    if type(item) is dict and type(item.get("value")) is str
                }
                option["options"] = [
                    by_value[value] for value in allowed if value in by_value
                ]
            if option.get("currentValue") not in allowed_set:
                option["currentValue"] = allowed[0]

    def to_child() -> None:
        try:
            for line in sys.stdin:
                forwarded = line
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    message = None
                if type(message) is dict:
                    method = message.get("method")
                    params = message.get("params")
                    if type(params) is not dict:
                        params = {}
                    requested_config = None
                    requested_value = None
                    if method == "session/set_config_option":
                        requested_config = params.get("configId")
                        requested_value = params.get("value")
                    elif method in SESSION_METHODS and "model" in params:
                        requested_config = "model"
                        requested_value = params.get("model")
                    allowed_values = {
                        "model": allowed_model_set,
                        "thinking": allowed_thinking_set,
                    }
                    if (
                        requested_config in allowed_values
                        and requested_value not in allowed_values[requested_config]
                    ):
                        reject_config_request(message, requested_config)
                        continue
                    if method in SESSION_METHODS:
                        message["params"] = params
                        params["mcpServers"] = mcp_servers
                        params["cwd"] = str(cwd)
                        request_id = message.get("id")
                        if request_id is not None:
                            with creation_lock:
                                creation_ids.add(request_id)
                        newline = "\n" if line.endswith("\n") else ""
                        forwarded = json.dumps(message, separators=(",", ":")) + newline
                child.stdin.write(forwarded)
                child.stdin.flush()
        except (BrokenPipeError, OSError):
            pass
        finally:
            try:
                child.stdin.close()
            except OSError:
                pass

    def from_child() -> None:
        try:
            for reply in child.stdout:
                forwarded = reply
                try:
                    message = json.loads(reply)
                except json.JSONDecodeError:
                    message = None
                if type(message) is dict:
                    response_id = message.get("id")
                    with creation_lock:
                        is_creation = response_id in creation_ids
                        if is_creation:
                            creation_ids.remove(response_id)
                    if is_creation:
                        filter_config_options(message)
                        newline = "\n" if reply.endswith("\n") else ""
                        forwarded = json.dumps(message, separators=(",", ":")) + newline
                write_parent(forwarded)
        except (BrokenPipeError, OSError):
            pass

    def from_stderr() -> None:
        try:
            for diagnostic in child.stderr:
                sys.stderr.write(diagnostic)
                sys.stderr.flush()
        except (BrokenPipeError, OSError):
            pass

    incoming = threading.Thread(target=to_child, daemon=True, name="buzz-omp-input")
    outgoing = threading.Thread(target=from_child, name="buzz-omp-output")
    diagnostics = threading.Thread(target=from_stderr, name="buzz-omp-stderr")
    incoming.start()
    outgoing.start()
    diagnostics.start()
    child.wait()
    outgoing.join()
    diagnostics.join()
    return child.returncode or 0


def main(argv: list[str]) -> int:
    try:
        if len(argv) == 4 and argv[1] == "compile":
            compile_bundle(Path(argv[2]), Path(argv[3]))
            return 0
        if len(argv) == 2:
            return run_proxy(Path(argv[1]))
        if len(argv) == 1:
            bundle = os.environ.get("BUZZ_OMP_BUNDLE")
            if bundle:
                return run_proxy(Path(bundle))
        print("usage: buzz-omp compile SPEC OUT | buzz-omp BUNDLE", file=sys.stderr)
        return 2
    except BundleError as e:
        print(f"buzz-omp: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
