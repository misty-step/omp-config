from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "global" / "hooks" / "claude-safety.py"

LIB = ROOT / "global" / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from claude_safety.bash_policy import destructive_command_reason, is_safe_bash
from claude_safety.redaction import redact, secret_path_mentioned
from claude_safety.skill_audit import build_skill_invocation_entry


def run_hook(name: str, payload: object, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        [sys.executable, str(HOOK), "claude-hook", name],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=merged,
        check=False,
    )


def hook_json(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return json.loads(result.stdout)


class ClaudeSafetyHookTests(unittest.TestCase):
    def test_public_policy_units_cover_bash_redaction_and_skill_audit(self) -> None:
        self.assertTrue(is_safe_bash("git status --short"))
        self.assertEqual(
            destructive_command_reason("git branch -D master", Path("/tmp")),
            "Force-deleting master is blocked. Protected branch.",
        )
        secret = "-".join(("sk", "or", "v1", "ABCDEF1234567890"))
        self.assertNotIn(secret, redact(f"token={secret}"))
        self.assertTrue(secret_path_mentioned("cat ~/.secrets", Path.home()))
        entry = build_skill_invocation_entry(
            {"tool_name": "Skill", "tool_input": {"skill": "oracle", "args": ""}, "cwd": "/tmp/project"}
        )
        self.assertIsNotNone(entry)
        self.assertEqual(entry["invocation_kind"], "unknown")

    def test_permission_allows_reads_and_safe_bash_but_not_mutation(self) -> None:
        read = run_hook("permission-auto-approve", {"tool_name": "Read", "tool_input": {"file_path": "README.md"}})
        self.assertEqual(hook_json(read)["hookSpecificOutput"]["permissionDecision"], "allow")
        safe_bash = run_hook("permission-auto-approve", {"tool_name": "Bash", "tool_input": {"command": "git status --short"}})
        self.assertEqual(hook_json(safe_bash)["hookSpecificOutput"]["permissionDecision"], "allow")
        mutation = run_hook("permission-auto-approve", {"tool_name": "Bash", "tool_input": {"command": "rm README.md"}})
        self.assertEqual(mutation.stdout, "")
        for command in ("git status; touch /tmp/changed", "cat /dev/null >target",
                        "git status\ntouch /tmp/changed", "git branch -D feature",
                        "git remote add origin https://example.invalid/repo",
                        "git tag -d release", "git log --output=/tmp/log"):
            with self.subTest(command=command):
                compound = run_hook("permission-auto-approve", {"tool_name": "Bash", "tool_input": {"command": command}})
                self.assertEqual(compound.stdout, "")

    def test_destructive_guard_denies_dangerous_commands_and_ignores_quoted_text(self) -> None:
        denied = run_hook("destructive-command-guard", {"tool_name": "Bash", "tool_input": {"command": "git reset --hard"}})
        denied_output = hook_json(denied)["hookSpecificOutput"]
        self.assertEqual(denied_output["permissionDecision"], "deny")
        self.assertIn("BLOCKED", denied_output["permissionDecisionReason"])
        quoted = run_hook("destructive-command-guard", {"tool_name": "Bash", "tool_input": {"command": 'git commit -m "rm all files"'}})
        self.assertEqual(quoted.stdout, "")

    def test_destructive_guard_catches_wrappers_and_forced_pushes(self) -> None:
        denied_commands = (
            "env rm README.md",
            "nice -n 5 /bin/rm README.md",
            "nohup command /bin/rm README.md",
            "git push --force origin HEAD",
            "git push -f origin HEAD",
            "git reset --hard HEAD",
            "find . -delete -print",
            "find . -name doomed -exec /bin/rm {} +",
            "env git push --force origin HEAD",
            "command git reset --hard HEAD",
        )
        for command in denied_commands:
            with self.subTest(command=command):
                result = run_hook("destructive-command-guard", {"tool_name": "Bash", "tool_input": {"command": command}})
                self.assertEqual(hook_json(result)["hookSpecificOutput"]["permissionDecision"], "deny")
        lease = run_hook("destructive-command-guard", {"tool_name": "Bash", "tool_input": {"command": "git push --force-with-lease origin HEAD"}})
        self.assertEqual(lease.stdout, "")
        reset_origin = run_hook("destructive-command-guard", {"tool_name": "Bash", "tool_input": {"command": "git reset --hard origin/master"}})
        self.assertEqual(hook_json(reset_origin)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_secret_guards_deny_bash_read_and_source(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            blocked = run_hook("secrets-read-guard", {"tool_name": "Bash", "tool_input": {"command": "grep KEY ~/.secrets --"}}, env={"HOME": home})
            self.assertEqual(hook_json(blocked)["hookSpecificOutput"]["permissionDecision"], "deny")
            absolute = run_hook("secrets-read-guard", {"tool_name": "Bash", "tool_input": {"command": f"cat {Path(home) / '.secrets'}"}}, env={"HOME": home})
            self.assertEqual(hook_json(absolute)["hookSpecificOutput"]["permissionDecision"], "deny")
            read = run_hook("secrets-read-tool-guard", {"tool_name": "Read", "tool_input": {"file_path": "~/.secrets"}}, env={"HOME": home})
            self.assertEqual(hook_json(read)["hookSpecificOutput"]["permissionDecision"], "deny")
            for command in ("source ~/.secrets && exec command", ". ~/.secrets", 'source "$HOME/.secrets"', '. "$HOME/./.secrets"'):
                with self.subTest(command=command):
                    source = run_hook("secrets-read-guard", {"tool_name": "Bash", "tool_input": {"command": command}}, env={"HOME": home})
                    self.assertEqual(hook_json(source)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_secret_guard_normalizes_home_forms_and_quoted_paths(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            home_var = "$" + "{HOME}"
            commands = (
                'cat "$HOME/.secrets"',
                'cat "$HOME/./.secrets"',
                'cat "' + home_var + '/.secrets"',
                f"python3 -c \\\"open('{Path(home) / '.secrets'}')\\\"",
                'source "' + home_var + '/./.secrets"',
                '. "' + str(Path(home) / '.secrets') + '"',
            )
            for command in commands:
                with self.subTest(command=command):
                    result = run_hook("secrets-read-guard", {"tool_name": "Bash", "tool_input": {"command": command}}, env={"HOME": home})
                    self.assertEqual(hook_json(result)["hookSpecificOutput"]["permissionDecision"], "deny")
            read = run_hook("secrets-read-tool-guard", {"tool_name": "Read", "tool_input": {"file_path": home_var + '/./.secrets'}}, env={"HOME": home})
            self.assertEqual(hook_json(read)["hookSpecificOutput"]["permissionDecision"], "deny")
    def test_redaction_stream_masks_named_shapes_and_preserves_prose(self) -> None:
        key = "-".join(("sk", "or", "v1", "ABCDEF1234567890"))
        slack = "-".join(("xoxb", "1234567890", "abcdefghijklmnop"))
        jwt = ".".join(("eyJhbGciOiJIUzI1NiJ9", "eyJzdWIiOiIxMjM0NTY3ODkwIn0", "SflKxw5"))
        payload = f"key={key} slack={slack} jwt={jwt} plain=pre-existing"
        result = subprocess.run([sys.executable, str(HOOK), "redact-stream"], input=payload, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertNotIn(key, result.stdout)
        self.assertNotIn(slack, result.stdout)
        self.assertNotIn(jwt, result.stdout)
        self.assertIn("plain=pre-existing", result.stdout)

    def test_redaction_rewrite_wraps_safe_bash_and_skips_guards(self) -> None:
        result = run_hook("secrets-redaction-rewrite", {"tool_name": "Bash", "tool_input": {"command": "printf 'hello\\n'"}})
        rewritten = hook_json(result)["hookSpecificOutput"]["modifiedToolInput"]["command"]
        self.assertIn("claude-safety.py", rewritten)
        self.assertIn("redact-stream", rewritten)
        self.assertIn("__omp_rc=$?", rewritten)
        blocked = run_hook("secrets-redaction-rewrite", {"tool_name": "Bash", "tool_input": {"command": "cat ~/.secrets"}})
        self.assertEqual(blocked.stdout, "")

    def test_skill_tracker_appends_context_and_time_context_continues(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            log = Path(temp) / "skill-invocations.jsonl"
            result = run_hook("skill-invocation-tracker", {"tool_name": "Skill", "tool_input": {"skill": "harness-engineering", "args": ""}, "session_id": "session", "cwd": "/tmp/project"}, env={"SKILL_TRACKER_LOG_PATH": str(log)})
            self.assertEqual(result.returncode, 0)
            entry = json.loads(log.read_text())
            self.assertEqual(entry["skill"], "harness-engineering")
            self.assertEqual(entry["project"], "project")
            self.assertEqual(entry["invocation_kind"], "unknown")
        time = run_hook("time-context", {})
        self.assertEqual(hook_json(time)["result"], "continue")
        self.assertIn("Current time:", hook_json(time)["message"])

    # "testing_" stays discoverable without matching TruffleHog's Lob test-key detector.
    def testing_unknown_hook_fails_with_no_decision(self) -> None:
        result = subprocess.run([sys.executable, str(HOOK), "claude-hook", "unknown"], input="{}", text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
