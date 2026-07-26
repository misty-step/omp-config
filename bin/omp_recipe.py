#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

SCHEMA = "omp.recipe.v1"
LAUNCH_SCHEMA = "omp.recipe.launch.v1"
OWNER_FILE = ".omp-recipe-owned"
RECIPE_FILE = "recipe.json"
INSTRUCTIONS_FILE = "instructions.md"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
REASONING_LEVELS = {
    "off",
    "minimal",
    "low",
    "medium",
    "high",
    "xhigh",
    "max",
    "auto",
}
OPENROUTER_BASE_URL = "http://100.108.0.89:4949/proxy/https/openrouter.ai/api/v1"
# The mint alias whose credential every compiled bundle runs as. Overridable
# so a workload (e.g. the Hatchet PR factory) can ride its own child key with
# its own spend cap and its own audit trail, without forking the compiler.
# The value is a PLACEHOLDER name, never a credential: the broker resolves it
# host-side, and an invalid name fails closed at the proxy with 403.
OPENROUTER_API_KEY = f"__mint.openrouter.{os.environ.get('OMP_RECIPE_MINT_ALIAS', 'default')}__"
_STATE_FILES = {
    "agent.db",
    "agent.db-shm",
    "agent.db-wal",
    "models.db",
    "models.db-shm",
    "models.db-wal",
}
_STATE_DIRECTORIES = {"sessions"}


class RecipeError(ValueError):
    pass


@dataclass(frozen=True)
class PreparedRuntime:
    recipe: dict[str, Any]
    root: Path
    agent_dir: Path
    home: Path
    cwd: Path
    env: dict[str, str]


