from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
sys.path.insert(0, str(BIN))
import omp_recipe


class OmpRecipeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="omp-recipe-test-")
        self.root = Path(self.tmp.name)
        (self.root / "instructions.md").write_text("first instructions\n")
        skill = self.root / "source-skills" / "demo"
        (skill / "references").mkdir(parents=True)
        (skill / "scripts").mkdir()
        (skill / "SKILL.md").write_text("demo skill\n")
        (skill / "references" / "detail.md").write_text("nested detail\n")
        (skill / "scripts" / "run").write_text("#!/bin/sh\n")
        self.spec = self.root / "recipe-source.json"
        self.output = self.root / "compiled"
        self.write_recipe()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def recipe(self) -> dict:
        return {
            "schemaVersion": omp_recipe.SCHEMA,
            "instructions": "instructions.md",
            "models": [
                {"provider": "anthropic", "model": "claude-primary", "reasoning": "high"},
                {"provider": "openrouter", "model": "fallback", "reasoning": "medium"},
            ],
            "skills": [{"name": "demo", "path": "source-skills/demo"}],
            "mcpServers": [],
        }

    def write_recipe(self, recipe: dict | None = None) -> None:
        self.spec.write_text(json.dumps(recipe or self.recipe()))

    def compile(self) -> dict:
        return omp_recipe.compile_recipe(self.spec, self.output)

    def test_schema_is_exact_and_accepts_non_openrouter_provider(self) -> None:
        recipe = self.recipe()
        self.assertEqual(omp_recipe.validate_recipe(recipe), recipe)
        for legacy in (
            {**recipe, "agent": {"name": "legacy"}},
            {**recipe, "agentsMd": "AGENTS.md"},
        ):
            with self.assertRaises(omp_recipe.RecipeError):
                omp_recipe.validate_recipe(legacy)

    def test_compile_packages_complete_skill_directory(self) -> None:
        self.compile()
        skill = self.output / "skills" / "demo"
        self.assertEqual((skill / "SKILL.md").read_text(), "demo skill\n")
        self.assertEqual(
            (skill / "references" / "detail.md").read_text(), "nested detail\n"
        )
        self.assertEqual((skill / "scripts" / "run").read_text(), "#!/bin/sh\n")
        self.assertEqual(
            json.loads((self.output / omp_recipe.RECIPE_FILE).read_text()),
            self.recipe(),
        )

    def test_nested_skill_symlink_is_rejected_before_output_mutation(self) -> None:
        self.compile()
        previous_recipe = (self.output / omp_recipe.RECIPE_FILE).read_bytes()
        previous_instructions = (self.output / omp_recipe.INSTRUCTIONS_FILE).read_bytes()
        external = self.root / "outside"
        external.write_text("outside\n")
        (self.root / "source-skills" / "demo" / "references" / "link").symlink_to(
            external
        )

        with self.assertRaises(omp_recipe.RecipeError):
            self.compile()

        self.assertEqual(
            (self.output / omp_recipe.RECIPE_FILE).read_bytes(), previous_recipe
        )
        self.assertEqual(
            (self.output / omp_recipe.INSTRUCTIONS_FILE).read_bytes(),
            previous_instructions,
        )

    def test_failed_recompile_preserves_previous_owned_output(self) -> None:
        self.compile()
        previous_recipe = (self.output / omp_recipe.RECIPE_FILE).read_bytes()
        previous_instructions = (self.output / omp_recipe.INSTRUCTIONS_FILE).read_bytes()
        changed = self.recipe()
        changed["instructions"] = "missing.md"
        self.write_recipe(changed)

        with self.assertRaises(omp_recipe.RecipeError):
            self.compile()

        self.assertEqual(
            (self.output / omp_recipe.RECIPE_FILE).read_bytes(), previous_recipe
        )
        self.assertEqual(
            (self.output / omp_recipe.INSTRUCTIONS_FILE).read_bytes(),
            previous_instructions,
        )

    def test_successful_recompile_preserves_only_owned_runtime_state(self) -> None:
        self.compile()
        agent = self.output / "runtime" / "agent"
        sessions = agent / "sessions"
        sessions.mkdir(parents=True)
        (sessions / "history.jsonl").write_text("history\n")
        (agent / "mcp.json").write_text("{}")
        (agent / "RULES.md").write_text("stale\n")
        (self.root / "instructions.md").write_text("second instructions\n")

        self.compile()

        self.assertEqual(
            (self.output / omp_recipe.INSTRUCTIONS_FILE).read_text(),
            "second instructions\n",
        )
        self.assertEqual(
            (self.output / "runtime" / "agent" / "sessions" / "history.jsonl").read_text(),
            "history\n",
        )
        self.assertFalse((self.output / "runtime" / "agent" / "mcp.json").exists())
        self.assertFalse((self.output / "runtime" / "agent" / "RULES.md").exists())

    def test_compile_refuses_unrelated_directory(self) -> None:
        self.output.mkdir()
        sentinel = self.output / "sentinel"
        sentinel.write_text("preserve\n")

        with self.assertRaises(omp_recipe.RecipeError):
            self.compile()

        self.assertEqual(sentinel.read_text(), "preserve\n")
        self.assertEqual(list(self.output.iterdir()), [sentinel])

    def test_compile_refuses_marker_only_unverified_directory(self) -> None:
        self.output.mkdir()
        (self.output / omp_recipe.OWNER_FILE).write_text(f"{omp_recipe.SCHEMA}\n")
        sentinel = self.output / "sentinel"
        sentinel.write_text("preserve\n")

        with self.assertRaises(omp_recipe.RecipeError):
            self.compile()

        self.assertEqual(sentinel.read_text(), "preserve\n")

    def test_prepare_runtime_rebuilds_discovery_and_uses_caller_cwd(self) -> None:
        self.compile()
        workspace = self.root / "caller-workspace"
        workspace.mkdir()
        workspace_sentinel = workspace / "caller-file"
        workspace_sentinel.write_text("preserve\n")
        first = omp_recipe.prepare_runtime(self.output, workspace, environ={"PATH": "/bin"})
        (first.agent_dir / "sessions").mkdir()
        (first.agent_dir / "sessions" / "history.jsonl").write_text("history\n")
        (first.agent_dir / "mcp.json").write_text("{}")
        (first.agent_dir / "RULES.md").write_text("stale\n")
        (first.agent_dir / "extensions").mkdir()
        (first.agent_dir / "extensions" / "stale.py").write_text("bad\n")

        prepared = omp_recipe.prepare_runtime(
            self.output, workspace, environ={"PATH": "/bin"}
        )

        self.assertEqual(prepared.cwd, workspace.resolve())
        self.assertEqual(workspace_sentinel.read_text(), "preserve\n")
        self.assertEqual(
            (prepared.agent_dir / "sessions" / "history.jsonl").read_text(),
            "history\n",
        )
        self.assertFalse((prepared.agent_dir / "mcp.json").exists())
        self.assertFalse((prepared.agent_dir / "RULES.md").exists())
        self.assertFalse((prepared.agent_dir / "extensions").exists())
        self.assertTrue((prepared.agent_dir / "skills" / "demo" / "scripts" / "run").is_file())
        self.assertIn('default: "anthropic/claude-primary:high"', (prepared.agent_dir / "config.yml").read_text())
        config = (prepared.agent_dir / "config.yml").read_text()
        self.assertIn(str(prepared.agent_dir / "skills"), config)
        custom_only = self.recipe()
        custom_only["models"] = [
            {"provider": "anthropic", "model": "claude-primary", "reasoning": "high"}
        ]
        self.assertEqual(omp_recipe.render_models(custom_only), "providers: {}\n")

    def test_fresh_runtime_root_is_caller_owned_and_environment_is_allowlisted(self) -> None:
        self.compile()
        workspace = self.root / "fresh-workspace"
        workspace.mkdir()
        first_root = self.root / "launch-one"
        second_root = self.root / "launch-two"

        first = omp_recipe.prepare_runtime(
            self.output,
            workspace,
            environ={"PATH": "/bin", "PARENT_ONLY": "must-not-cross"},
            runtime_root=first_root,
        )
        second = omp_recipe.prepare_runtime(
            self.output,
            workspace,
            environ={"PATH": "/bin", "PARENT_ONLY": "must-not-cross"},
            runtime_root=second_root,
        )

        self.assertEqual(first.root, first_root.resolve())
        self.assertEqual(second.root, second_root.resolve())
        self.assertNotEqual(first.agent_dir, second.agent_dir)
        self.assertNotIn("PARENT_ONLY", first.env)
        self.assertFalse((self.output / "runtime" / "agent").exists())
        descriptor = omp_recipe.launch_descriptor(self.output, first)
        self.assertEqual(descriptor["schemaVersion"], omp_recipe.LAUNCH_SCHEMA)
        self.assertEqual(descriptor["runtimeRoot"], str(first_root.resolve()))
        self.assertEqual(descriptor["cwd"], str(workspace.resolve()))
        self.assertEqual(descriptor["env"], first.env)
        self.assertTrue(Path(descriptor["sessionDir"]).is_dir())

    def test_fresh_runtime_refuses_preexisting_root_without_mutation(self) -> None:
        self.compile()
        workspace = self.root / "fresh-workspace"
        workspace.mkdir()
        runtime_root = self.root / "claimed-runtime"
        runtime_root.mkdir()
        sentinel = runtime_root / "sentinel"
        sentinel.write_text("preserve\n")

        with self.assertRaises(omp_recipe.RecipeError):
            omp_recipe.prepare_runtime(
                self.output,
                workspace,
                runtime_root=runtime_root,
            )

        self.assertEqual(sentinel.read_text(), "preserve\n")

    def test_machine_prepare_command_emits_only_launch_json(self) -> None:
        self.compile()
        workspace = self.root / "command-workspace"
        workspace.mkdir()
        runtime_root = self.root / "command-runtime"
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = omp_recipe.main(
                [
                    "prepare-runtime",
                    "--bundle",
                    str(self.output),
                    "--cwd",
                    str(workspace),
                    "--runtime-root",
                    str(runtime_root),
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(stderr.getvalue(), "")
        descriptor = json.loads(stdout.getvalue())
        self.assertEqual(descriptor["schemaVersion"], omp_recipe.LAUNCH_SCHEMA)
        self.assertEqual(descriptor["runtimeRoot"], str(runtime_root.resolve()))
        self.assertEqual(descriptor["cwd"], str(workspace.resolve()))


if __name__ == "__main__":
    unittest.main()
