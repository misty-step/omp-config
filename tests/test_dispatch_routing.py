from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = ROOT / "bin"
if str(BIN_DIR) not in sys.path:
    sys.path.insert(0, str(BIN_DIR))

from config_contract import frontmatter  # noqa: E402


class DispatchRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads((ROOT / "tests/fixtures/dispatch-routing.json").read_text())
        cls.agent_dir = ROOT / "global/agents"
        cls.catalog = json.loads(
            (ROOT / "global/skills/dispatch/references/agent-roster.json").read_text()
        )["agents"]
        cls.fields = {
            path.stem: frontmatter(path)[0]
            for path in cls.agent_dir.glob("*.md")
        }

    def test_fixture_has_the_nine_routing_scenarios(self) -> None:
        scenarios = self.fixture["scenarios"]
        self.assertEqual(len(scenarios), 9)
        self.assertEqual(len({scenario["id"] for scenario in scenarios}), 9)
        self.assertEqual(
            {scenario["id"] for scenario in scenarios},
            {
                "accepted-implementation",
                "security-review",
                "live-qa",
                "incident-reproduction",
                "broad-research",
                "external-api-research",
                "ui-design",
                "persona-qa",
                "xl-architecture",
            },
        )

    def test_direct_chief_persona_route_uses_only_structural_qa_declarations(self) -> None:
        persona = next(item for item in self.fixture["scenarios"] if item["id"] == "persona-qa")
        self.assertEqual(persona["chain"], ["chief", "qa-master", "qa-persona"])
        coordinator = self.fields["qa-master"]
        leaf = self.fields["qa-persona"]
        self.assertIn("task", {part.strip() for part in coordinator.get("tools", "").split(",") if part.strip()})
        self.assertEqual(coordinator["spawns"], "qa-persona")
        self.assertEqual(leaf.get("tools", ""), "browser")
        self.assertNotIn("qa-master", self.fields["verifier"].get("spawns", ""))

    def test_direct_chief_persona_and_native_agent_routes_are_distinct(self) -> None:
        scenarios = {scenario["id"]: scenario for scenario in self.fixture["scenarios"]}
        self.assertEqual(scenarios["persona-qa"]["dispatch"], "direct-chief")
        for scenario_id in (
            "accepted-implementation",
            "security-review",
            "live-qa",
            "incident-reproduction",
            "broad-research",
            "external-api-research",
            "ui-design",
            "xl-architecture",
        ):
            self.assertEqual(scenarios[scenario_id]["dispatch"], "native-agent")

    def test_native_routes_use_the_declared_tool_and_skill_envelope(self) -> None:
        for scenario in self.fixture["scenarios"]:
            if scenario["id"] == "persona-qa":
                continue
            role = scenario["route"]
            self.assertIn(role, {"architect", "builder", "verifier", "researcher", "designer"})
            fields = self.fields[role]
            tools = {part.strip() for part in fields["tools"].split(",")}
            skills = {part.strip() for part in fields.get("autoloadSkills", "").split(",") if part.strip()}
            self.assertTrue(set(scenario.get("requiredTools", [])).issubset(tools), scenario["id"])
            self.assertTrue(set(scenario.get("requiredSkills", [])).issubset(skills), scenario["id"])
            self.assertEqual(fields.get("spawns", ""), "")
            for forbidden in scenario.get("forbidden", []):
                self.assertNotIn(forbidden, tools | skills | {role}, scenario["id"])

    def test_architect_is_a_broad_native_read_only_agent(self) -> None:
        scenario = next(item for item in self.fixture["scenarios"] if item["id"] == "xl-architecture")
        self.assertEqual(scenario["route"], "architect")
        self.assertIn("architect", self.fields)
        self.assertIn("architect", self.catalog)
        self.assertEqual(
            self.fields["architect"]["model"].split(",")[0],
            "openai-codex/gpt-5.6-sol:max",
        )
        self.assertNotIn("edit", self.fields["architect"]["tools"])
        self.assertEqual(self.fields["architect"].get("spawns", ""), "")

    def test_role_model_order_and_openrouter_policy(self) -> None:
        ladders = {
            name: [part.strip() for part in fields["model"].split(",")]
            for name, fields in self.fields.items()
            if "," in fields["model"]
        }
        deepseek = "openrouter/deepseek/deepseek-v4-flash-0731:high"
        deep_reasoning = {"architect", "builder", "verifier", "sculptor"}
        high_volume = {"researcher", "qa-master", "qa-persona"}

        self.assertEqual(ladders["architect"][0], "openai-codex/gpt-5.6-sol:max")
        self.assertEqual(ladders["designer"][0], "kimi-code/k3:max")
        for name, models in ladders.items():
            self.assertTrue(
                all(not model.startswith("openrouter/") or model == deepseek for model in models),
                name,
            )
            if name in deep_reasoning:
                self.assertEqual(models[-1], deepseek, name)
            if name in high_volume:
                self.assertEqual(models[0], deepseek, name)

    def test_every_scenario_names_a_catalog_agent(self) -> None:
        for scenario in self.fixture["scenarios"]:
            self.assertIn(scenario["route"], self.catalog)


if __name__ == "__main__":
    unittest.main()