def _obj(value: Any, label: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise RecipeError(f"{label} must be an object")
    return value


def _str(value: Any, label: str) -> str:
    if type(value) is not str or not value:
        raise RecipeError(f"{label} must be a non-empty string")
    return value


def _name(value: Any, label: str) -> str:
    name = _str(value, label)
    if not NAME_RE.fullmatch(name):
        raise RecipeError(f"{label} must match {NAME_RE.pattern}")
    return name


def _relative(value: Any, label: str) -> Path:
    text = _str(value, label)
    path = Path(text)
    if path.is_absolute() or path == Path(".") or ".." in path.parts:
        raise RecipeError(f"{label} must be a safe relative path")
    return path


def _validate_mcp(value: Any, label: str) -> None:
    entry = _obj(value, label)
    if "name" not in entry:
        raise RecipeError(f"{label} requires name")
    _name(entry["name"], f"{label}.name")
    if ("command" in entry) == ("url" in entry):
        raise RecipeError(f"{label} requires exactly one of command or url")
    if "command" in entry:
        if set(entry) - {"name", "command", "args", "env"}:
            raise RecipeError(f"{label} has unknown fields")
        _str(entry["command"], f"{label}.command")
        if "args" in entry and (
            type(entry["args"]) is not list
            or not all(type(item) is str for item in entry["args"])
        ):
            raise RecipeError(f"{label}.args must be a string list")
        if "env" in entry and (
            type(entry["env"]) is not dict
            or not all(
                type(name) is str and type(item) is str
                for name, item in entry["env"].items()
            )
        ):
            raise RecipeError(f"{label}.env must be a string mapping")
    else:
        if set(entry) - {"name", "url", "headers"}:
            raise RecipeError(f"{label} has unknown fields")
        _str(entry["url"], f"{label}.url")
        if "headers" in entry and (
            type(entry["headers"]) is not dict
            or not all(
                type(name) is str and type(item) is str
                for name, item in entry["headers"].items()
            )
        ):
            raise RecipeError(f"{label}.headers must be a string mapping")


def validate_recipe(raw: Any) -> dict[str, Any]:
    recipe = _obj(raw, "recipe")
    required = {"schemaVersion", "instructions", "models", "skills", "taskSkills", "mcpServers"}
    if set(recipe) != required:
        raise RecipeError(f"recipe keys must be exactly {sorted(required)}")
    if recipe["schemaVersion"] != SCHEMA:
        raise RecipeError(f"schemaVersion must be {SCHEMA}")

    _relative(recipe["instructions"], "instructions")
    models = recipe["models"]
    if type(models) is not list or not models:
        raise RecipeError("models must be a non-empty list")
    seen_models: set[tuple[str, str]] = set()
    for index, value in enumerate(models):
        model = _obj(value, f"models[{index}]")
        if set(model) != {"provider", "model", "reasoning"}:
            raise RecipeError(f"models[{index}] keys invalid")
        provider = _name(model["provider"], f"models[{index}].provider")
        model_name = _str(model["model"], f"models[{index}].model")
        reasoning = model["reasoning"]
        if reasoning not in REASONING_LEVELS:
            raise RecipeError(
                f"models[{index}].reasoning must be one of {sorted(REASONING_LEVELS)}"
            )
        identity = (provider, model_name)
        if identity in seen_models:
            raise RecipeError("duplicate model entry")
        seen_models.add(identity)

    skills = recipe["skills"]
    if type(skills) is not list:
        raise RecipeError("skills must be a list")
    skill_names: set[str] = set()
    skill_paths: set[Path] = set()
    for index, value in enumerate(skills):
        skill = _obj(value, f"skills[{index}]")
        if set(skill) != {"name", "path"}:
            raise RecipeError(f"skills[{index}] keys invalid")
        name = _name(skill["name"], f"skills[{index}].name")
        path = _relative(skill["path"], f"skills[{index}].path")
        if name in skill_names:
            raise RecipeError("duplicate skill entry")
        if path in skill_paths:
            raise RecipeError("duplicate skill source path")
        skill_names.add(name)
        skill_paths.add(path)

    task_skills = recipe["taskSkills"]
    if type(task_skills) is not list:
        raise RecipeError("taskSkills must be a list")
    task_skill_names: set[str] = set()
    task_skill_paths: set[Path] = set()
    for index, value in enumerate(task_skills):
        skill = _obj(value, f"taskSkills[{index}]")
        if set(skill) != {"name", "path"}:
            raise RecipeError(f"taskSkills[{index}] keys invalid")
        name = _name(skill["name"], f"taskSkills[{index}].name")
        path = _relative(skill["path"], f"taskSkills[{index}].path")
        if name in task_skill_names:
            raise RecipeError(f"duplicate taskSkill entry at taskSkills[{index}]")
        if path in task_skill_paths:
            raise RecipeError(f"duplicate taskSkill source path at taskSkills[{index}]")
        task_skill_names.add(name)
        task_skill_paths.add(path)

    if type(recipe["mcpServers"]) is not list:
        raise RecipeError("mcpServers must be a list")
    mcp_names: set[str] = set()
    for index, value in enumerate(recipe["mcpServers"]):
        _validate_mcp(value, f"mcpServers[{index}]")
        name = value["name"]
        if name in mcp_names:
            raise RecipeError("duplicate MCP server entry")
        mcp_names.add(name)
    return recipe


def _path_without_links(root: Path, relative: Path, label: str) -> Path:
    try:
        source_root = root.resolve(strict=True)
    except OSError as error:
        raise RecipeError(f"source root is unavailable: {error}") from error
    candidate = root
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise RecipeError(f"{label} must not contain symlinks")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(source_root)
    except (OSError, ValueError) as error:
        raise RecipeError(f"{label} escapes its root") from error
    return resolved


def _regular_file(root: Path, relative: Path, label: str) -> Path:
    path = _path_without_links(root, relative, label)
    if not path.is_file():
        raise RecipeError(f"{label} must be a regular file: {path}")
    if path.stat().st_nlink > 1:
        raise RecipeError(f"{label} must not be a hard-linked file: {path}")
    return path


def _directory(root: Path, relative: Path, label: str) -> Path:
    directory = _path_without_links(root, relative, label)
    if not directory.is_dir():
        raise RecipeError(f"{label} must be a directory: {directory}")
    for current, directories, files in os.walk(directory, followlinks=False):
        current_path = Path(current)
        for name in directories:
            child = current_path / name
            if child.is_symlink():
                raise RecipeError(f"{label} must not contain symlinks: {child}")
        for name in files:
            child = current_path / name
            if child.is_symlink():
                raise RecipeError(f"{label} must not contain symlinks: {child}")
            if not child.is_file():
                raise RecipeError(f"{label} contains a non-regular file: {child}")
            if child.stat().st_nlink > 1:
                raise RecipeError(
                    f"{label} must not contain hard-linked files: {child}"
                )
    return directory


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _copy_directory(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, copy_function=shutil.copy2)


def _owned_output(path: Path) -> bool:
    marker = path / OWNER_FILE
    if marker.is_symlink() or not marker.is_file():
        return False
    try:
        return marker.read_text() == f"{SCHEMA}\n"
    except OSError:
        return False


def _copy_runtime_state(source_runtime: Path, destination_runtime: Path) -> None:
    destination_runtime.mkdir()
    source_agent = source_runtime / "agent"
    if not source_agent.exists():
        return
    if source_agent.is_symlink() or not source_agent.is_dir():
        raise RecipeError("existing runtime agent path is unsafe")
    destination_agent = destination_runtime / "agent"
    destination_agent.mkdir()
    for name in sorted(_STATE_FILES):
        source = source_agent / name
        if not source.exists():
            continue
        if source.is_symlink() or not source.is_file():
            raise RecipeError(f"runtime state file is unsafe: {source}")
        _copy_file(source, destination_agent / name)
    for name in sorted(_STATE_DIRECTORIES):
        source = source_agent / name
        if not source.exists():
            continue
        safe_source = _directory(source_agent, Path(name), f"runtime state {name}")
        _copy_directory(safe_source, destination_agent / name)


def _swap_directories(first: Path, second: Path) -> bool:
    if sys.platform != "darwin":
        return False
    libc = ctypes.CDLL(None, use_errno=True)
    renameatx_np = getattr(libc, "renameatx_np", None)
    if renameatx_np is None:
        return False
    renameatx_np.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    renameatx_np.restype = ctypes.c_int
    result = renameatx_np(
        -2,
        os.fsencode(first),
        -2,
        os.fsencode(second),
        0x00000002,
    )
    if result == 0:
        return True
    error = ctypes.get_errno()
    if error in {22, 45, 95}:
        return False
    raise OSError(error, os.strerror(error))


def _install_staged_directory(stage: Path, output: Path) -> None:
    if not output.exists():
        os.replace(stage, output)
        return
    if _swap_directories(stage, output):
        shutil.rmtree(stage, ignore_errors=True)
        return
    backup = Path(tempfile.mkdtemp(prefix=f".{output.name}.backup-", dir=output.parent))
    backup.rmdir()
    os.replace(output, backup)
    try:
        os.replace(stage, output)
    except BaseException:
        os.replace(backup, output)
        raise
    shutil.rmtree(backup, ignore_errors=True)


def compile_recipe(spec_path: Path, output: Path) -> dict[str, Any]:
    if spec_path.is_symlink():
        raise RecipeError("recipe source must not be a symlink")
    try:
        recipe = validate_recipe(json.loads(spec_path.read_text()))
    except (OSError, json.JSONDecodeError, RecipeError) as error:
        raise RecipeError(f"invalid recipe: {error}") from error

    if output.is_symlink():
        raise RecipeError("recipe output must not be a symlink")
    output_exists = output.exists()
    if output_exists and (not output.is_dir() or not _owned_output(output)):
        raise RecipeError("recipe output exists but is not owned by omp.recipe.v1")
    if output_exists:
        load_recipe(output)

    base = spec_path.parent
    instructions = _regular_file(
        base, _relative(recipe["instructions"], "instructions"), "instructions"
    )
    skill_sources: list[tuple[dict[str, Any], Path]] = []
    for skill in recipe["skills"]:
        source = _directory(
            base,
            _relative(skill["path"], "skill.path"),
            f"skill {skill['name']}",
        )
        if not (source / "SKILL.md").is_file():
            raise RecipeError(f"skill {skill['name']} is missing SKILL.md")
        skill_sources.append((skill, source))
    for skill in recipe["taskSkills"]:
        source = _directory(
            base,
            _relative(skill["path"], "taskSkill.path"),
            f"taskSkill {skill['name']}",
        )
        if not (source / "SKILL.md").is_file():
            raise RecipeError(f"taskSkill {skill['name']} is missing SKILL.md")

    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output.name}.stage-", dir=output.parent))
    try:
        _copy_file(instructions, stage / INSTRUCTIONS_FILE)
        for skill, source in skill_sources:
            _copy_directory(source, stage / "skills" / skill["name"])
        (stage / RECIPE_FILE).write_text(json.dumps(recipe, indent=2) + "\n")
        (stage / OWNER_FILE).write_text(f"{SCHEMA}\n")
        if output_exists:
            _copy_runtime_state(output / "runtime", stage / "runtime")
        else:
            (stage / "runtime").mkdir()
        load_recipe(stage)
        _install_staged_directory(stage, output)
    except BaseException:
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)
        raise
    return recipe


