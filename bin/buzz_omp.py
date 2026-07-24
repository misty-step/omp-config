#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
from collections import Counter
from pathlib import Path
from typing import Any

from omp_recipe import (
    RecipeError,
    compile_recipe,
    model_selector,
    prepare_runtime,
)

SESSION_METHODS = {"session/new", "session/load", "session/resume", "session/fork"}


def _acp_mcp_servers(recipe: dict[str, Any]) -> list[dict[str, Any]]:
    servers: list[dict[str, Any]] = []
    for entry in recipe["mcpServers"]:
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


def _prepare_workspace(bundle: Path) -> Path:
    workspace = bundle / "runtime" / "cwd"
    if workspace.is_symlink() or (workspace.exists() and not workspace.is_dir()):
        raise RecipeError("runtime workspace path is unsafe")
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir()
    return workspace


def run_proxy(bundle: Path) -> int:
    if bundle.is_symlink():
        raise RecipeError("compiled recipe root must not be a symlink")
    try:
        bundle = bundle.resolve(strict=True)
    except OSError as error:
        raise RecipeError(f"compiled recipe root is unavailable: {error}") from error
    workspace = _prepare_workspace(bundle)
    prepared = prepare_runtime(bundle, workspace)
    recipe = prepared.recipe
    omp = os.environ.get("BUZZ_OMP_OMP", "/Users/phaedrus/.bun/bin/omp")

    try:
        child = subprocess.Popen(
            [omp, "--no-extensions", "acp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=prepared.env,
            cwd=prepared.cwd,
            text=True,
            bufsize=1,
        )
    except OSError as error:
        print(f"buzz-omp: {error}", file=sys.stderr)
        return 1
    assert child.stdin and child.stdout and child.stderr

    mcp_servers = _acp_mcp_servers(recipe)
    allowed_models = [model_selector(recipe["models"][0], reasoning=False)]
    allowed_model_set = set(allowed_models)
    allowed_thinking = [recipe["models"][0]["reasoning"]]
    allowed_thinking_set = set(allowed_thinking)
    creation_ids: Counter[Any] = Counter()
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
                "message": f"{config_id} is not allowed by the OMP recipe",
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
                    requested: list[tuple[str, Any]] = []
                    if method == "session/set_config_option":
                        requested.append((params.get("configId"), params.get("value")))
                    elif method in SESSION_METHODS:
                        for config_id in ("model", "thinking"):
                            if config_id in params:
                                requested.append((config_id, params[config_id]))
                    allowed_values = {
                        "model": allowed_model_set,
                        "thinking": allowed_thinking_set,
                    }
                    rejected = next(
                        (
                            config_id
                            for config_id, value in requested
                            if config_id in allowed_values
                            and value not in allowed_values[config_id]
                        ),
                        None,
                    )
                    if rejected is not None:
                        reject_config_request(message, rejected)
                        continue
                    if method in SESSION_METHODS:
                        message["params"] = params
                        params["mcpServers"] = mcp_servers
                        params["cwd"] = str(prepared.cwd)
                        request_id = message.get("id")
                        if request_id is not None:
                            with creation_lock:
                                creation_ids[request_id] += 1
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
                    is_response = "method" not in message and (
                        "result" in message or "error" in message
                    )
                    is_creation = False
                    if is_response:
                        with creation_lock:
                            is_creation = creation_ids[response_id] > 0
                            if is_creation:
                                creation_ids[response_id] -= 1
                                if creation_ids[response_id] == 0:
                                    del creation_ids[response_id]
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
            compile_recipe(Path(argv[2]), Path(argv[3]))
            return 0
        if len(argv) == 2:
            return run_proxy(Path(argv[1]))
        if len(argv) == 1:
            bundle = os.environ.get("BUZZ_OMP_BUNDLE")
            if bundle:
                return run_proxy(Path(bundle))
        print("usage: buzz-omp compile RECIPE OUT | buzz-omp COMPILED_RECIPE", file=sys.stderr)
        return 2
    except RecipeError as error:
        print(f"buzz-omp: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
