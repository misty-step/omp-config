"""Illegal-transition tables for fixed OMP protocols.

These tables document the review-gate and qa-users FSMs. Fail-closed moves
return ``failed``. Integration coverage stays in test_review_gate.py and
qa-users integrity scripts.
"""

from __future__ import annotations

import unittest

# Review gate: see global/references/review-gate-fsm.md
REVIEW_TRANSITIONS: frozenset[tuple[str, str, str]] = frozenset(
    {
        ("idle", "freeze", "frozen"),
        ("frozen", "submit_pass", "passes_partial"),
        ("frozen", "submit_pass", "passes_complete"),
        ("passes_partial", "submit_pass", "passes_partial"),
        ("passes_partial", "submit_pass", "passes_complete"),
        ("passes_complete", "record", "receipted"),
        ("receipted", "verify", "verified"),
        ("idle", "verify", "failed"),
        ("frozen", "verify", "failed"),
        ("passes_partial", "verify", "failed"),
        ("passes_partial", "record", "failed"),
        ("frozen", "submit_forged", "failed"),
        ("receipted", "range_drift", "failed"),
        ("failed", "freeze", "frozen"),
        ("verified", "range_superseded", "idle"),
        ("idle", "record", "failed"),
        ("idle", "submit_pass", "failed"),
        ("frozen", "record", "failed"),
        ("passes_complete", "verify", "failed"),
        ("receipted", "submit_pass", "failed"),
    }
)

REVIEW_ILLEGAL: frozenset[tuple[str, str]] = frozenset(
    {
        ("idle", "verify"),
        ("idle", "record"),
        ("idle", "submit_pass"),
        ("frozen", "verify"),
        ("frozen", "record"),
        ("passes_partial", "verify"),
        ("passes_partial", "record"),
        ("passes_complete", "verify"),
        ("receipted", "submit_pass"),
    }
)


def review_move(state: str, event: str) -> str | None:
    destinations = {dst for src, ev, dst in REVIEW_TRANSITIONS if src == state and ev == event}
    if (state, event) in REVIEW_ILLEGAL:
        return "failed"
    if event == "submit_pass" and destinations <= {"passes_partial", "passes_complete"}:
        return "passes_partial"
    if len(destinations) == 1:
        return next(iter(destinations))
    return None


# qa-users: see global/skills/qa-users/references/fsm.md
QA_TRANSITIONS: frozenset[tuple[str, str, str]] = frozenset(
    {
        ("explore", "mint", "minted"),
        ("minted", "freeze", "frozen"),
        ("frozen", "dry_run_stop", "halt_dry"),
        ("frozen", "dispatch", "dispatching"),
        ("dispatching", "personas_returned", "evidence"),
        ("evidence", "reproduce", "reproducing"),
        ("reproducing", "rca", "rca_optional"),
        ("reproducing", "synthesize", "synthesized"),
        ("rca_optional", "synthesize", "synthesized"),
        ("synthesized", "chief_tracker_write", "chief_write"),
        ("chief_write", "fix_and_pr", "handoff_optional"),
        ("explore", "dispatch", "failed"),
        ("minted", "dispatch", "failed"),
        ("frozen", "production_env", "failed"),
        ("dispatching", "persona_non_browser_tools", "failed"),
        ("evidence", "tracker_write_from_persona", "failed"),
        ("reproducing", "full_persona_on_master", "failed"),
        ("synthesized", "fix_and_pr_before_chief", "failed"),
        ("explore", "rca", "failed"),
        ("minted", "rca", "failed"),
        ("frozen", "rca", "failed"),
        ("explore", "chief_tracker_write", "failed"),
        ("frozen", "chief_tracker_write", "failed"),
        ("dispatching", "chief_tracker_write", "failed"),
        ("evidence", "fix_and_pr", "failed"),
        ("reproducing", "fix_and_pr", "failed"),
    }
)

QA_ILLEGAL: frozenset[tuple[str, str]] = frozenset(
    {
        ("explore", "dispatch"),
        ("minted", "dispatch"),
        ("explore", "chief_tracker_write"),
        ("frozen", "chief_tracker_write"),
        ("dispatching", "chief_tracker_write"),
        ("evidence", "fix_and_pr"),
        ("reproducing", "fix_and_pr"),
        ("explore", "rca"),
        ("minted", "rca"),
        ("frozen", "rca"),
    }
)


def qa_move(state: str, event: str) -> str | None:
    destinations = {dst for src, ev, dst in QA_TRANSITIONS if src == state and ev == event}
    if (state, event) in QA_ILLEGAL:
        return "failed"
    if len(destinations) == 1:
        return next(iter(destinations))
    return None


class ReviewGateFsmTests(unittest.TestCase):
    def test_happy_path(self) -> None:
        state = "idle"
        for event, expected in (
            ("freeze", "frozen"),
            ("submit_pass", "passes_partial"),
        ):
            nxt = review_move(state, event)
            self.assertEqual(nxt, expected, event)
            assert nxt is not None
            state = nxt
        self.assertEqual(review_move("passes_complete", "record"), "receipted")
        self.assertEqual(review_move("receipted", "verify"), "verified")

    def test_illegal_ship_without_receipt(self) -> None:
        for state in ("idle", "frozen", "passes_partial"):
            self.assertEqual(review_move(state, "verify"), "failed", state)

    def test_illegal_record_before_complete(self) -> None:
        self.assertEqual(review_move("frozen", "record"), "failed")
        self.assertEqual(review_move("passes_partial", "record"), "failed")

    def test_every_illegal_pair_fails_closed(self) -> None:
        for state, event in REVIEW_ILLEGAL:
            destinations = {
                dst
                for src, ev, dst in REVIEW_TRANSITIONS
                if src == state and ev == event and dst != "failed"
            }
            self.assertEqual(destinations, set(), f"{state}+{event}")
            self.assertEqual(review_move(state, event), "failed", f"{state}+{event}")


class QaUsersFsmTests(unittest.TestCase):
    def test_happy_path(self) -> None:
        state = "explore"
        path = [
            ("mint", "minted"),
            ("freeze", "frozen"),
            ("dispatch", "dispatching"),
            ("personas_returned", "evidence"),
            ("reproduce", "reproducing"),
            ("synthesize", "synthesized"),
            ("chief_tracker_write", "chief_write"),
        ]
        for event, expected in path:
            nxt = qa_move(state, event)
            self.assertEqual(nxt, expected, event)
            assert nxt is not None
            state = nxt

    def test_no_dispatch_before_freeze(self) -> None:
        self.assertEqual(qa_move("explore", "dispatch"), "failed")
        self.assertEqual(qa_move("minted", "dispatch"), "failed")

    def test_no_tracker_before_packet(self) -> None:
        for state in ("explore", "frozen", "dispatching"):
            self.assertEqual(qa_move(state, "chief_tracker_write"), "failed", state)

    def test_no_rca_before_reproduction(self) -> None:
        for state in ("explore", "minted", "frozen"):
            self.assertEqual(qa_move(state, "rca"), "failed", state)

    def test_dry_run_halts_after_freeze(self) -> None:
        self.assertEqual(qa_move("frozen", "dry_run_stop"), "halt_dry")

    def test_every_illegal_pair_fails_closed(self) -> None:
        for state, event in QA_ILLEGAL:
            destinations = {
                dst
                for src, ev, dst in QA_TRANSITIONS
                if src == state and ev == event and dst != "failed"
            }
            self.assertEqual(destinations, set(), f"{state}+{event}")
            self.assertEqual(qa_move(state, event), "failed", f"{state}+{event}")


if __name__ == "__main__":
    unittest.main()