def load_recipe(root: Path) -> dict[str, Any]:
    if root.is_symlink():
        raise RecipeError("compiled recipe root must not be a symlink")
    try:
        root = root.resolve(strict=True)
        if not _owned_output(root):
            raise RecipeError("compiled recipe ownership marker is missing")
        recipe_path = _regular_file(root, Path(RECIPE_FILE), "compiled recipe")
        recipe = validate_recipe(json.loads(recipe_path.read_text()))
        _regular_file(root, Path(INSTRUCTIONS_FILE), "compiled instructions")
        for skill in recipe["skills"]:
            directory = _directory(
                root,
                Path("skills") / skill["name"],
                f"compiled skill {skill['name']}",
            )
            if not (directory / "SKILL.md").is_file():
                raise RecipeError(f"compiled skill {skill['name']} is missing SKILL.md")
        runtime = root / "runtime"
        if runtime.is_symlink() or not runtime.is_dir():
            raise RecipeError("compiled recipe runtime directory is unsafe")
    except (OSError, json.JSONDecodeError, RecipeError) as error:
        raise RecipeError(str(error)) from error
    return recipe


def model_selector(model: Mapping[str, Any], *, reasoning: bool = True) -> str:
    suffix = f":{model['reasoning']}" if reasoning else ""
    return f"{model['provider']}/{model['model']}{suffix}"


