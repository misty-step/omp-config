from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))

from config_contract import ContractError  # noqa: E402
from launch_compile import compile_bundle  # noqa: E402
from launch_run import run_bundle  # noqa: E402
from launch_verify import verify_bundle  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "launch-contract"


class LaunchContractTests(unittest.TestCase):
    def test_compilation_is_deterministic_and_verifiable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first"
            second = Path(temp) / "second"
            first_manifest = compile_bundle(ROOT, FIXTURE / "contract.json", first)
            second_manifest = compile_bundle(ROOT, FIXTURE / "contract.json", second)
            self.assertEqual(first_manifest["digest"], second_manifest["digest"])
            self.assertEqual(first_manifest["files"], second_manifest["files"])
            self.assertEqual(verify_bundle(first)["digest"], first_manifest["digest"])
            self.assertTrue((first / "agent" / "agents" / "conductor.md").is_file())
            self.assertTrue((first / "agent" / "agents" / "pico.md").is_file())
            self.assertEqual(json.loads((first / "agent" / "mcp.json").read_text())["mcpServers"], {})
            config = (first / "agent" / "config.yml").read_text()
            self.assertIn('disabledAgents: ["conductor","designer","librarian","scout","sonic","task"]', config)
            prompt = (first / "system-prompt.txt").read_text()
            sticky_rules = (ROOT / "global" / "RULES.md").read_text().strip()
            self.assertIn(f"<sticky-rules>\n{sticky_rules}\n</sticky-rules>", prompt)
            self.assertNotIn("discoveryMode", config)
            self.assertNotIn("\ntools:", config)
            self.assertEqual(first_manifest["repository"]["file_count"], 4)
            self.assertTrue(first_manifest["repository"]["digest"].startswith("sha256:"))

    def test_unsupported_sandbox_fails_before_output(self) -> None:
        contract = json.loads((FIXTURE / "contract.json").read_text())
        contract["sandbox"]["filesystem"] = "workspace"
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            contract["repository"]["root"] = str(FIXTURE / "repository")
            contract_path = temp_root / "contract.json"
            contract_path.write_text(json.dumps(contract))
            output = temp_root / "bundle"
            with self.assertRaisesRegex(ContractError, "not enforceable"):
                compile_bundle(ROOT, contract_path, output)
            self.assertFalse(output.exists())

    # "testing_" stays discoverable without matching TruffleHog's Lob test-key detector.
    def testing_duplicate_skill_source_fails_closed(self) -> None:
        contract = json.loads((FIXTURE / "contract.json").read_text())
        contract["composition"]["skills"] = ["research"]
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            repository = temp_root / "repository"
            shutil.copytree(FIXTURE / "repository", repository)
            duplicate = repository / ".omp" / "skills" / "research"
            duplicate.mkdir(parents=True)
            duplicate.joinpath("SKILL.md").write_text(
                "---\nname: research\ndescription: duplicate proof skill\n---\nDuplicate.\n"
            )
            contract["repository"]["root"] = str(repository)
            contract_path = temp_root / "contract.json"
            contract_path.write_text(json.dumps(contract))
            with self.assertRaisesRegex(ContractError, "duplicate sources for skill 'research'"):
                compile_bundle(ROOT, contract_path, temp_root / "bundle")

    def test_repository_drift_is_rejected_before_launch(self) -> None:
        contract = json.loads((FIXTURE / "contract.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            repository = temp_root / "repository"
            shutil.copytree(FIXTURE / "repository", repository)
            contract["repository"]["root"] = str(repository)
            contract_path = temp_root / "contract.json"
            contract_path.write_text(json.dumps(contract))
            bundle = temp_root / "bundle"
            compile_bundle(ROOT, contract_path, bundle)
            repository.joinpath("marker.txt").write_text("drift\n")
            with self.assertRaisesRegex(ContractError, "compiled repository drift"):
                run_bundle(bundle, "unreachable")

    def test_unselected_project_agent_is_rejected(self) -> None:
        contract = json.loads((FIXTURE / "contract.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            repository = temp_root / "repository"
            shutil.copytree(FIXTURE / "repository", repository)
            repository.joinpath(".omp", "agents", "rogue.md").write_text(
                "---\nname: rogue\ndescription: must not remain ambient\nmodel: openai-codex/gpt-5.6-luna\n"
                "thinkingLevel: low\ntools: read\nautoloadSkills: ''\nspawns: ''\n---\nNo.\n"
            )
            contract["repository"]["root"] = str(repository)
            contract_path = temp_root / "contract.json"
            contract_path.write_text(json.dumps(contract))
            with self.assertRaisesRegex(ContractError, "undeclared project agents"):
                compile_bundle(ROOT, contract_path, temp_root / "bundle")

    def test_gitignored_project_agent_added_after_compile_is_rejected(self) -> None:
        contract = json.loads((FIXTURE / "contract.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            repository = temp_root / "repository"
            shutil.copytree(FIXTURE / "repository", repository)
            repository.joinpath(".gitignore").write_text(".omp/agents/rogue.md\n")
            subprocess.run(["git", "init", "--quiet", str(repository)], check=True)
            subprocess.run(["git", "-C", str(repository), "add", "."], check=True)
            contract["repository"]["root"] = str(repository)
            contract_path = temp_root / "contract.json"
            contract_path.write_text(json.dumps(contract))
            bundle = temp_root / "bundle"
            compile_bundle(ROOT, contract_path, bundle)
            repository.joinpath(".omp", "agents", "rogue.md").write_text(
                "---\nname: rogue\ndescription: ignored ambient agent\nmodel: openai-codex/gpt-5.6-luna\n"
                "thinkingLevel: low\ntools: read\nautoloadSkills: ''\nspawns: ''\n---\nNo.\n"
            )
            with self.assertRaisesRegex(ContractError, "undeclared project agents"):
                run_bundle(bundle, "unreachable")

    def test_ancestor_project_agent_is_rejected(self) -> None:
        contract = json.loads((FIXTURE / "contract.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            repository = temp_root / "nested" / "repository"
            shutil.copytree(FIXTURE / "repository", repository)
            shutil.rmtree(repository / ".omp" / "agents")
            contract["repository"]["root"] = str(repository)
            contract["composition"].update(
                {
                    "agent": "daedalus",
                    "model": "openai-codex/gpt-5.6-sol",
                    "thinking": "high",
                    "tools": ["read", "grep", "glob", "lsp", "web_search"],
                    "skills": ["project-engineering"],
                    "subagents": {"allowed": [], "tools": [], "isolation": "inherit", "max_concurrency": 1},
                }
            )
            ancestor_agents = temp_root / ".omp" / "agents"
            ancestor_agents.mkdir(parents=True)
            ancestor_agents.joinpath("rogue.md").write_text("---\nname: rogue\n---\nNo.\n")
            contract_path = temp_root / "contract.json"
            contract_path.write_text(json.dumps(contract))
            with self.assertRaisesRegex(ContractError, "ancestor project agents"):
                compile_bundle(ROOT, contract_path, temp_root / "bundle")

    def test_ancestor_project_agent_added_after_compile_is_rejected(self) -> None:
        contract = json.loads((FIXTURE / "contract.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            repository = temp_root / "nested" / "repository"
            shutil.copytree(FIXTURE / "repository", repository)
            shutil.rmtree(repository / ".omp" / "agents")
            contract["repository"]["root"] = str(repository)
            contract["composition"].update(
                {
                    "agent": "daedalus",
                    "model": "openai-codex/gpt-5.6-sol",
                    "thinking": "high",
                    "tools": ["read", "grep", "glob", "lsp", "web_search"],
                    "skills": ["project-engineering"],
                    "subagents": {"allowed": [], "tools": [], "isolation": "inherit", "max_concurrency": 1},
                }
            )
            contract_path = temp_root / "contract.json"
            contract_path.write_text(json.dumps(contract))
            bundle = temp_root / "bundle"
            compile_bundle(ROOT, contract_path, bundle)
            ancestor_agents = temp_root / ".omp" / "agents"
            ancestor_agents.mkdir(parents=True)
            ancestor_agents.joinpath("rogue.md").write_text("---\nname: rogue\n---\nNo.\n")
            with self.assertRaisesRegex(ContractError, "ancestor project agents"):
                run_bundle(bundle, "unreachable")

    def test_subagent_tools_must_cover_agent_declaration(self) -> None:
        contract = json.loads((FIXTURE / "contract.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            repository = temp_root / "repository"
            shutil.copytree(FIXTURE / "repository", repository)
            child = repository / ".omp" / "agents" / "pico.md"
            child.write_text(child.read_text().replace("tools: read", "tools: read, bash"))
            contract["repository"]["root"] = str(repository)
            contract_path = temp_root / "contract.json"
            contract_path.write_text(json.dumps(contract))
            with self.assertRaisesRegex(ContractError, "omits tools declared by pico"):
                compile_bundle(ROOT, contract_path, temp_root / "bundle")

    # "testing_" stays discoverable without matching TruffleHog's Lob test-key detector.
    def testing_allowed_subagent_requires_task_tool(self) -> None:
        contract = json.loads((FIXTURE / "contract.json").read_text())
        contract["composition"]["tools"] = ["read"]
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            contract["repository"]["root"] = str(FIXTURE / "repository")
            contract_path = temp_root / "contract.json"
            contract_path.write_text(json.dumps(contract))
            with self.assertRaisesRegex(ContractError, "must include task"):
                compile_bundle(ROOT, contract_path, temp_root / "bundle")

    def test_manifest_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp) / "bundle"
            compile_bundle(ROOT, FIXTURE / "contract.json", bundle)
            (bundle / "system-prompt.txt").write_text("drift\n")
            with self.assertRaisesRegex(ContractError, "file drift"):
                verify_bundle(bundle)


if __name__ == "__main__":
    unittest.main()
