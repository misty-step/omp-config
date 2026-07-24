from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import stat
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
sys.path.insert(0, str(BIN))
import omp_recipe

MODULE_PATH = BIN / "buzz_omp.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "buzz_omp_test_module", MODULE_PATH
)
assert MODULE_SPEC and MODULE_SPEC.loader
buzz_omp = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(buzz_omp)


FAKE_CHILD = (
    "#!"
    + sys.executable
    + "\n"
    + textwrap.dedent(
        """
    import json
    import os
    import sys
    import time
    from pathlib import Path

    def emit(value):
        sys.stdout.write(json.dumps(value, separators=(",", ":")) + "\\n")
        sys.stdout.flush()

    def runtime_state():
        agent = Path(os.environ["PI_CODING_AGENT_DIR"])
        return {
            "kind": "runtime",
            "home": os.environ.get("HOME"),
            "agent": os.environ.get("PI_CODING_AGENT_DIR"),
            "cwd": os.getcwd(),
            "nested_skill": (agent / "skills" / "demo" / "SKILL.md").is_file(),
            "flat_skill": (agent / "skills" / "demo.md").exists(),
            "config": (agent / "config.yml").read_text(),
            "models": (agent / "models.yml").read_text(),
            "proxy_env": {
                key: os.environ.get(key)
                for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY")
            },
        }

    for line in sys.stdin:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            emit({"kind": "raw", "line": line})
            continue
        if isinstance(message, dict) and message.get("method") == "session/new":
            emit({"kind": "notification", "params": {"unsolicited": True}})
            emit({"kind": "response", "id": message.get("id"), "received": message})
            sys.stderr.write("fake-child-diagnostic\\n")
            sys.stderr.flush()
            time.sleep(0.15)
            emit(runtime_state())
        else:
            emit({"kind": "other", "received": message})
"""
    )
)


class BuzzOmpTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source_tmp = tempfile.TemporaryDirectory(prefix="adapter-test-source-")
        self.source = Path(self.source_tmp.name)
        (self.source / "instructions.md").write_text("agent instructions\n")
        (self.source / "skills" / "demo").mkdir(parents=True)
        (self.source / "skills" / "demo" / "SKILL.md").write_text("demo skill\n")
        (self.source / "skills" / "demo" / "references").mkdir()
        (self.source / "skills" / "demo" / "references" / "detail.md").write_text(
            "nested resource\n"
        )
        self.child_tmp = tempfile.TemporaryDirectory(prefix="adapter-test-child-")
        self.child = Path(self.child_tmp.name) / "fake-child"
        self.child.write_text(FAKE_CHILD)
        self.child.chmod(self.child.stat().st_mode | stat.S_IXUSR)

    def tearDown(self) -> None:
        self.child_tmp.cleanup()
        self.source_tmp.cleanup()

    def make_bundle(
        self, *, mcp: list[dict] | None = None, models: list[dict] | None = None
    ) -> Path:
        recipe = {
            "schemaVersion": omp_recipe.SCHEMA,
            "instructions": "instructions.md",
            "models": models
            or [
                {"provider": "openrouter", "model": "primary", "reasoning": "medium"},
                {"provider": "openrouter", "model": "fallback", "reasoning": "high"},
                {"provider": "openrouter", "model": "last", "reasoning": "low"},
            ],
            "skills": [{"name": "demo", "path": "skills/demo"}],
            "mcpServers": mcp if mcp is not None else [],
        }
        spec = self.source / "recipe.json"
        spec.write_text(json.dumps(recipe))
        bundle = self.source / "bundle"
        omp_recipe.compile_recipe(spec, bundle)
        return bundle

    def invoke(
        self, bundle: Path, request: str, *, child: Path | None = None
    ) -> tuple[int, list[dict], str]:
        stdin = io.StringIO(request)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch.dict(
            os.environ, {"BUZZ_OMP_OMP": str(child or self.child)}, clear=False
        ):
            with (
                patch.object(sys, "stdin", stdin),
                patch.object(sys, "stdout", stdout),
                patch.object(sys, "stderr", stderr),
            ):
                status = buzz_omp.run_proxy(bundle)
        lines = [line for line in stdout.getvalue().splitlines() if line]
        messages = [json.loads(line) for line in lines]
        return status, messages, stderr.getvalue()

    @staticmethod
    def session_request(mcp: list[dict] | None = None) -> str:
        message = {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "session/new",
            "params": {
                "cwd": "/caller",
                "mcpServers": mcp or [{"name": "caller", "command": "not-used"}],
            },
        }
        return json.dumps(message, separators=(",", ":")) + "\n"

    def test_stdout_purity_and_independent_messages(self) -> None:
        status, messages, stderr = self.invoke(
            self.make_bundle(), self.session_request()
        )
        self.assertEqual(status, 0)
        self.assertGreaterEqual(len(messages), 3)
        self.assertEqual(messages[0]["kind"], "notification")
        self.assertEqual(messages[1]["kind"], "response")
        self.assertEqual(messages[-1]["kind"], "runtime")
        self.assertNotIn(
            "fake-child-diagnostic",
            "\n".join(json.dumps(message) for message in messages),
        )
        self.assertIn("fake-child-diagnostic", stderr)

    def test_exact_mcp_list_replacement_non_empty(self) -> None:
        mcp = [
            {
                "name": "stdio",
                "command": "server",
                "args": ["--once"],
                "env": {"TOKEN": "placeholder"},
            }
        ]
        _, messages, _ = self.invoke(self.make_bundle(mcp=mcp), self.session_request())
        received = next(
            message for message in messages if message["kind"] == "response"
        )["received"]
        self.assertEqual(
            received["params"]["mcpServers"],
            [
                {
                    "name": "stdio",
                    "command": "server",
                    "args": ["--once"],
                    "env": [{"name": "TOKEN", "value": "placeholder"}],
                }
            ],
        )
        self.assertNotEqual(received["params"]["cwd"], "/caller")

    def test_exact_mcp_list_replacement_explicit_empty(self) -> None:
        _, messages, _ = self.invoke(self.make_bundle(mcp=[]), self.session_request())
        received = next(
            message for message in messages if message["kind"] == "response"
        )["received"]
        self.assertEqual(received["params"]["mcpServers"], [])

    def test_stderr_is_fully_drained(self) -> None:
        _, _, stderr = self.invoke(self.make_bundle(), self.session_request())
        self.assertEqual(stderr, "fake-child-diagnostic\n")

    def test_delayed_final_stdout_is_fully_drained(self) -> None:
        _, messages, _ = self.invoke(self.make_bundle(), self.session_request())
        self.assertEqual(messages[-1]["kind"], "runtime")
        self.assertTrue(messages[-1]["nested_skill"])

    def test_runtime_directories_are_stable_clean_and_isolated(self) -> None:
        bundle = self.make_bundle()
        _, first, _ = self.invoke(bundle, self.session_request())
        first_runtime = next(
            message for message in first if message["kind"] == "runtime"
        )
        agent = Path(first_runtime["agent"])
        Path(first_runtime["home"], "sentinel").write_text("remove")
        Path(first_runtime["cwd"], "sentinel").write_text("remove")
        (agent / "sentinel").write_text("remove")
        (agent / "mcp.json").write_text("{}")
        (agent / "RULES.md").write_text("stale")
        (agent / "sessions").mkdir()
        (agent / "sessions" / "history.jsonl").write_text("preserve\n")

        _, restarted, _ = self.invoke(bundle, self.session_request())
        restarted_runtime = next(
            message for message in restarted if message["kind"] == "runtime"
        )
        for key in ("home", "agent", "cwd"):
            self.assertEqual(first_runtime[key], restarted_runtime[key])
            self.assertNotEqual(restarted_runtime[key], os.environ.get("HOME"))
            self.assertTrue(Path(restarted_runtime[key]).is_absolute())
        self.assertFalse(Path(restarted_runtime["home"], "sentinel").exists())
        self.assertFalse(Path(restarted_runtime["cwd"], "sentinel").exists())
        self.assertFalse(Path(restarted_runtime["agent"], "sentinel").exists())
        self.assertFalse(Path(restarted_runtime["agent"], "mcp.json").exists())
        self.assertFalse(Path(restarted_runtime["agent"], "RULES.md").exists())
        self.assertEqual(
            Path(restarted_runtime["agent"], "sessions", "history.jsonl").read_text(),
            "preserve\n",
        )

        other_bundle = self.source / "other-bundle"
        shutil.copytree(bundle, other_bundle)
        _, other, _ = self.invoke(other_bundle, self.session_request())
        other_runtime = next(
            message for message in other if message["kind"] == "runtime"
        )
        for key in ("home", "agent", "cwd"):
            self.assertNotEqual(restarted_runtime[key], other_runtime[key])

    def test_skill_layout_is_nested_and_not_flattened(self) -> None:
        _, messages, _ = self.invoke(self.make_bundle(), self.session_request())
        runtime = next(message for message in messages if message["kind"] == "runtime")
        self.assertTrue(runtime["nested_skill"])
        self.assertFalse(runtime["flat_skill"])

    def test_discovery_is_disabled_and_skills_are_allowlisted(self) -> None:
        _, messages, _ = self.invoke(self.make_bundle(), self.session_request())
        config = next(message for message in messages if message["kind"] == "runtime")[
            "config"
        ]
        self.assertIn("includeSkills:", config)
        self.assertIn('- "demo"', config)
        self.assertIn("enableProjectConfig: false", config)
        for key in (
            "enableClaudeUser: false",
            "enableClaudeProject: false",
            "enablePiUser: false",
            "enablePiProject: false",
            "enableAgentsUser: false",
            "enableAgentsProject: false",
        ):
            self.assertIn(key, config)
        self.assertNotIn("ignoredSkills:", config)

    def test_model_cascade_uses_ordered_selectors(self) -> None:
        models = [
            {"provider": "openrouter", "model": "first", "reasoning": "low"},
            {"provider": "openrouter", "model": "second", "reasoning": "high"},
            {"provider": "openrouter", "model": "third", "reasoning": "off"},
        ]
        _, messages, _ = self.invoke(
            self.make_bundle(models=models), self.session_request()
        )
        config = next(message for message in messages if message["kind"] == "runtime")[
            "config"
        ]
        self.assertIn('default: "openrouter/first:low"', config)
        self.assertIn('      - "openrouter/second:high"', config)
        self.assertIn('      - "openrouter/third:off"', config)

    def test_provider_file_uses_mint_placeholder(self) -> None:
        _, messages, _ = self.invoke(self.make_bundle(), self.session_request())
        models = next(message for message in messages if message["kind"] == "runtime")[
            "models"
        ]
        self.assertIn(
            'baseUrl: "http://100.108.0.89:4949/proxy/https/openrouter.ai/api/v1"',
            models,
        )
        self.assertIn('apiKey: "__mint.openrouter.default__"', models)
        self.assertNotRegex(models, r"sk-[A-Za-z0-9]{12,}")

    def test_validation_failures(self) -> None:
        base = {
            "schemaVersion": omp_recipe.SCHEMA,
            "instructions": "instructions.md",
            "models": [
                {"provider": "openrouter", "model": "primary", "reasoning": "medium"}
            ],
            "skills": [{"name": "demo", "path": "skills/demo"}],
            "mcpServers": [],
        }
        cases = {
            "path traversal": {**base, "instructions": "../instructions.md"},
            "unknown key": {**base, "unexpected": True},
            "invalid reasoning": {
                **base,
                "models": [
                    {"provider": "openrouter", "model": "primary", "reasoning": "turbo"}
                ],
            },
            "malformed MCP": {**base, "mcpServers": [{"name": "broken"}]},
            "both MCP transports": {
                **base,
                "mcpServers": [{"name": "broken", "command": "x", "url": "http://x"}],
            },
            "extra MCP field": {
                **base,
                "mcpServers": [{"name": "broken", "url": "http://x", "extra": True}],
            },
            "duplicate skill name": {
                **base,
                "skills": [
                    {"name": "demo", "path": "skills/demo"},
                    {"name": "demo", "path": "skills/demo"},
                ],
            },
            "duplicate skill source": {
                **base,
                "skills": [
                    {"name": "demo", "path": "skills/demo"},
                    {"name": "other", "path": "skills/demo"},
                ],
            },
        }
        for label, recipe in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(omp_recipe.RecipeError):
                    omp_recipe.validate_recipe(recipe)

    def test_runtime_symlink_is_rejected_without_external_mutation(self) -> None:
        bundle = self.make_bundle()
        external = self.source / "external-runtime"
        external.mkdir()
        sentinel = external / "sentinel"
        sentinel.write_text("preserve")
        shutil.rmtree(bundle / "runtime")
        (bundle / "runtime").symlink_to(external, target_is_directory=True)

        with self.assertRaises(omp_recipe.RecipeError):
            self.invoke(bundle, self.session_request())

        self.assertEqual(sentinel.read_text(), "preserve")

    def test_compile_rejects_nested_symlinked_skill_source(self) -> None:
        external = self.source / "external-skill"
        external.write_text("outside")
        nested = self.source / "skills" / "demo" / "references" / "outside.md"
        nested.symlink_to(external)
        recipe = {
            "schemaVersion": omp_recipe.SCHEMA,
            "instructions": "instructions.md",
            "models": [
                {"provider": "openrouter", "model": "primary", "reasoning": "medium"}
            ],
            "skills": [{"name": "demo", "path": "skills/demo"}],
            "mcpServers": [],
        }
        spec = self.source / "symlink-recipe.json"
        spec.write_text(json.dumps(recipe))

        with self.assertRaises(omp_recipe.RecipeError):
            omp_recipe.compile_recipe(spec, self.source / "symlink-bundle")

    def test_proxy_credentials_are_not_inherited(self) -> None:
        with patch.dict(
            os.environ,
            {
                "HTTP_PROXY": "http://user:secret@example.test",
                "HTTPS_PROXY": "https://user:secret@example.test",
                "ALL_PROXY": "socks5://user:secret@example.test",
            },
            clear=False,
        ):
            _, messages, _ = self.invoke(self.make_bundle(), self.session_request())
        runtime = next(message for message in messages if message["kind"] == "runtime")
        self.assertEqual(
            runtime["proxy_env"],
            {"HTTP_PROXY": None, "HTTPS_PROXY": None, "ALL_PROXY": None},
        )

    def test_forbidden_model_selection_is_rejected_without_forwarding(self) -> None:
        request = (
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 17,
                    "method": "session/set_config_option",
                    "params": {
                        "sessionId": "session",
                        "configId": "model",
                        "value": "openrouter/unassigned",
                    },
                }
            )
            + "\n"
        )
        _, messages, _ = self.invoke(self.make_bundle(), request)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["id"], 17)
        self.assertEqual(messages[0]["error"]["code"], -32602)
        self.assertNotIn("kind", messages[0])

    def test_forbidden_thinking_selection_is_rejected_without_forwarding(
        self,
    ) -> None:
        request = (
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 18,
                    "method": "session/set_config_option",
                    "params": {
                        "sessionId": "session",
                        "configId": "thinking",
                        "value": "max",
                    },
                }
            )
            + "\n"
        )
        _, messages, _ = self.invoke(self.make_bundle(), request)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["id"], 18)
        self.assertEqual(messages[0]["error"]["code"], -32602)
        self.assertNotIn("kind", messages[0])

    def test_session_lifecycle_rejects_unassigned_model_and_thinking(self) -> None:
        forbidden = {
            "model": "openrouter/unassigned",
            "thinking": "max",
        }
        for method in sorted(buzz_omp.SESSION_METHODS):
            for config_id, value in forbidden.items():
                with self.subTest(method=method, config_id=config_id):
                    request = json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": f"{method}:{config_id}",
                            "method": method,
                            "params": {config_id: value},
                        }
                    ) + "\n"
                    _, messages, _ = self.invoke(self.make_bundle(), request)
                    self.assertEqual(len(messages), 1)
                    self.assertEqual(messages[0]["error"]["code"], -32602)
                    self.assertIn(config_id, messages[0]["error"]["message"])

    def test_same_id_child_request_does_not_consume_creation_response(self) -> None:
        child = self.source / "same-id-child"
        child.write_text(
            "#!"
            + sys.executable
            + "\n"
            + textwrap.dedent(
                """
                import json
                import sys

                for line in sys.stdin:
                    message = json.loads(line)
                    request = {
                        "jsonrpc": "2.0",
                        "id": message["id"],
                        "method": "client/same_id",
                        "params": {},
                    }
                    response = {
                        "jsonrpc": "2.0",
                        "id": message["id"],
                        "result": {
                            "sessionId": "filtered",
                            "configOptions": [{
                                "id": "model",
                                "currentValue": "openrouter/unassigned",
                                "options": [
                                    {"value": "openrouter/unassigned"},
                                    {"value": "openrouter/primary"},
                                ],
                            }],
                        },
                    }
                    print(json.dumps(request, separators=(",", ":")), flush=True)
                    print(json.dumps(response, separators=(",", ":")), flush=True)
                """
            )
        )
        child.chmod(child.stat().st_mode | stat.S_IXUSR)
        _, messages, _ = self.invoke(
            self.make_bundle(), self.session_request(), child=child
        )
        self.assertEqual(messages[0]["method"], "client/same_id")
        option = messages[1]["result"]["configOptions"][0]
        self.assertEqual(
            [item["value"] for item in option["options"]],
            ["openrouter/primary"],
        )
        self.assertEqual(option["currentValue"], "openrouter/primary")

    def test_creation_response_exposes_only_primary_model_and_thinking(self) -> None:
        child = self.source / "model-child"
        child.write_text(
            "#!"
            + sys.executable
            + "\n"
            + textwrap.dedent(
                """
                import json
                import sys

                for line in sys.stdin:
                    message = json.loads(line)
                    response = {
                        "jsonrpc": "2.0",
                        "id": message["id"],
                        "result": {
                            "sessionId": "filtered",
                            "configOptions": [
                                {
                                    "id": "model",
                                    "currentValue": "openrouter/unassigned",
                                    "options": [
                                        {"value": "openrouter/unassigned", "name": "Unassigned"},
                                        {"value": "openrouter/last", "name": "Last"},
                                        {"value": "openrouter/primary", "name": "Primary"},
                                        {"value": "openrouter/fallback", "name": "Fallback"},
                                    ],
                                },
                                {
                                    "id": "thinking",
                                    "currentValue": "max",
                                    "options": [
                                        {"value": "low", "name": "Low"},
                                        {"value": "medium", "name": "Medium"},
                                        {"value": "max", "name": "Max"},
                                    ],
                                },
                            ],
                        },
                    }
                    print(json.dumps(response, separators=(",", ":")), flush=True)
                """
            )
        )
        child.chmod(child.stat().st_mode | stat.S_IXUSR)
        _, messages, _ = self.invoke(
            self.make_bundle(), self.session_request(), child=child
        )
        model_option, thinking_option = messages[0]["result"]["configOptions"]
        self.assertEqual(
            [item["value"] for item in model_option["options"]],
            ["openrouter/primary"],
        )
        self.assertEqual(model_option["currentValue"], "openrouter/primary")
        self.assertEqual(
            [item["value"] for item in thinking_option["options"]],
            ["medium"],
        )
        self.assertEqual(thinking_option["currentValue"], "medium")

    def test_main_uses_env_bundle_without_positional_argument(self) -> None:
        with (
            patch.dict(os.environ, {"BUZZ_OMP_BUNDLE": "/env-bundle"}, clear=False),
            patch.object(buzz_omp, "run_proxy", return_value=0) as run_proxy,
        ):
            self.assertEqual(buzz_omp.main(["buzz-omp"]), 0)
        run_proxy.assert_called_once_with(Path("/env-bundle"))

    def test_main_explicit_bundle_overrides_environment(self) -> None:
        with (
            patch.dict(os.environ, {"BUZZ_OMP_BUNDLE": "/env-bundle"}, clear=False),
            patch.object(buzz_omp, "run_proxy", return_value=0) as run_proxy,
        ):
            self.assertEqual(buzz_omp.main(["buzz-omp", "/argument-bundle"]), 0)
        run_proxy.assert_called_once_with(Path("/argument-bundle"))

    def test_non_session_json_is_forwarded_without_reserialization(self) -> None:
        bundle = self.make_bundle()
        capture = bundle / "runtime" / "agent" / "captured.ndjson"
        child = self.source / "capture-child"
        child.write_text(
            "#!"
            + sys.executable
            + "\n"
            + "import os, sys\n"
            + "from pathlib import Path\n"
            + "Path(os.environ['PI_CODING_AGENT_DIR'], 'captured.ndjson').write_bytes(sys.stdin.buffer.read())\n"
        )
        child.chmod(child.stat().st_mode | stat.S_IXUSR)
        raw = (
            '{ "jsonrpc" : "2.0", "id" : 9, "method" : "other", '
            '"params" : { "x" : 1e999 } }\n'
        )
        status, messages, stderr = self.invoke(bundle, raw, child=child)
        self.assertEqual(status, 0)
        self.assertEqual(messages, [])
        self.assertEqual(stderr, "")
        self.assertEqual(capture.read_text(), raw)


if __name__ == "__main__":
    unittest.main()
