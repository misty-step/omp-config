# QA runbook

Every audit runs both tracks. Both return evidence, never opinions. The
deterministic track proves the contracts you already know. The persona track
finds the behavior you did not think to script. Neither substitutes for the
other.

## Track D: deterministic scenarios

One row per scenario in the frozen scenario table:

| Field | Content |
|---|---|
| `id` | stable scenario identifier |
| `entrypoint` | named entrypoint from the discovery inventory |
| `preconditions` | exact state: fixture data, auth, feature flags, seed |
| `steps` | numbered exact user actions |
| `expected` | observable result, stated before execution |
| `evidence` | what to capture: screenshot, snapshot, status, console line |

Execution rules:

- `qa` lanes execute the table with the `verify-live` escalation ladder and
  its evidence discipline. Do not restate that skill; apply it.
- Verdict per row: PASS, WARN, FAIL, or SKIP, with the exact command or
  interaction and the observed result. SKIP names the blocker.
- Deterministic means re-runnable: named preconditions, seeded data, no
  wall-clock or ordering dependence between rows. Reproduce a FAIL before
  recording it.
- Coverage floor per entrypoint: every golden path, every stated invariant,
  and the hostile edges a real user hits — invalid input, empty state, auth
  failure, double submit, refresh mid-flow, back navigation, concurrent
  session.

## Track P: fuzzy persona flows

Browser-only `qa-user-leaf` agents pretend to be users. They receive a
mission and a persona, not a script: they click around, read what the page
shows, pursue a realistic goal, get confused where a real user would, and
report what happened. `skill://qa-users` is the normative contract — frozen
`input.v1`, `local`/`dev`/`staging` environments only, coordinator and leaf
authority boundaries, root triage, fingerprint deduplication, and tracker
ceilings all come from it.

Persona design:

- Give each persona a distinct goal, tolerance, and expertise level — the
  hurried first-timer, the power user with data to lose, the skeptic who
  reads error messages. State the goal, never the steps.
- Personas preserve strengths and friction: what worked well is reported with
  the same rigor as what broke. Friction below the finding threshold stays in
  the report as friction, never discarded.
- A leaf returns exact steps taken, expected versus observed behavior,
  runtime evidence references, strengths, friction, and a `failure_reason`
  when the mission failed.

## Evidence discipline

- Record during exploration, not after. A session interruption must not cost
  a finding.
- Video for an interactive reproduction; one annotated screenshot for a
  static one. Never delete evidence during a session.
- Report artifact paths, never inline heavy payloads.

## Exit criteria

The runbook is complete when every scenario row has a verdict, every persona
returned evidence or a `failure_reason`, and every unexercised surface is a
named SKIP. The assessment step consumes the two track outputs together;
neither track reports directly to the operator.
