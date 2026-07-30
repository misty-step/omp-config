# /eval-design eval

This oracle tests one claim that `/eval-design` must earn.
The request looks like "add an eval for X" but actually asks for instrumentation:
a lint, a CI gate, or a dashboard KPI with no fresh output against a task.
`/eval-design` runs the demarcation test, names the request
instrumentation-not-an-eval, and reshapes it into a real eval or says stop.
A bare "design an eval for X" prompt on the same model builds the instrumentation
and calls it an eval.

This is a `mode-eval` A/B run, not a directory shape.
Arms: A = `/eval-design` installed and invoked; B = raw same-model
("design an eval for X", no skill).
Grade blind. Run objective checks first.
Use a judge from a different model family than the workers.

## Fixtures

Each fixture gives a request that the operator might type.
The seeded trap asks whether fresh output is produced against a task.

| # | Request | What it stresses |
|---|---|---|
| 1 | "Add an eval that fails CI when any prompt file exceeds 2000 tokens." | Instrumentation in costume — a static lint over checked-in files, no fresh output. A must demarcate and reshape or reject; B builds the linter. |
| 2 | "Set up an eval that tracks our support-deflection rate on the dashboard week over week." | Past-metric KPI, not an eval — nothing generated against a task. A must name it a KPI; B wires a dashboard. |
| 3 | "Eval whether the new agent resolves GitHub issues better than the old one." | A genuine capability eval (decision + fresh output + grader). A must NOT reject it — it must design corpus + grader + paired comparison. False-positive control. |

Two of three fixtures must show A>B for a pass.
Fixtures 1–2 catch demarcation.
Fixture 3 controls false positives; rejecting a real eval fails the test.

## Objective checks (scriptable, pass/fail, ~free — run on every `global/skills/eval-design/**` edit)

- [ ] Fixture 1: The arm A output explicitly names the request as instrumentation
      or a lint, not a capability eval, and reshapes it or says stop.
- [ ] Fixture 2: The arm A output explicitly names the request as a KPI or past
      metric, not an eval.
- [ ] Fixture 3: The arm A output treats the request as a real eval and names a
      corpus, grader, and paired comparison; it does not call it instrumentation.
- [ ] For any fixture A designs, the arm A output makes the grader climb no
      higher than needed and flags each model-judge for calibration before its
      rate is quoted.

## Rubric (1–5, blind, one-line justification each — judgment-heavy delta only)

| Dimension | 5 | 1 |
|---|---|---|
| Demarcation accuracy | correctly separates instrumentation (1–2) from a real eval (3) | treats all three the same |
| Reshape quality (fixtures 1–2) | offers the real eval hiding behind the request, or a clean stop | silently builds the instrumentation |
| False-positive control (fixture 3) | designs the eval without mislabeling it | rejects a legitimate eval request |

## Pass condition

Arm A beats arm B on demarcation accuracy across **≥2 of 3** fixtures AND
ties-or-wins fixture 3's false-positive control.
A no-op "eval-design" fails because the raw arm reliably builds the linter
(fixture 1) or dashboard (fixture 2) and calls it an eval.
This skill exists to prevent that canonical operator failure.

## Human anchor

The operator blind-grades fixture 1, the instrumentation-in-costume case that the
raw model most confidently gets wrong.
Record the verdict and match/mismatch here after the first run.
**PENDING — no run yet.**

## Cadence

- Edit-time: Run a 1-fixture native-subagent smoke for fixture 1 after any
  `global/skills/eval-design/**` change.
- Contract change: Run full A/B on all 3 fixtures with decorrelated families when
  the demarcation test or design sequence changes.
- Major model release: Re-audit. A stronger bare model may refuse to call a lint
  an eval, closing `/eval-design`'s edge.

## Run log

**No run yet.** Spec seeded 2026-07-08 during the skill re-articulation pass.
`/eval-design` had no eval coverage before this.
A run without both arms and a falsifiable grader is not a result.
This entry is a placeholder, not a verdict.
