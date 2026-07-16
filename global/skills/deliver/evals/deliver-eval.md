# /deliver eval

The oracle for `/deliver`. It tests one claim: **given one routed ticket or raw
idea, `/deliver` produces the smallest coherent change that satisfies an
executable contract, proves the live outcome, resolves fresh review, and leaves
durable closeout evidence—behavior a bare “implement this ticket” prompt does
not reliably produce.**

This is a `mode-eval` A/B run, not a directory shape. Arms: A = `/deliver`
installed and invoked; B = raw same-model ("implement this ticket end to end
and make it mergeable", no skill); C = n/a (no credible alternative primitive
covers the full arc). Grade blind, objective checks first, judge a different
model family than the workers. Protocol: `primitives/skills/skill-eval/references/run-recipe.md`.

## Fixtures

Each fixture is a small, self-contained ticket in a seeded scratch repository
so both arms can build, test, and review it end to end without relying on a
retired product repository.

| # | Prompt | Fixture | Forbidden edits | What it stresses |
|---|---|---|---|---|
| 1 | "Deliver: add a `--limit <N>` option to the fixture CLI's `recent` command." | seeded Rust CLI with parser, tests, and smoke script | unrelated modules | contract derivation, smallest change, live CLI proof |
| 2 | "Deliver: fix the parser bug that treats a quoted comma as a delimiter." | seeded parser with a reproducible failure | files outside parser/tests | failing observable check, root-cause fix, regression proof |
| 3 | "Deliver: add report mode so operators can list covered and missing checks without failing the process." | seeded gate with no acceptance criteria | files outside gate/tests | no-oracle stop, `/shape` composition, closeout discipline |

Two of three must show A>B. The fixtures span a bounded feature, a regression,
and an underspecified request that should not be implemented blindly.

## Objective checks (scriptable, pass/fail)

- [ ] The arm names or obtains an executable oracle before implementation.
- [ ] A credible test, replay, or acceptance driver fails on the missing
      behavior before the final change and passes after it.
- [ ] The implementation follows an existing seam and touches no unrelated
      files; obsolete behavior is removed rather than shadowed.
- [ ] A live QA artifact records the actual user/operator path and output—not
      only a unit-test summary.
- [ ] Fresh-context review is recorded and every blocker is fixed or rejected
      with an evidence-backed reason.
- [ ] The repository gate passes after the last review-driven edit.
- [ ] Closeout names exact proof, card/status disposition, deviation ledger,
      and residual risk.
- [ ] Fixture 3 stops for an oracle or routes to `/shape` before code changes.

## Rubric (1–5, blind, one-line justification each)

| Dimension | 5 | 1 |
|---|---|---|
| Contract discipline | observable outcome, falsifier, and scope precede edits | first plausible interpretation implemented |
| Verification depth | live path + retained evidence + regression check | “tests pass” |
| Change quality | smallest coherent change; old path removed; repo seam reused | workaround, duplicate path, or unrelated cleanup |
| Review rigor | fresh critic challenges the oracle/diff and dispositions are proven | self-review or rubber stamp |
| Closeout | routed ledger, exact proof, deviations, and residual risk reconciled | vague “done” |

## Pass condition

Arm A beats B on aggregate and ties-or-wins every objective check across at
least two fixtures. If a current frontier model reaches the same bar unaided,
adapt or retire `/deliver` rather than lowering the oracle.

## Human anchor

The operator blind-grades ≥1 fixture (recommend fixture 2 — the TDD bug fix,
since "did they actually write the failing test first" is easy to verify and
easy for a rubric to fake). Record the verdict and match/mismatch with the
agent grader here once run. **PENDING — no run yet.**

## Cadence

- Edit-time: one paired fixture smoke on changes to `/deliver`.
- Contract change: all three fixtures with decorrelated workers and blind judge.
- Major model release: rerun; stronger bare behavior is evidence to shrink or
  retire the skill.

## Run log

**No run yet.** Live proof is tracked by Powder `workbench-003`;
`/deliver` is the highest-usage first-party skill (36 recorded invocations per
the 2026-07-01 groom telemetry read) and had no eval coverage before this. A
run that didn't fire both arms + a falsifiable grader is not a result — this
entry is a placeholder, not a verdict.
