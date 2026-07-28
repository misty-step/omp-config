from __future__ import annotations

import os
import shutil
import signal
import socket
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

from config_contract import ContractError
from contract_utils import mapping, string
from launch_common import reject_undeclared_project_agents, repository_receipt
from launch_verify import verify_bundle


def reserve_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("127.0.0.1", 0))
        return int(server.getsockname()[1])


def broker_environment(omp: str) -> tuple[dict[str, str], subprocess.Popen[bytes] | None]:
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
    port = reserve_loopback_port()
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
    composition = mapping(manifest.get("composition"), "manifest.composition")
    execution = mapping(manifest.get("execution"), "manifest.execution")
    repository_receipt_value = mapping(manifest.get("repository"), "manifest.repository")
    runtime = mapping(manifest.get("runtime"), "manifest.runtime")
    repository = Path(string(runtime, "repository_path", "manifest.runtime"))
    if not repository.is_dir():
        raise ContractError(f"compiled repository is unavailable: {repository}")
    manifest_agent = string(composition, "agent", "manifest.composition")
    manifest_subagents = mapping(composition.get("subagents"), "manifest.composition.subagents")
    manifest_allowed_agents = manifest_subagents.get("allowed")
    if not isinstance(manifest_allowed_agents, list) or not all(
        isinstance(item, str) for item in manifest_allowed_agents
    ):
        raise ContractError("manifest.composition.subagents.allowed must be a string list")
    reject_undeclared_project_agents(repository, {manifest_agent, *manifest_allowed_agents})
    repository_digest, repository_file_count = repository_receipt(repository)
    if repository_digest != repository_receipt_value.get("digest"):
        raise ContractError("compiled repository drift")
    if repository_file_count != repository_receipt_value.get("file_count"):
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
        broker_env, broker = broker_environment(omp)
        with tempfile.TemporaryDirectory(prefix="omp-launch-runtime-") as temp:
            runtime_agent = Path(temp) / "agent"
            shutil.copytree(Path(bundle).resolve() / "agent", runtime_agent)
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
                string(composition, "model", "manifest.composition"),
                "--system-prompt",
                (Path(bundle).resolve() / "system-prompt.txt").read_text(),
                "--append-system-prompt",
                "",
                "--tools",
                ",".join(tools),
                "--thinking",
                string(composition, "thinking", "manifest.composition"),
                "--approval-mode",
                string(execution, "approval_mode", "manifest.execution"),
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
