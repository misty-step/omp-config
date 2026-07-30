# /code-review eval

The `/code-review` skill must earn one claim.
Given a diff with at least one seeded, non-obvious defect, it must find the defect and mark it blocking.
The defect can be a stub implementation, an unverified runtime path, or a test that never touches changed code.
The skill must not ship on the author's own say-so.
A bare "review this diff" prompt on the same model must reliably miss the defect.


This is a `mode-eval` A/B run, not a directory shape. Arms: A = `/code-review`
installed and invoked; B = raw same-model ("review this diff for correctness
and readiness to ship", no skill); C = single-reviewer same-model pass (tests
whether the fan-out/decorrelation machinery earns its cost over one careful
look). Grade blind, objective checks first, judge a different model family
than the workers and than the authoring model that produced the diff.

## Fixtures

Each fixture has a known, seeded defect with an answer key for the grader.
This makes the eval falsifiable.
The raw arm can pass a clean-looking diff by saying nothing, so each fixture must contain something concrete to find.


| # | Diff (seeded defect) | Repo @ SHA | Forbidden edits | What it stresses |
|---|---|---|---|---|
| 1 | A new `eval_coverage::check_eval_coverage` whose test suite only exercises the happy path — the diff silently swallows `fs::read_dir` errors on a malformed `evals/` entry instead of surfacing them (seeded regression) | `harness-kit@c6e01b9` | none (review-only) | swallowed error / unverified runtime path detection |
| 2 | A refactor of `skill_invocation_analytics::usage_summary` that looks cleaner but silently double-counts `cost_usd` when both `work_ledger` and `skill_log` rows share a `backlog_ref` (seeded correctness bug, plausible-looking diff) | `harness-kit@c6e01b9` | none (review-only) | plausible-but-wrong: passes existing tests, wrong under a case the tests don't cover |
| 3 | A clean, correct, well-tested diff with no seeded defect (a genuine no-op fixture) | `harness-kit@c6e01b9` | none (review-only) | false-positive control — the arm must NOT invent a blocking finding where none exists |

Fixtures 1–2 must show A catching the seeded defect as blocking for a pass.
Fixture 3 is a control.
An arm that invents findings on a clean diff fails it regardless of fixtures 1–2.


## Objective checks (scriptable, pass/fail, ~free — run on every `global/skills/code-review/**` edit)

- [ ] Fixture 1: review output names the swallowed-error path specifically
      (file:line or function) as a finding, not a vague "add error handling."
- [ ] Fixture 2: review output identifies the double-count scenario or asks a
      question that would surface it (e.g. "what happens when both sources
      share a backlog_ref?") — a generic "looks fine" does not count.
- [ ] Fixture 3: review output contains zero blocking-severity findings.
- [ ] Findings use the canonical ranked severities (blocking / high / medium / low), not a flat list.
- [ ] At least one reviewer/lens is explicitly named as decorrelated from the
      authoring model family (fixtures 1–2 only; single-model monoculture on a
      substantive diff is itself a finding this eval should catch).
- [ ] The review never says "ship it" while a blocking finding remains open.


## Rubric (1–5, blind, one-line justification each — judgment-heavy delta only)

| Dimension | 5 | 1 |
|---|---|---|
| Defect detection | names the seeded defect precisely, with the failure scenario | misses it entirely or uses vague language ("consider edge cases") |
| Severity discipline | blocking/high/medium/low correctly separates seeded bugs from bounded cleanup | flat wall of undifferentiated comments |
| False-positive control (fixture 3) | zero invented findings on the clean diff | invents a "blocking" issue that is not real |
| Scope discipline | stays on the diff, does not wander into unrelated repo critique | reviews the whole repo instead of the change |


## Pass condition

Arm A beats arm B on defect detection across **≥2 of fixtures 1–2**.
Arm A ties-or-beats arm B on fixture 3's false-positive control.
Arm A ties-or-wins every objective check.
A no-op "code-review" fails because the raw arm reliably misses the seeded plausible-but-wrong bug or produces an undifferentiated finding list without severity ranking.
Fixture 2 is designed to survive a single pass.


## Human anchor

The operator blind-grades fixture 2.
This plausible-but-wrong double-count bug is the hardest to catch and easiest for a lenient grader to accept without enough checking.
Record the verdict and match/mismatch here once run.
**PENDING — no run yet.**


## Cadence

- Edit-time: run a 1-fixture native-subagent smoke (fixture 1) on any
  `global/skills/code-review/**` change.
- Contract change (the fan-out topology, severity ranking, or the
  never-ship-on-own-review rule moves): run full A/B, all 3 fixtures, decorrelated
  families, and re-check the false-positive control specifically.
- Major model release: re-audit.
  A stronger bare model may already catch seeded defects without help, which can close `/code-review`'s advantage over single-reviewer arm C first.


## Run log

**No run yet.** Revisit when this skill changes.
`/code-review` is the second-highest-usage first-party skill (33 recorded
invocations per the 2026-07-01 groom telemetry read) and had no eval coverage
before this.
A run that did not run both arms and a falsifiable grader is not a result.
This entry is a placeholder, not a verdict.