def render_config(recipe: Mapping[str, Any], skill_root: Path) -> str:
    primary = model_selector(recipe["models"][0])
    fallbacks = [model_selector(model) for model in recipe["models"][1:]]
    providers = list(dict.fromkeys(model["provider"] for model in recipe["models"]))
    skill_names = [skill["name"] for skill in recipe["skills"]]
    lines = [
        "modelRoles:",
        f"  default: {json.dumps(primary)}",
        f"defaultThinkingLevel: {json.dumps(recipe['models'][0]['reasoning'])}",
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


def render_models(recipe: Mapping[str, Any]) -> str:
    if not any(model["provider"] == "openrouter" for model in recipe["models"]):
        return "providers: {}\n"
    return "\n".join(
        [
            "providers:",
            "  openrouter:",
            f"    baseUrl: {json.dumps(OPENROUTER_BASE_URL)}",
            f"    apiKey: {json.dumps(OPENROUTER_API_KEY)}",
            "",
        ]
    )


def _replace_runtime_agent(
    runtime: Path, recipe: Mapping[str, Any], bundle: Path
) -> Path:
    agent_dir = runtime / "agent"
    if agent_dir.is_symlink() or (agent_dir.exists() and not agent_dir.is_dir()):
        raise RecipeError("runtime agent path is unsafe")
    stage = Path(tempfile.mkdtemp(prefix=".agent.stage-", dir=runtime))
    try:
        if agent_dir.exists():
            preserved = stage.parent / f"{stage.name}-state"
            _copy_runtime_state(runtime, preserved)
            preserved_agent = preserved / "agent"
            if preserved_agent.exists():
                for child in preserved_agent.iterdir():
                    os.replace(child, stage / child.name)
            shutil.rmtree(preserved)
        instructions = _regular_file(bundle, Path(INSTRUCTIONS_FILE), "compiled instructions")
        _copy_file(instructions, stage / "AGENTS.md")
        skills_dir = stage / "skills"
        skills_dir.mkdir()
        for skill in recipe["skills"]:
            source = _directory(
                bundle,
                Path("skills") / skill["name"],
                f"compiled skill {skill['name']}",
            )
            _copy_directory(source, skills_dir / skill["name"])
        (stage / "config.yml").write_text(
            render_config(recipe, agent_dir / "skills")
        )
        (stage / "models.yml").write_text(render_models(recipe))
        _install_staged_directory(stage, agent_dir)
    except BaseException:
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)
        raise
    return agent_dir


