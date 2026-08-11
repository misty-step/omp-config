from __future__ import annotations

import io
import json
import stat
import sqlite3
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import usage_ledger


class UsageLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="usage-ledger-test-")
        root = Path(self.tmp.name)
        self.sessions = root / "sessions"
        self.sessions.mkdir()
        self.db = root / "usage-ledger.sqlite3"
        workspace = root / "workspace" / "repo"
        self.parent = self.sessions / "workspace" / "session-1.jsonl"
        self.parent.parent.mkdir(parents=True)
        self.child = self.parent.with_suffix("") / "VerifierLane.jsonl"
        self.child.parent.mkdir()
        self.child.write_text(
            self._record(
                "2026-08-06T01:00:00Z",
                "lane-response",
                provider="openrouter",
                model="deepseek",
                input_tokens=120,
                output_tokens=80,
                cache_read=50,
                cost=2.5,
            )
            + "\n"
            + self._record(
                "2026-08-06T01:01:00Z",
                "parent-response",
                provider="openrouter",
                model="deepseek",
                input_tokens=120,
                output_tokens=80,
                cache_read=50,
                cost=2.5,
            )
            + "\n"
            + '{"type":"message","message":{"role":"assistant","usage":\n'
        )
        self.parent.write_text(
            json.dumps(
                {
                    "type": "session",
                    "id": "session-1",
                    "cwd": str(workspace),
                    "timestamp": "2026-08-05T00:00:00Z",
                }
            )
            + "\n"
            + json.dumps(
                {
                    "type": "message",
                    "message": {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "toolCall",
                                "name": "task",
                                "arguments": {
                                    "tasks": [
                                        {"name": "VerifierLane", "agent": "verifier"}
                                    ]
                                },
                            }
                        ],
                    },
                }
            )
            + "\n"
            + self._record(
                "2026-08-05T12:00:00Z",
                "parent-response",
                provider="openai",
                model="subscription-model",
                input_tokens=60,
                output_tokens=40,
                cache_read=20,
                cost=1.25,
            )
            + "\n"
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_nested_dispatch_attributes_a_deep_lane(self) -> None:
        leaf = self.child.with_suffix("") / f"{self.child.stem}.PersonaLeaf.jsonl"
        leaf.parent.mkdir()
        leaf.write_text(
            self._record(
                "2026-08-06T03:00:00Z",
                "leaf-response",
                provider="openrouter",
                model="deepseek",
                input_tokens=8,
                output_tokens=4,
                cache_read=2,
                cost=0.25,
            )
            + "\n"
        )
        dispatch = json.dumps(
            {
                "type": "message",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "toolCall",
                            "name": "task",
                            "arguments": {"tasks": [{"name": "PersonaLeaf", "agent": "qa-persona"}]},
                        }
                    ],
                },
            }
        )
        self.child.write_text(self.child.read_text() + dispatch + "\n")
        self.invoke("ingest", "--sessions-root", str(self.sessions), "--db", str(self.db))
        rows = {row["dimension"]: row for row in self.report("--by", "agent")["rows"]}
        self.assertEqual(rows["qa-persona"]["requests"], 1)
        sessions = {row["dimension"] for row in self.report("--by", "session")["rows"]}
        self.assertNotIn("unknown", sessions)

    def test_nested_dispatch_attributes_a_sibling_lane(self) -> None:
        persona = self.child.parent / "PersonaLane.jsonl"
        persona.write_text(
            self._record(
                "2026-08-06T02:00:00Z",
                "persona-response",
                provider="openrouter",
                model="deepseek",
                input_tokens=10,
                output_tokens=5,
                cache_read=1,
                cost=0.5,
            )
            + "\n"
        )
        dispatch = json.dumps(
            {
                "type": "message",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "toolCall",
                            "name": "task",
                            "arguments": {"tasks": [{"name": "PersonaLane", "agent": "qa-persona"}]},
                        }
                    ],
                },
            }
        )
        self.child.write_text(dispatch + "\n" + self.child.read_text())
        self.invoke("ingest", "--sessions-root", str(self.sessions), "--db", str(self.db))
        rows = {row["dimension"]: row for row in self.report("--by", "agent")["rows"]}
        self.assertIn("qa-persona", rows)
        self.assertEqual(rows["qa-persona"]["requests"], 1)

    @staticmethod
    def _record(
        timestamp: str,
        response_id: str,
        *,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cache_read: int,
        cost: float,
    ) -> str:
        return json.dumps(
            {
                "type": "message",
                "timestamp": timestamp,
                "message": {
                    "role": "assistant",
                    "provider": provider,
                    "model": model,
                    "responseId": response_id,
                    "usage": {
                        "input": input_tokens,
                        "output": output_tokens,
                        "cacheRead": cache_read,
                        "cacheWrite": 4,
                        "totalTokens": input_tokens + output_tokens,
                        "reasoningTokens": 10,
                        "cost": {
                            "input": cost / 2,
                            "output": cost / 4,
                            "cacheRead": cost / 8,
                            "cacheWrite": cost / 8,
                            "total": cost,
                        },
                    },
                    "duration": 1.5,
                    "ttft": 0.25,
                },
            }
        )

    def invoke(self, *arguments: str) -> str:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = usage_ledger.main(list(arguments))
        self.assertEqual(status, 0, stderr.getvalue())
        return stdout.getvalue()

    def report(self, *arguments: str) -> dict:
        output = self.invoke("report", "--db", str(self.db), "--json", *arguments)
        return json.loads(output)

    def test_ingest_is_idempotent(self) -> None:
        first = self.invoke(
            "ingest",
            "--sessions-root",
            str(self.sessions),
            "--db",
            str(self.db),
        )
        self.assertIn("scanned files: 2", first)
        self.assertIn("inserted rows: 2", first)
        self.assertIn("skipped rows: 2", first)
        second = self.invoke(
            "ingest",
            "--sessions-root",
            str(self.sessions),
            "--db",
            str(self.db),
        )
        self.assertIn("inserted rows: 0", second)
        self.assertEqual(self.report("--by", "agent")["totals"]["requests"], 2)
        with sqlite3.connect(self.db) as connection:
            columns = {row[1] for row in connection.execute("PRAGMA table_info(responses)")}
        self.assertNotIn("content", columns)
        self.assertNotIn("arguments", columns)
        self.assertNotIn("title", columns)
        self.assertEqual(stat.S_IMODE(self.db.parent.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(self.db.stat().st_mode), 0o600)

    def test_agent_attribution_and_aggregation(self) -> None:
        self.invoke(
            "ingest",
            "--sessions-root",
            str(self.sessions),
            "--db",
            str(self.db),
        )
        rows = {row["dimension"]: row for row in self.report("--by", "agent")["rows"]}
        self.assertEqual(rows["verifier"]["requests"], 1)
        self.assertEqual(rows["verifier"]["total_tokens"], 200)
        self.assertEqual(rows["verifier"]["cached_tokens"], 50)
        self.assertEqual(rows["chief"]["requests"], 1)
        self.assertNotIn("unknown", rows)
        self.assertEqual(self.report("--by", "provider")["totals"]["total_cost"], 3.75)

    def test_report_filters(self) -> None:
        self.invoke(
            "ingest",
            "--sessions-root",
            str(self.sessions),
            "--db",
            str(self.db),
        )
        self.assertEqual(
            self.report("--by", "model", "--provider", "openrouter")["totals"]["requests"],
            1,
        )
        self.assertEqual(
            self.report("--by", "day", "--since", "2026-08-06")["totals"]["requests"],
            1,
        )
        self.assertEqual(
            self.report("--by", "day", "--until", "2026-08-05")["totals"]["requests"],
            1,
        )

    def test_incremental_ingest_resumes_at_byte_offset(self) -> None:
        self.invoke(
            "ingest",
            "--sessions-root",
            str(self.sessions),
            "--db",
            str(self.db),
        )
        partial = self._record(
            "2026-08-09T01:00:00Z",
            "partial-response",
            provider="openrouter",
            model="deepseek",
            input_tokens=40,
            output_tokens=20,
            cache_read=10,
            cost=0.5,
        )
        with self.child.open("a") as stream:
            stream.write(partial)
        partial_summary = self.invoke(
            "ingest",
            "--sessions-root",
            str(self.sessions),
            "--db",
            str(self.db),
        )
        self.assertIn("inserted rows: 0", partial_summary)
        self.assertIn("skipped rows: 1", partial_summary)
        with self.child.open("a") as stream:
            stream.write(
                "\n"
                + self._record(
                    "2026-08-10T01:00:00Z",
                    "new-response",
                    provider="openrouter",
                    model="deepseek",
                    input_tokens=200,
                    output_tokens=100,
                    cache_read=30,
                    cost=3.5,
                )
                + "\n"
            )
        summary = self.invoke(
            "ingest",
            "--sessions-root",
            str(self.sessions),
            "--db",
            str(self.db),
        )
        self.assertIn("inserted rows: 2", summary)
        self.assertIn("skipped rows: 0", summary)
        report = self.report("--by", "agent", "--model", "deepseek")
        self.assertEqual(report["totals"]["requests"], 3)
        self.assertEqual(report["totals"]["total_tokens"], 560)
        self.assertEqual(report["totals"]["cached_tokens"], 90)


if __name__ == "__main__":
    unittest.main()
