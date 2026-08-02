from __future__ import annotations

import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = ROOT / "bin"
if str(BIN_DIR) not in sys.path:
    sys.path.insert(0, str(BIN_DIR))

CHECK = runpy.run_path(str(BIN_DIR / "check"))
DURABLE_AGENT_NAMES = CHECK["DURABLE_AGENT_NAMES"]
EXACT_DEEPSEEK_ROUTE = CHECK["EXACT_DEEPSEEK_ROUTE"]
EXPECTED_AGENT_MODELS = CHECK["EXPECTED_AGENT_MODELS"]
EXPECTED_AGENT_SKILLS = CHECK["EXPECTED_AGENT_SKILLS"]
EXPECTED_AGENT_THINKING = CHECK["EXPECTED_AGENT_THINKING"]
EXPECTED_AGENT_TOOLS = CHECK["EXPECTED_AGENT_TOOLS"]
check_model_route_policy = CHECK["check_model_route_policy"]
check_roster_policy = CHECK["check_roster_policy"]


class DispatchContractTests(unittest.TestCase):
    def _fields(self) -> dict[str, dict[str, str]]:
        fields: dict[str, dict[str, str]] = {}
        for name in DURABLE_AGENT_NAMES:
            fields[name] = {
                "model": ",".join(EXPECTED_AGENT_MODELS[name]),
                "thinkingLevel": EXPECTED_AGENT_THINKING[name],
                "tools": ",".join(EXPECTED_AGENT_TOOLS[name]),
                "autoloadSkills": ",".join(EXPECTED_AGENT_SKILLS[name]),
                "spawns": "qa-user-leaf" if name == "qa-user" else "",
            }
        return fields

    def _settings(self, directory: Path) -> Path:
        settings = directory / "config.yml"
        settings.write_text(
            "task:\n"
            "  maxRecursionDepth: 2\n"
            "  maxConcurrency: 12\n"
            "  disabledAgents:\n"
            "    - task\n"
            "    - scout\n"
            "    - librarian\n"
            "    - sonic\n"
            "    - reviewer\n"
            "    - security-reviewer\n"
        )
        return settings

    def test_valid_native_roster_and_persona_depth(self) -> None:
        fields = self._fields()
        with tempfile.TemporaryDirectory(prefix="dispatch-roster-") as directory:
            settings = self._settings(Path(directory))
            check_roster_policy(
                SimpleNamespace(bundled_agents=frozenset({"task", "scout", "librarian", "designer", "sonic"})),
                settings,
                set(skill for values in EXPECTED_AGENT_SKILLS.values() for skill in values),
                set(fields),
                fields,
            )

    def test_roster_rejects_verifier_persona_spawn(self) -> None:
        fields = self._fields()
        fields["verifier"]["spawns"] = "qa-user"
        with tempfile.TemporaryDirectory(prefix="dispatch-roster-") as directory:
            with self.assertRaises(SystemExit):
                check_roster_policy(
                    SimpleNamespace(bundled_agents=frozenset({"task", "scout", "librarian", "designer", "sonic"})),
                    self._settings(Path(directory)),
                    set(skill for values in EXPECTED_AGENT_SKILLS.values() for skill in values),
                    set(fields),
                    fields,
                )

    def test_roster_rejects_role_model_order_drift(self) -> None:
        fields = self._fields()
        verifier_models = fields["verifier"]["model"].split(",")
        verifier_models[0], verifier_models[1] = (
            verifier_models[1],
            verifier_models[0],
        )
        fields["verifier"]["model"] = ",".join(verifier_models)
        with tempfile.TemporaryDirectory(prefix="dispatch-roster-") as directory:
            with self.assertRaises(SystemExit):
                check_roster_policy(
                    SimpleNamespace(
                        bundled_agents=frozenset(
                            {"task", "scout", "librarian", "designer", "sonic"}
                        )
                    ),
                    self._settings(Path(directory)),
                    {
                        skill
                        for values in EXPECTED_AGENT_SKILLS.values()
                        for skill in values
                    },
                    set(fields),
                    fields,
                )

    def test_model_policy_rejects_global_role_drift(self) -> None:
        source = (ROOT / "global" / "config.yml").read_text()
        mutations = {
            "non-deepseek OpenRouter primary": (
                f"  tiny: {EXACT_DEEPSEEK_ROUTE}",
                "  tiny: openrouter/z-ai/glm-5.2:high",
            ),
            "non-designer Kimi primary": (
                "  advisor: xai-oauth/grok-4.5:high",
                "  advisor: kimi-code/k3:high",
            ),
            "subscription order": (
                "      - openai-codex/gpt-5.6-sol:max\n"
                "      - openai-codex/gpt-5.6-luna:xhigh",
                "      - openai-codex/gpt-5.6-luna:xhigh\n"
                "      - openai-codex/gpt-5.6-sol:max",
            ),
            "OpenRouter reasoning effort": (
                "      - openrouter/x-ai/grok-4.5:high",
                "      - openrouter/x-ai/grok-4.5:low",
            ),
        }
        catalog = (
            ROOT
            / "global"
            / "skills"
            / "dispatch"
            / "references"
            / "agent-roster.json"
        )
        agents = sorted((ROOT / "global" / "agents").glob("*.md"))
        for label, (old, new) in mutations.items():
            with self.subTest(label=label):
                invalid = source.replace(old, new, 1)
                self.assertNotEqual(source, invalid)
                with tempfile.TemporaryDirectory(
                    prefix="dispatch-model-policy-"
                ) as directory:
                    settings = Path(directory) / "config.yml"
                    settings.write_text(invalid)
                    with self.assertRaises(SystemExit):
                        check_model_route_policy(settings, catalog, agents)

    def test_model_policy_rejects_sonnet_and_noncanonical_deepseek(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dispatch-model-policy-") as directory:
            root = Path(directory)
            settings = root / "config.yml"
            catalog = root / "catalog.json"
            agent = root / "builder.md"
            settings.write_text(f"modelRoles:\n  smol: {EXACT_DEEPSEEK_ROUTE}\n")
            agent.write_text("builder")

            catalog.write_text('{"model": "anthropic/claude-sonnet-5:xhigh"}')
            with self.assertRaises(SystemExit):
                check_model_route_policy(settings, catalog, [agent])

            catalog.write_text('{"model": "openrouter/deepseek/deepseek-v4-flash-0731:low"}')
            with self.assertRaises(SystemExit):
                check_model_route_policy(settings, catalog, [agent])


if __name__ == "__main__":
    unittest.main()