def prepare_runtime(
    bundle: Path,
    cwd: Path,
    *,
    environ: Mapping[str, str] | None = None,
    runtime_root: Path | None = None,
) -> PreparedRuntime:
    if bundle.is_symlink():
        raise RecipeError("compiled recipe root must not be a symlink")
    try:
        bundle = bundle.resolve(strict=True)
    except OSError as error:
        raise RecipeError(f"compiled recipe root is unavailable: {error}") from error
    recipe = load_recipe(bundle)

    if cwd.is_symlink():
        raise RecipeError("workspace cwd must not be a symlink")
    try:
        cwd = cwd.resolve(strict=True)
    except OSError as error:
        raise RecipeError(f"workspace cwd is unavailable: {error}") from error
    if not cwd.is_dir():
        raise RecipeError("workspace cwd must be a directory")

    fresh_runtime = runtime_root is not None
    if runtime_root is None:
        runtime = bundle / "runtime"
        if runtime.is_symlink() or not runtime.is_dir():
            raise RecipeError("runtime path is unsafe")
    else:
        if not runtime_root.is_absolute():
            raise RecipeError("caller runtime root must be absolute")
        if runtime_root.is_symlink() or runtime_root.exists():
            raise RecipeError("caller runtime root must not already exist")
        try:
            parent = runtime_root.parent.resolve(strict=True)
        except OSError as error:
            raise RecipeError(f"caller runtime parent is unavailable: {error}") from error
        if not parent.is_dir():
            raise RecipeError("caller runtime parent must be a directory")
        runtime = parent / runtime_root.name
        runtime.mkdir()

    try:
        home = runtime / "home"
        if home.is_symlink() or (home.exists() and not home.is_dir()):
            raise RecipeError("runtime home path is unsafe")
        if home.exists():
            shutil.rmtree(home)
        home.mkdir()
        agent_dir = _replace_runtime_agent(runtime, recipe, bundle)

        source_env = os.environ if environ is None else environ
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
        env = {key: source_env[key] for key in inherited_keys if key in source_env}
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
        return PreparedRuntime(recipe, runtime, agent_dir, home, cwd, env)
    except BaseException:
        if fresh_runtime and runtime.exists():
            shutil.rmtree(runtime, ignore_errors=True)
        raise


def launch_descriptor(bundle: Path, prepared: PreparedRuntime) -> dict[str, Any]:
    session_dir = prepared.root / "sessions"
    session_dir.mkdir()
    model = prepared.recipe["models"][0]
    return {
        "schemaVersion": LAUNCH_SCHEMA,
        "bundle": str(bundle.resolve()),
        "cwd": str(prepared.cwd),
        "runtimeRoot": str(prepared.root),
        "agentDir": str(prepared.agent_dir),
        "home": str(prepared.home),
        "sessionDir": str(session_dir),
        "model": {
            "provider": model["provider"],
            "id": model["model"],
            "reasoning": model["reasoning"],
        },
        "env": prepared.env,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare-runtime", add_help=False)
    prepare.add_argument("--bundle", required=True)
    prepare.add_argument("--cwd", required=True)
    prepare.add_argument("--runtime-root", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parse_args(sys.argv[1:] if argv is None else argv)
        if args.command != "prepare-runtime":
            raise RecipeError(f"unsupported command: {args.command}")
        bundle = Path(args.bundle)
        prepared = prepare_runtime(
            bundle,
            Path(args.cwd),
            runtime_root=Path(args.runtime_root),
        )
        print(json.dumps(launch_descriptor(bundle, prepared), separators=(",", ":")))
        return 0
    except (OSError, RecipeError) as error:
        print(f"omp_recipe: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
