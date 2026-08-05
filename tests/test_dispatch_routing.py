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
        self.assertEqual(persona["chain"], ["chief", "qa-user", "qa-user-leaf"])
        coordinator = self.fields["qa-user"]
        leaf = self.fields["qa-user-leaf"]
        self.assertEqual(coordinator["tools"], "task")
        self.assertEqual(coordinator["spawns"], "qa-user-leaf")
        self.assertEqual(leaf["tools"], "browser")
        self.assertEqual(leaf.get("spawns", ""), "")
        self.assertNotIn("qa-user", self.fields["verifier"].get("spawns", ""))

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
            "openrouter/openai/gpt-5.6-luna:xhigh",
        )
        self.assertNotIn("edit", self.fields["architect"]["tools"])
        self.assertEqual(self.fields["architect"].get("spawns", ""), "")

    def test_role_model_order_and_workhorse_heads(self) -> None:
        ladders = {
            name: [part.strip() for part in fields["model"].split(",")]
            for name, fields in self.fields.items()
            if "," in fields["model"]
        }
        luna = "openrouter/openai/gpt-5.6-luna"
        deepseek = "openrouter/deepseek/deepseek-v4-flash-0731"
        deepseek_first = {"researcher", "qa-user", "qa-user-leaf"}
        self.assertEqual(
            [name for name, models in ladders.items() if models[0].startswith("kimi-code/k3")],
            ["designer"],
        )
        for name, models in ladders.items():
            head = models[1:3] if name == "designer" else models[:2]
            expected = [deepseek, luna] if name in deepseek_first else [luna, deepseek]
            self.assertEqual([model.rsplit(":", 1)[0] for model in head], expected, name)
            self.assertEqual(
                [model.rsplit(":", 1)[0] for model in models[-2:]],
                ["openrouter/x-ai/grok-4.5", "openrouter/z-ai/glm-5.2"],
                name,
            )

    def test_every_scenario_names_a_catalog_agent(self) -> None:
        for scenario in self.fixture["scenarios"]:
            self.assertIn(scenario["route"], self.catalog)


if __name__ == "__main__":
    unittest.main()
