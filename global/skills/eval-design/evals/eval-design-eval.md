# /eval-design eval

The oracle for the `/eval-design` skill. Tests the one claim an eval-design
skill must earn: **given a request that looks like "add an eval for X" but is
actually a request for instrumentation (a lint, a CI gate, or a dashboard KPI —
no fresh output produced against a task), `/eval-design` runs the demarcation
test, names it as instrumentation-not-an-eval, and either reshapes it into a
real eval or says stop — where a bare "design an eval for X" prompt on the same
model builds the instrumentation and calls it an eval.**

This is a `mode-eval` A/B run, not a directory shape. Arms: A = `/eval-design`
installed and invoked; B = raw same-model ("design an eval for X", no skill).
Grade blind, objective checks first, judge a different model family than the
workers.

## Fixtures

Each fixture is a request the operator might actually type; the seeded trap is
whether fresh output is produced against a task.

| # | Request | What it stresses |
|---|---|---|
| 1 | "Add an eval that fails CI when any prompt file exceeds 2000 tokens." | Instrumentation in costume — a static lint over checked-in files, no fresh output. A must demarcate and reshape or reject; B builds the linter. |
| 2 | "Set up an eval that tracks our support-deflection rate on the dashboard week over week." | Past-metric KPI, not an eval — nothing generated against a task. A must name it a KPI; B wires a dashboard. |
| 3 | "Eval whether the new agent resolves GitHub issues better than the old one." | A genuine capability eval (decision + fresh output + grader). A must NOT reject it — it must design corpus + grader + paired comparison. False-positive control. |

Two of three must show A>B for a pass; fixtures 1–2 are the demarcation catch,
fixture 3 is the false-positive control (rejecting a real eval fails it).

## Objective checks (scriptable, pass/fail, ~free — run on every `primitives/skills/eval-design/**` edit)

- [ ] Fixture 1: output explicitly names the request as instrumentation / a lint
      (not a capability eval) and either reshapes it or says stop.
- [ ] Fixture 2: output explicitly names the request as a KPI / past metric, not
      an eval.
- [ ] Fixture 3: output treats the request as a real eval — names a corpus, a
      grader, and a paired comparison — and does NOT call it instrumentation.
- [ ] For any fixture A designs, the grader climbs no higher than needed and any
      model-judge is flagged for calibration before its rate is quoted.

## Rubric (1–5, blind, one-line justification each — judgment-heavy delta only)

| Dimension | 5 | 1 |
|---|---|---|
| Demarcation accuracy | correctly separates instrumentation (1–2) from a real eval (3) | treats all three the same |
| Reshape quality (fixtures 1–2) | offers the real eval hiding behind the request, or a clean stop | silently builds the instrumentation |
| False-positive control (fixture 3) | designs the eval without mislabeling it | rejects a legitimate eval request |

## Pass condition

Arm A beats arm B on demarcation accuracy across **≥2 of 3** fixtures AND
ties-or-wins fixture 3's false-positive control. A no-op "eval-design" fails
because the raw arm reliably builds the linter (fixture 1) or the dashboard
(fixture 2) and calls it an eval — the operator's canonical failure this skill
exists to prevent.

## Human anchor

The operator blind-grades fixture 1 (the instrumentation-in-costume case — the
one the raw model most confidently gets wrong). Record the verdict and
match/mismatch here once run. **PENDING — no run yet.**

## Cadence

- Edit-time: 1-fixture native-subagent smoke (fixture 1) on any
  `primitives/skills/eval-design/**` change.
- Contract change (the demarcation test or design sequence moves): full A/B, all
  3 fixtures, decorrelated families.
- Major model release: re-audit — a stronger bare model may already refuse to
  call a lint an eval, closing `/eval-design`'s edge.

## Run log

**No run yet.** Spec seeded 2026-07-08 during the skill re-articulation pass;
`/eval-design` had no eval coverage before this. A run that didn't fire both
arms + a falsifiable grader is not a result — this entry is a placeholder, not a
verdict.
