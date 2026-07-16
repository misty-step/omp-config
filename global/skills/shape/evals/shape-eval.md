# /shape eval

The oracle for the `/shape` skill. Tests the one claim a shaping skill must
earn: **given a raw idea, `/shape` produces a context packet a cold lane can
build the intended thing from — with a fenced scope, alternatives that fail
differently and a named pick, an executable oracle, real repo anchors, and a
premise source — that bare "flesh out this spec for me" does not.**

This is a `mode-eval` A/B run, not a directory shape. Arms: A = `/shape`
installed and invoked; B = raw same-model ("flesh out this spec into something
buildable", no skill); C = n/a for now (Ponytail is a candidate alternative for
the simplicity-pressure dimension once A>B is established). Grade blind,
objective checks first, judge a different model family than the workers. Live
proof is tracked by Powder `workbench-003` and driven per
`primitives/skills/skill-eval/references/run-recipe.md`.

## Fixtures

Each fixture is spec-only: the arm outputs a context packet and makes no source
changes. Use live Roster state for fixtures 1–2 and a seeded service for 3.

| # | Prompt | Repo/card evidence | Forbidden edits | What it stresses |
|---|---|---|---|---|
| 1 | "Shape a dynamic model/provider catalog for Roster dispatch." | Roster + Powder `roster-model-catalog` | source edits | premise challenge, repo anchors, executable rollout oracle |
| 2 | "Shape one cross-harness tool-grievance surface without adding another standalone CLI." | Roster + Powder `roster-cross-harness-grievance` | source edits | alternatives that fail differently, boundary placement, attribution invariants |
| 3 | "Shape enforcing a refund threshold: refunds above $X require a second approver." | seeded Python billing service | source edits | high-risk money/auth, failure/rollback, premise challenge |

At least two fixtures must show A>B; the set spans product infrastructure,
cross-harness architecture, and high-risk behavior.

## Objective checks (scriptable, pass/fail, ~free — run on every `primitives/skills/shape/**` edit)

Each can fail on a real artifact; a no-op "shape" that echoes the prompt fails
here without a judge.

- [ ] Required packet fields are non-empty: Outcome, Deliverable, Non-Goals,
      Invariants, Repo Anchors, Alternatives, Design, Oracle, Premise Source,
      Risks + Rollout.
- [ ] Oracle contains a runnable command, route, probe, or acceptance artifact—not
      “it should work.”
- [ ] Repo Anchors cite 3–10 live paths and one convention exemplar.
- [ ] Alternatives include at least two options that fail differently and name
      exactly one recommendation.
- [ ] Premise Source is `sha256:<digest> <path-or-url>` or an explicit waiver.
- [ ] Non-trivial fixtures name a reachable HTML plan attached to the Powder
      card, or carry an explicit waiver.
- [ ] No forbidden source edits.
- [ ] Load-bearing choices contain no “preferably” or “decide later.”

## Rubric (1–5, blind, one-line justification each — judgment-heavy delta only)

Every dimension ties to "a stranger can build the intended thing". Drop any a
strong raw arm could win on prose alone.

| Dimension | 5 | 1 |
|---|---|---|
| Premise challenge | names the underlying outcome, reframes the first-draft request | implements the request verbatim |
| Alternatives | ≥2 that fail *differently* (incl. boring/manual) + one killed-on-record pick | one idea in three outfits, or a menu with no pick |
| Architecture depth | surfaces touched, data/control flow, ADR-grade decision | hand-waves the "how it fits" |
| Tooling + verification | names the exact harness, commands, tests, deps the builder runs | "add tests", no command |
| Executability by a stranger | a cold lane builds it with no chat context | needs the author in the room |
| Artifact quality | skeleton discipline; HTML plan uses spatial structure to show sequence/tradeoffs/risk | prose dumped into a browser |

## Pass condition

Arm A beats arm B on aggregate rubric **and** ties-or-wins every objective check,
across **≥2 of 3** fixtures. A no-op shape fails because the raw arm reliably
omits Non-Goals, Alternatives-with-a-pick, an executable Oracle, the Premise
Source, and the HTML plan — the objective checks alone separate them. If A does
*not* clear this on the current default worker model, the result is `adapt` or
`cut` for `/shape`, not a softened bar.

## Cadence

- Edit-time: 1-fixture native-subagent smoke (fixture 1) on any `primitives/skills/shape/**`
  change — free, catches gross regressions.
- Contract change (packet skeleton or a Contract gate moves): full A/B, all 3
  fixtures, decorrelated families.
- Major model release: re-audit. A stronger bare model may close the gap — that
  is the signal to retire or rewrite `/shape`, and the reason this eval exists.

## Run log

Append-only. A run that didn't fire both arms + a falsifiable grader is not a
result.

**2026-06-30 — fixture 1 smoke (native subagents, shared-family waiver).** A =
`/shape`, B = raw, blind grader. Evidence:
`.evidence/harness-evals/shape/2026-06-30/`.

| | Objective checks | Rubric | Verdict |
|---|---|---|---|
| B (raw) | 5/8 (no Alternatives / Premise Source / HTML Plan / Risks) | 24/30 | — |
| A (shape) | 8/8 | **29/30** | **more buildable** |

**Agent-provisional pass on fixture 1:** A beats B on aggregate rubric and
ties-or-wins every objective check. Win is on-claim (scope-lock, alternatives+pick,
premise source, HTML plan). Counter-evidence kept honest: raw won architecture-depth
(5 vs 4) and caught a move/clone gotcha shape missed. Falsifier could have
tied/flipped — it didn't. Limits: n=1 (easiest fixture for raw), shared family.

**Human anchor: PENDING.** This verdict is the agent proxy's; it is not validated
until the operator blind-grades fixture 1 and agrees. Material staged at
`.evidence/harness-evals/shape/2026-06-30/human-judge/`. On disagreement, the
rubric is broken, not the operator.

**Decision: needs-more-tasks** — land the human anchor, then run fixtures 2–3 +
one decorrelated paired run before `keep`.

**2026-06-30 — fixture 2 (runner-vs-protocol decision; native subagents, shared-family waiver).**
A = `/shape`, B = raw, blind grader (read the live crate to check claims).

| | Objective | Rubric | Verdict |
|---|---|---|---|
| B (raw) | sections incomplete (no premise source / HTML plan), prose oracle | 23/30 | — |
| A (shape) | complete, runnable grep/cargo oracle, anchors verified true | **29/30** | **more buildable** |

Agent-provisional A>B again — now **≥2 of 3 fixtures**, so shape clears the pass
direction on the proxy's read. Honest counter: the raw arm was genuinely deep
(crisp 3-layer ownership table; surfaced the more central enforcement seam).
**Human anchor still PENDING** — both fixtures staged for blind judging; dashboard
at `.evidence/harness-evals/shape/2026-06-30/dashboard.html`.

**Bugs this eval surfaced (real, independent of the verdict):**
1. `primitives/skills/shape/SKILL.md` Verification cites `harness-kit-checks premise-source
   validate` / `self-test` — that subcommand does **not exist** in the crate.
   Fix shape's SKILL.md (drop the citation or wire the command).
2. `primitives/skills/skill-eval/references/run-recipe.md` "serious run" via `council.sh`
   **cannot enforce skill-on/off** — `opencode` has no projection root, so the
   most-trusted run has the weakest A/B integrity. Enforced arms must route
   through `dispatch-agent --lane-harness`; fix the run-recipe.
